#!/usr/bin/env python3
r"""Full workflow that converts RetroPath2.0 output to a list of pathways.

Copyright (C) 2017 JL Faulon's research group, INRA

Use of this source code is governed by the MIT license that can be found in the
LICENSE.txt file.

Command line example:
python RP2paths.py all results.csv --outdir pathways
"""

import os
import argparse
import signal
import subprocess
import logging
from rdkit import Chem
from rp2paths.rp2erxn import compute as rp2erxn_compute
from rp2paths.Scope import compute as Scope_compute
from rp2paths.EFMHandler import EFMHandler
from rp2paths.ImgHandler import ImgHandler
from rp2paths.DotHandler import DotHandler
from rp2paths.PathFilter import PathFilter
from rp2paths.enumerate import enumerate_paths


def canonicalize_smiles(smiles: str) -> str:
    """
    Convert a SMILES string to its canonical form using RDKit.

    Parameters:
    - smiles (str): Input SMILES string.

    Returns:
    - str: Canonical SMILES string. Returns None if input is invalid.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None  # Handle invalid SMILES
    return Chem.MolToSmiles(mol, canonical=True)


class NoScopeMatrix(Exception):
    """Raised when no scope matrix was produced"""
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'NoScopeMatrix, {0} '.format(self.message)
        else:
            return 'NoScopeMatrix has been raised'


class GeneralTask(object):
    """Generic class for handling the execution of task."""

    def __init__(self, forward=False, check_args = True, logger=logging.getLogger(__name__)):
        self.forward = forward
        self.logger = logger
        if check_args:
            # If check_args is True, check the arguments
            # Otherwise, do not check them (used in TaskPath)
            self._check_args()

    def _launch_external_program(self, command, baselog, timeout,
                                 use_shell=False):
        """Make a system call to an external program."""
        if hasattr(os,'setsid'): #setsid not present on Windows
            p = subprocess.Popen(command, stdout=subprocess.PIPE,  # nosec
                                 stderr=subprocess.PIPE, shell=use_shell,
                                 preexec_fn=os.setsid)
        else:
            p = subprocess.Popen(command, stdout=subprocess.PIPE,  # nosec
                                 stderr=subprocess.PIPE, shell=use_shell)
        try:
            fout = open(baselog+'.log', 'w')
            ferr = open(baselog+'.err', 'w')
            out, err = p.communicate(timeout=timeout)
            fout.write(' '.join(command) + '\n')
            fout.write(out.decode('UTF-8'))
            ferr.write(err.decode('UTF-8'))
        except (subprocess.TimeoutExpired):
            fout.write(' '.join(command) + '\n')
            print('TIMEOUT:' + ' '.join(command) + '\n')
            ferr.write('TIMEOUT')
            if hasattr(os,'killpg'): #killpg not present on Windows
                os.killpg(p.pid, signal.SIGKILL)
            else:
                from signal import CTRL_C_EVENT
                os.kill(p.pid, CTRL_C_EVENT)

        fout.close()
        ferr.close()

    def _check_args(self):
        """Make some checking on arguments."""
        raise NotImplementedError("baseclass")

    def compute(self, timeout):
        """Make some computation."""
        raise NotImplementedError("baseclass")


class TaskConvert(GeneralTask):
    """Handling the execution of the conversion task."""

    def __init__(self, infile, cmpdfile, reacfile, sinkfile, forward, logger=logging.getLogger(__name__)):
        """Initializing."""
        self.infile = infile
        self.cmpdfile = cmpdfile
        self.reacfile = reacfile
        self.sinkfile = sinkfile
        super(TaskConvert, self).__init__(forward=forward, logger=logger)

    def _check_args(self):
        """Checking that arguments are usable."""
        if not os.path.exists(self.infile):
            raise IOError(self.infile)

    def compute(self, timeout):
        """Process the conversion."""
        rp2erxn_compute(self.infile, self.cmpdfile,
                        self.reacfile, self.sinkfile,
                        self.forward)

    def set_absolute_infile_path(self):
        """Change the path of the infile."""
        self.infile = os.path.abspath(self.infile)


class TaskCofactors(GeneralTask):
    """Handling the execution of the cofactors task."""

    def __init__(self, cmpdfile, reacfile, cofile, logger=logging.getLogger(__name__)):
        """Initialize."""
        self.cmpdfile = cmpdfile
        self.reacfile = reacfile
        self.cofile = cofile
        self.logger = logger
        super(TaskCofactors, self).__init__(logger=logger)

    def _check_args(self):
        """Check the validity of some arguments."""
        for f in [self.reacfile, self.cmpdfile]:
            if not os.path.exists(f):
                raise FileNotFoundError(f)

    @staticmethod
    def read_cofactors(cofile, logger=logging.getLogger(__name__)):
        # Read cofactors from cofile whose the header is:
        # <ID>	<SMILES>	<INCHI>	<INCHIKEY>
        # as a dict with <SMILES> as key and value is a sub-dict like:
        # {<SMILES>: {'id': <ID>, 'inchi': <INCHI>, 'inchikey': <INCHIKEY> }}
        cofactors = {}
        with open(cofile, 'r') as f:
            next(f)  # Skip header line
            for line in f:
                parts = line.strip().split('\t')
                # convert into canonized smiles using rdkit
                if len(parts) >= 2:
                    smiles = canonicalize_smiles(parts[1])
                    cofactors[smiles] = {'id': parts[0], 'inchi': parts[2], 'inchikey': parts[3]}
        logger.debug(f"Read cofactors: {cofactors}")
        return cofactors

    @staticmethod
    def rm_cofactors_in_cmpdfile(cmpdfile, cofactors, logger=logging.getLogger(__name__)):
        """Remove cofactors from the compound file."""
        # In cmpdfile, remove lines that are in cofactors
        # Keep remaining compounds in a dict with id as key and structure as value
        compounds = {}
        logger.debug(f"Removing cofactors from cmpdfile {cmpdfile}")
        with open(cmpdfile, 'r') as f:
            # Keep the header line
            header = f.readline()
            cmpdlines = f.readlines()
        with open(cmpdfile, 'w') as f:
            f.write(header)
            for line in cmpdlines:
                id_struct = line.strip().split('\t')
                smiles = canonicalize_smiles(id_struct[1])
                if smiles not in cofactors:
                    compounds[id_struct[0]] = id_struct[1]
                    logger.debug(f"Keeping compound {id_struct[0]} with structure {id_struct[1]}")
                    f.write(line)
                else:
                    logger.debug(f"Removing cofactor {line.strip()} from cmpdfile {cmpdfile}")
        logger.debug(f"Remaining compounds after removing cofactors: {compounds}")
        return compounds

    @staticmethod
    def dict_from_reacfile(reacfile, logger=logging.getLogger(__name__)):
        reac_dict = {}
        with open(reacfile, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 5:
                    reac_dict[parts[0]] = {
                        'rules': parts[1].split(','),
                        'reactants': [r.split('].')[-1].replace('[','').replace(']','') if '].' in r else r.split('.')[-1].replace('[','').replace(']','') for r in parts[2].split(':')],
                        'products': [p.split('].')[-1].replace('[','').replace(']','') if '].' in p else p.split('.')[-1].replace('[','').replace(']','') for p in parts[4].split(':')]
                    }
        return reac_dict

    @staticmethod
    def clean_reactions(reacdict, compounds, cofactors, logger=logging.getLogger(__name__)):
        """
        Replace compound IDs with structures and remove cofactors from both sides of reactions.
        Also filters out reactions with empty reactant or product lists after removal.

        Args:
            reacdict (dict): Dictionary of reactions with compound IDs.
            compounds (dict): Dictionary mapping compound IDs to structures.
            cofactors (set): Set of cofactor structures to remove.
            logger (Logger): Optional logger.

        Returns:
            dict: Cleaned reactions with structures instead of IDs and no cofactors.
        """
        cleaned = {}
        for reac_id, values in reacdict.items():
            # Map compound IDs to structures and remove cofactors
            reactants = [
                compounds[r] for r in values['reactants']
                if r in compounds and compounds[r] not in cofactors
            ]
            products = [
                compounds[p] for p in values['products']
                if p in compounds and compounds[p] not in cofactors
            ]

            # Keep only reactions with non-empty sides
            if reactants and products:
                cleaned[reac_id] = {
                    'reactants': reactants,
                    'products': products
                }

        logger.debug(f"Reactions after structure mapping and cofactor removal: {cleaned}")
        return cleaned

    @staticmethod
    def parse_reacfile(reacfile):
        """
        Read the raw reaction file into lines.

        Args:
            reacfile (str): Path to the reaction file.

        Returns:
            list: List of lines from the file.
        """
        with open(reacfile, 'r') as f:
            return f.readlines()

    @staticmethod
    def build_reactions_dict(reacfile_lines, reacdict, compounds, logger=logging.getLogger(__name__)):
        """
        Build a structured dictionary from raw reaction file lines and cleaned reacdict.
        Handles merging of rules for duplicate reactions (i.e., same stoichiometry).

        Args:
            reacfile_lines (list): Raw lines from the reaction file.
            reacdict (dict): Cleaned reactions from `clean_reactions`.
            compounds (dict): Valid compounds for checking presence.
            logger (Logger): Optional logger.

        Returns:
            dict: Structured dictionary of filtered and merged reactions.
        """
        reactions = {}

        for line in reacfile_lines:
            parts = line.strip().split('\t')
            if len(parts) < 5:
                continue  # Skip malformed lines

            reac_id = parts[0]
            if reac_id not in reacdict:
                continue  # Skip reactions not in the cleaned reaction dictionary

            # Extract raw reactants and products from line
            raw_reactants = parts[2].split(':')
            raw_products = parts[4].split(':')

            # Filter raw strings based on compound ID existence
            reactants = [
                r for r in raw_reactants
                if r.split('.')[-1].strip('[]') in compounds
            ]
            products = [
                p for p in raw_products
                if p.split('.')[-1].strip('[]') in compounds
            ]

            if not reactants or not products:
                continue  # Skip reactions with any empty side

            # Extract rule identifiers
            rules = set(parts[1].split(','))

            # Use a key that collapses identical reactions with same stoichiometry
            key = (','.join(sorted(reactants)), ','.join(sorted(products)))

            if key in reactions:
                # Merge rule sets for duplicate reactions
                logger.debug(f"Duplicate reaction found: {reactants} -> {products}. Merging rules.")
                reactions[key][1] |= rules
            else:
                # Store new reaction entry
                reactions[key] = [reac_id, rules, reactants, products]

        logger.debug(f"Final reactions dictionary: {reactions}")
        return reactions

    @staticmethod
    def rm_cofactors_in_reacfile(reacfile, cofactors, compounds, logger=logging.getLogger(__name__)):
        """
        High-level wrapper that orchestrates:
          - Reading and parsing the reaction file.
          - Replacing IDs with structures.
          - Removing cofactors.
          - Filtering invalid reactions and merging rules.

        Args:
            reacfile (str): Path to the reaction file.
            cofactors (set): Set of cofactor structures.
            compounds (dict): Dictionary of compound ID -> structure.
            logger (Logger): Optional logger.

        Returns:
            dict: Final filtered and merged reaction dictionary.
        """
        # Parse the reaction file into a dict format with ID references
        reacdict = TaskCofactors.dict_from_reacfile(reacfile, logger)

        # Clean reactions by removing cofactors and replacing IDs with structures
        cleaned_reacdict = TaskCofactors.clean_reactions(reacdict, compounds, cofactors, logger)

        # Read raw lines from the file for rule extraction and duplicate merging
        reacfile_lines = TaskCofactors.parse_reacfile(reacfile)

        # Build final dictionary with merged rules and valid reactions
        final_reactions = TaskCofactors.build_reactions_dict(reacfile_lines, cleaned_reacdict, compounds, logger)

        return final_reactions


    def compute(self, timeout):
        """Process the conversion."""
        # If cofile does not exist, do nothing
        if not os.path.exists(self.cofile):
            self.logger.warning(f"Cofactor file {self.cofile} does not exist.")
            return
        self.logger.info(f"Removing cofactors and overwriting {self.cmpdfile} and {self.reacfile}.")
        cofactors = TaskCofactors.read_cofactors(self.cofile, self.logger)
        # Edit the cmpdfile to remove cofactors
        compounds = TaskCofactors.rm_cofactors_in_cmpdfile(self.cmpdfile, cofactors, self.logger)
        # Edit the reacfile to remove cofactors
        reactions = TaskCofactors.rm_cofactors_in_reacfile(self.reacfile, cofactors, compounds, self.logger)
        print(reactions)
        # Write the filtered reactions back to the reacfile
        with open(self.reacfile, 'w') as f:
            for _, line in reactions.items():
                # Write the line with updated reactants and products
                f.write(f"{line[0]}\t{','.join(line[1])}\t{':'.join(line[2])}\t=\t{':'.join(line[3])}\n")


class TaskScope(GeneralTask):
    """Handling the execution of the scope task."""

    def __init__(self, reacfile, sinkfile, target, minDepth=False,
                 customsinkfile=None, forward=False, logger=logging.getLogger(__name__)):
        """Initialize."""
        self.outdir = '.'
        self.reacfile = reacfile
        self.sinkfile = sinkfile
        self.target = target
        self.minDepth = minDepth
        # Custom sink? If yes, replace sinkfile
        if customsinkfile is not None:
            self.sinkfile = customsinkfile
            self.sinkfile = os.path.abspath(self.sinkfile)
        super(TaskScope, self).__init__(forward=forward, logger=logger)

    def _check_args(self):
        """Check the validity of some arguments."""
        for f in [self.outdir, self.reacfile, self.sinkfile]:
            if not os.path.exists(f):
                raise FileNotFoundError(f)

    def _check_output(self):
        """Check whether the outputted scope is empty."""
        if not os.path.exists('out_mat'):
            raise NoScopeMatrix("*** Scope Task: no scope matrix was produced, exit")

    def compute(self, timeout):
        """Process the conversion."""
        Scope_compute(out_folder=self.outdir, sink_file=self.sinkfile,
                      reaction_file=self.reacfile, target=self.target,
                      minDepth=self.minDepth, forward=self.forward,
                      logger=self.logger)
        self._check_output()


class TaskEfm(GeneralTask):
    """Handling the execution of the efm task."""

    def __init__(self, ebin, basename, max_steps, max_paths, forward=False, logger=logging.getLogger(__name__)):
        """Initialize."""
        self.ebin = ebin
        self.basename = basename
        self.max_steps = max_steps
        self.max_paths = max_paths
        super(TaskEfm, self).__init__(forward=forward, logger=logger)

    def _check_args(self):
        if not os.path.exists(self.ebin):
            raise IOError(self.ebin)

    def compute(self, timeout):
        """Enumerate EFMs."""
        if not os.path.exists(self.basename + '_mat'):
            raise IOError('No stoichiometry matrix found: ' + self.basename + '_mat')

        # command = [self.ebin, self.basename, self.basename]
        elemodes = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'efmtool', 'elemodes.jar'
        )
        def filename(name: str):
            return os.path.join(
                os.getcwd(),
                self.basename+'_'+name
            )
        if not self.forward:
            command = f'java -jar \
                {elemodes} \
                -kind stoichiometry \
                -stoich {filename("mat")} \
                -rev {filename("rever")} \
                -meta {filename("comp")} \
                -reac {filename("react")} \
                -arithmetic double \
                -zero 1e-10  \
                -compression default \
                -log console \
                -level {self.logger.level} \
                -maxthreads -1 \
                -normalize min \
                -adjacency-method pattern-tree-minzero \
                -rowordering MostZerosOrAbsLexMin \
                -out text-boolean {filename("efm")}'

            self._launch_external_program(command=command, baselog='efm',
                                        timeout=timeout, use_shell=True)
        else:
            # Enumerate all longest pathways w/o running EFM
            enumerate_paths(
                mat_file=filename("mat"),
                react_file=filename("react"),
                comp_file=filename("comp"),
                start_cmpd='TARGET_0000000001',
                max_depth=self.max_steps,
                max_paths=self.max_paths,
                output_file=filename("efm"),
                logger=self.logger
            )


class TaskPath(GeneralTask):
    """Handling result generated by the EFM enumeration tool."""

    def __init__(self, basename, outfile,
                 unfold_stoichio=False, unfold_compounds=False,
                 maxsteps=0, logger=logging.getLogger(__name__)):
        """Initialization."""
        self.basename = basename
        self.full_react_file = basename + '_full_react'
        self.react_file = basename + '_react'
        self.efm_file = basename + '_efm'
        self.outfile = outfile
        self.unfold_stoichio = unfold_stoichio
        self.unfold_compounds = unfold_compounds
        self.maxsteps = maxsteps if maxsteps != 0 else float('+inf')
        # Initialize parameters through mother class
        super(TaskPath, self).__init__(check_args=False, logger=logger)

    def _check_args(self):
        """Perform some checking on arguments."""
        assert type(self.unfold_stoichio) is bool
        assert type(self.unfold_compounds) is bool
        assert self.maxsteps > 0
        for filepath in (self.full_react_file, self.react_file, self.efm_file):
            if not os.path.exists(filepath):
                raise IOError(filepath)

    def compute(self, timeout):
        """Generate pathways from EFM enumerations."""
        self._check_args()
        efmh = EFMHandler(
            full_react_file=self.full_react_file,
            react_file=self.react_file,
            efm_file=self.efm_file,
            outfile=self.outfile,
            unfold_stoichio=self.unfold_stoichio,
            unfold_compounds=self.unfold_compounds,
            maxsteps=self.maxsteps,
            logger=self.logger
        )
        efmh.ParseEFMs()
        efmh.WriteCsv()


class TaskFilter(GeneralTask):
    """Filter out unwanted pathways."""

    def __init__(self, pathfile, sinkfile,
                 customsinkfile=None,
                 onlyPathsStartingBy=None,
                 notPathsStartingBy=None,
                 forward=False,
                 logger=logging.getLogger(__name__)):
        """Initialize."""
        self.pathfile = pathfile
        self.sinkfile = sinkfile
        # Custom sink? If yes, replace sinkfile
        if customsinkfile is not None:
            self.sinkfile = customsinkfile
            self.sinkfile = os.path.abspath(self.sinkfile)
        # Only keep paths starting by specified compound(s)?
        self.onlyPathsStartingBy = onlyPathsStartingBy
        # Filter out paths starting by specified compound(s)?
        self.notPathsStartingBy = notPathsStartingBy
        super(TaskFilter, self).__init__(forward=forward, logger=logger)

    def _check_args(self):
        for f in [self.pathfile, self.sinkfile]:
            if not os.path.exists(f):
                raise IOError(f)

    def compute(self, timeout):
        """Filter pathways."""
        pf = PathFilter(
            pathfile=self.pathfile,
            sinkfile=self.sinkfile,
            filter_bootstraps=True,
            filter_inconsistentsubstrates=True,
            onlyPathsStartingBy=self.onlyPathsStartingBy,
            notPathsStartingBy=self.notPathsStartingBy,
            logger=self.logger
        )
        pf.GetPathwaysFromFile()
        pf.GetSinkCompoundsFromFile()
        pf.FilterOutPathways()
        pf.RewritePathFile()


class TaskImg(GeneralTask):
    """Handling computation of pictures."""

    def __init__(self, pathsfile, cmpdfile, imgdir, cmpdnamefile=None, forward=False, logger=logging.getLogger(__name__)):
        """Initialize."""
        self.pathsfile = pathsfile
        self.cmpdfile = cmpdfile
        self.imgdir = imgdir
        self.cmpdnamefile = cmpdnamefile
        super(TaskImg, self).__init__(forward=forward, logger=logger)
        self.tryCairo = True
        self.width = 400
        self.height = 200
        self.kekulize = True

    def _check_args(self):
        if not os.path.isdir(self.imgdir):
            os.mkdir(self.imgdir)
        if not os.path.exists(self.pathsfile):
            raise IOError(self.pathsfile)
        if self.cmpdnamefile is not None:
            if not os.path.exists(self.cmpdnamefile):
                self.cmpdnamefile = None
                print('Warning: --cmpdnamefile is not a valid path, name of compounds will be not available.')

    def compute(self, timeout):
        """Compute pictures."""
        imgh = ImgHandler(
            pathsfile=self.pathsfile,
            cmpdfile=self.cmpdfile,
            imgdir=self.imgdir,
            cmpdnamefile=self.cmpdnamefile,
            width=self.width,
            height=self.height,
            tryCairo=self.tryCairo,
            kekulize=self.kekulize,
            logger=self.logger
        )
        imgh.GetInvolvedCompoundsFromFile()
        imgh.GetSmilesOfCompoundsFromFile()
        imgh.GetCompoundsNameFromFile()
        imgh.MakeAllImg()


class TaskDot(GeneralTask):
    """Generating pathways as dot files."""

    def __init__(self, pathsfile, chassisfile, target, outbasename,
                 imgdir=None, cmpdnamefile=None, customchassisfile=None,
                 forward=False, logger=logging.getLogger(__name__)):
        """Initialization."""
        self.pathsfile = pathsfile
        self.chassisfile = chassisfile
        self.target = target
        self.outbasename = outbasename
        self.imgdir = imgdir
        self.cmpdnamefile = cmpdnamefile
        # Custom sink? If yes, replace chassisfile
        if customchassisfile is not None:
            self.chassisfile = customchassisfile
            self.chassisfile = os.path.abspath(self.chassisfile)
        super(TaskDot, self).__init__(forward=forward, logger=logger)

    def _check_args(self):
        """Perform some checking on arguments."""
        for filepath in (self.pathsfile, self.chassisfile):
            if not os.path.exists(filepath):
                raise IOError(filepath)
        if self.cmpdnamefile is not None:
            if not os.path.exists(self.cmpdnamefile):
                self.cmpdnamefile = None
                print('Warning: --cmpdnamefile is not a valid path, name of compounds will be not available.')

    def compute(self, timeout):
        """Generate all dot files."""
        doth = DotHandler(
            pathsfile=self.pathsfile,
            chassisfile=self.chassisfile,
            target=self.target,
            outbasename=self.outbasename,
            imgdir=self.imgdir,
            cmpdnamefile=self.cmpdnamefile,
            logger=self.logger
        )
        doth.GetPathwaysFromFile()
        doth.GetChassisCompoundsFromFile()
        doth.GetCompoundsNameFromFile()
        doth.MakeAllDot(dot=True, svg=True, png=False)


def launch(tasks, outdir, timeout):
    """Launch the computation of one or several tasks.

    tasks: list, *Task object
    ..
    """
    # Checking output folder
    dir_handler(outdir)
    # Switch the
    base_dir = os.getcwd()
    os.chdir(os.path.join(outdir))
    # Compute each task
    for t in tasks:
        t._check_args()
        t.compute(timeout=timeout)
    # Back to initial folder
    os.chdir(os.path.join(base_dir))


def dir_handler(outdir):
    """Handling paths to the output folder."""
    # Create the out folder if it does not exist
    if not os.path.exists(os.path.join(outdir)):
        os.mkdir(os.path.join(outdir))


def convert(args, logger=logging.getLogger(__name__)):
    """Convert output from RetroPath2.0 workflow."""
    task = TaskConvert(infile=args.infile, cmpdfile=args.cmpdfile,
                       reacfile=args.reacfile, sinkfile=args.sinkfile,
                       forward=args.forward, logger=logger)
    task.set_absolute_infile_path()
    launch(tasks=[task], outdir=args.outdir, timeout=None)


def remove_cofactors(args, logger=logging.getLogger(__name__)):
    """Remove cofactors from the cmpd and reac files."""
    task = TaskCofactors(cmpdfile=args.cmpdfile, reacfile=args.reacfile,
                         cofile=args.cofile, logger=logger)
    task.compute(timeout=None)
    launch(tasks=[task], outdir=args.outdir, timeout=None)


def scope(args, logger=logging.getLogger(__name__)):
    """Compute the scope using new version."""
    task = TaskScope(reacfile=args.reacfile, sinkfile=args.sinkfile,
                     target=args.target, minDepth=args.minDepth,
                     customsinkfile=args.customsinkfile, logger=logger)
    launch(tasks=[task], outdir=args.outdir, timeout=None)


def efm(args, logger=logging.getLogger(__name__)):
    """Enumerate EFMs."""
    task = TaskEfm(ebin=args.ebin, basename=args.basename, max_steps=args.maxsteps, max_paths=args.maxpaths,
                   forward=args.forward, logger=logger)
    launch(tasks=[task], outdir=args.outdir, timeout=args.timeout)


def paths(args, logger=logging.getLogger(__name__)):
    """Compute possible heterologous pathways."""
    task = TaskPath(basename=args.basename, outfile=args.pathsfile,
                    unfold_stoichio=args.unfold_stoichio,
                    unfold_compounds=args.unfold_compounds,
                    maxsteps=args.maxsteps, maxpaths=args.maxpaths,
                    forward=args.forward, logger=logger)
    launch(tasks=[task], outdir=args.outdir, timeout=None)


def filter(args, logger=logging.getLogger(__name__)):
    """Filter out some paths according to some criteria."""
    task = TaskFilter(pathfile=args.pathsfile, sinkfile=args.sinkfile,
                      customsinkfile=args.customsinkfile,
                      onlyPathsStartingBy=args.onlyPathsStartingBy,
                      notPathsStartingBy=args.notPathsStartingBy,
                      forward=args.forward, logger=logger)
    launch(tasks=[task], outdir=args.outdir, timeout=None)


def img(args, logger=logging.getLogger(__name__)):
    """Compute compound and pathway pictures."""
    task = TaskImg(pathsfile=args.pathsfile, cmpdfile=args.cmpdfile,
                   imgdir=args.imgdir, cmpdnamefile=args.cmpdnamefile,
                   forward=args.forward, logger=logger)
    launch(tasks=[task], outdir=args.outdir, timeout=None)


def dot(args, logger=logging.getLogger(__name__)):
    """Compute dot files of pathways."""
    task = TaskDot(pathsfile=args.pathsfile, chassisfile=args.sinkfile,
                   target=args.target, outbasename=args.dotfilebase,
                   imgdir=args.imgdir, cmpdnamefile=args.cmpdnamefile,
                   customchassisfile=args.customsinkfile,
                   forward=args.forward, logger=logger)
    launch(tasks=[task], outdir=args.outdir, timeout=None)


def doall(args, logger=logging.getLogger(__name__)):
    """Compute all the tasks at once."""
    c_task = TaskConvert(
        infile=args.infile, cmpdfile=args.cmpdfile,
        reacfile=args.reacfile, sinkfile=args.sinkfile,
        forward=args.forward, logger=logger)
    c_task.set_absolute_infile_path()
    r_task = TaskCofactors(
        reacfile=args.reacfile, cmpdfile=args.cmpdfile,
        cofile=args.cofile, logger=logger)
    # Extract sinks and reactions, either in retro (default) or forward direction
    s_task = TaskScope(
        reacfile=args.reacfile, sinkfile=args.sinkfile,
        target=args.target, minDepth=args.minDepth,
        customsinkfile=args.customsinkfile,
        forward=args.forward, logger=logger)
    e_task = TaskEfm(
        ebin=args.ebin, basename=args.basename,
        forward=args.forward, max_steps=args.maxsteps, max_paths=args.maxpaths, logger=logger)
    unfold_stoichio = args.unfold_stoichio
    if args.forward:
        unfold_stoichio = False
    p_task = TaskPath(
        basename=args.basename, outfile=args.pathsfile,
        unfold_stoichio=unfold_stoichio,
        unfold_compounds=args.unfold_compounds,
        maxsteps=args.maxsteps, logger=logger)
    f_task = TaskFilter(
        pathfile=args.pathsfile, sinkfile=args.sinkfile,
        customsinkfile=args.customsinkfile,
        onlyPathsStartingBy=args.onlyPathsStartingBy,
        notPathsStartingBy=args.notPathsStartingBy, logger=logger)
    i_task = TaskImg(
        pathsfile=args.pathsfile, cmpdfile=args.cmpdfile,
        imgdir=args.imgdir, cmpdnamefile=args.cmpdnamefile, forward=args.forward, logger=logger)
    d_task = TaskDot(
        pathsfile=args.pathsfile, chassisfile=args.sinkfile,
        target=args.target, outbasename=args.dotfilebase,
        imgdir=args.imgdir, cmpdnamefile=args.cmpdnamefile,
        customchassisfile=args.customsinkfile, forward=args.forward, logger=logger)
    launch(
        tasks=[c_task, r_task, s_task, e_task, p_task, f_task, i_task, d_task],
        outdir=args.outdir, timeout=args.timeout)


def build_args_parser(prog='rp2paths'):

    script_path = os.path.dirname(os.path.realpath(__file__))

    # Args: converting the EMS from RetroPath2.0 Knime workflow
    c_args = argparse.ArgumentParser(prog='rp2paths', add_help=False)
    c_args.add_argument(
        dest='infile',
        help='File outputed by the RetroPath2.0 Knime workflow',
        type=str)
    c_args.add_argument(
        '--outdir', dest='outdir',
        help='Folder to put all results',
        type=str, required=False,
        default=os.getcwd()+'/')
    c_args.add_argument(
        '--forward', '-r', dest='forward',
        help='Consider reactions in the forward direction',
        required=False, action='store_true',
        default=False)

    # Remove cofactors from the cmpd and reac files    
    r_args = argparse.ArgumentParser(prog='rp2paths', add_help=False)
    r_args.add_argument(
        '--reacfile', dest='reacfile',
        help='Path to the reaction file',
        type=str, required=False,
        default=os.path.join(script_path, 'reactions.erxn'))
    r_args.add_argument(
        '--cmpdfile', dest='cmpdfile',
        help='Path to the compound file',
        type=str, required=False,
        default=os.path.join(script_path, 'compounds.tsv'))
    r_args.add_argument(
        '--cofile', dest='cofile',
        help='Path to the cofactor file',
        type=str, required=False,
        default=os.path.join(script_path, 'cofactors.csv'))

    # Args: computing the scope
    s_args = argparse.ArgumentParser(prog='rp2paths', add_help=False)
    s_args.add_argument(
        '--outdir', dest='outdir',
        help='Folder to put all results',
        type=str, required=False,
        default=os.getcwd()+'/')
    s_args.add_argument(
        '--minDepth', action='store_true', default=False,
        help='Use minimal depth scope, i.e. stop the scope computation as \
        as soon an a first minimal path linking target to sink is found \
        (default: False).')
    s_args.add_argument(
        '--target',
        help='Target compound internal ID. This internal ID specifies \
        which compound should be considered as the targeted compound. The \
        default behavior is to consider as the target the first compound \
        used as a source compound in a first iteration of a metabolic \
        exploration. Let this value as it is except if you know what you \
        are doing.',
        type=str, required=False,
        default='TARGET_0000000001')
    s_args.add_argument(
        '--customsinkfile', dest='customsinkfile',
        help='User-defined sink file, i.e. file listing compounds to \
        consider as sink compounds. Sink compounds should be provided by \
        their IDs, as used in the reaction.erxn file. If no file is \
        provided then the sink file generated during the "convert" task \
        is used (default behavior). If a file is provided then **only** \
        compounds listed in this file will be used.',
        type=str, required=False, default=None)

    # Args: enumerating EFMs
    e_args = argparse.ArgumentParser(prog='rp2paths', add_help=False)
    e_args.add_argument(
        '--outdir', dest='outdir',
        help='Folder to put all results',
        type=str, required=False,
        default=os.getcwd()+'/')
    e_args.add_argument(
        '--ebin', dest='ebin',
        help='Path to the binary that enumerate the EFMs',
        type=str, required=False,
        default=os.path.join(script_path, 'efmtool', 'launch_efm.sh'))
    e_args.add_argument(
        '--timeout', dest='timeout',
        help='Timeout before killing a process (in s)',
        type=int, required=False,
        default=900)
    e_args.add_argument(
        '--target',
        help='Target compound internal ID. This internal ID specifies \
        which compound should be considered as the targeted compound. The \
        default behavior is to consider as the target the first compound \
        used as a source compound in a first iteration of a metabolic \
        exploration. Let this value as it is except if you know what you \
        are doing.',
        type=str, required=False,
        default='TARGET_0000000001')

    # Args: computing each possible pathways
    p_args = argparse.ArgumentParser(prog='rp2paths', add_help=False)
    p_args.add_argument(
        '--outdir', dest='outdir',
        help='Folder to put all results',
        type=str, required=False,
        default=os.getcwd()+'/')
    p_args.add_argument(
        '--maxsteps', dest='maxsteps',
        help='Cutoff on the maximum number of steps in a pathways. 0 (default) for \
        unlimited number of steps.',
        type=int, default=0)
    p_args.add_argument(
        '--maxpaths', dest='maxpaths',
        help='cutoff on the maximum number of pathways. 0 (default) for \
        unlimited number of pathways.',
        required=False, type=int, default=0)
    p_args.add_argument(
        '--timeout', dest='timeout',
        help='Timeout before killing a process (in s)',
        type=int, required=False,
        default=900)
    p_args.add_argument(
        '--forward', '-r', dest='forward',
        help='Consider reactions in the forward direction',
        required=False, action='store_true',
        default=False)
    p_args.add_argument(
        '--unfold_compounds', dest='unfold_compounds',
        help='Unfold pathways based on equivalencie of compounds (can lead \
        to combinatorial explosion).',
        default=False, action='store_true')
    p_args.add_argument(
        '--target',
        help='Target compound internal ID. This internal ID specifies \
        which compound should be considered as the targeted compound. The \
        default behavior is to consider as the target the first compound \
        used as a source compound in a first iteration of a metabolic \
        exploration. Let this value as it is except if you know what you \
        are doing.',
        type=str, required=False,
        default='TARGET_0000000001')

    # Args: filtering paths
    f_args = argparse.ArgumentParser(prog='rp2paths', add_help=False)
    f_args.add_argument(
        '--outdir', dest='outdir',
        help='Folder to put all results',
        type=str, required=False,
        default=os.getcwd()+'/')
    f_args.add_argument(
        '--customsinkfile', dest='customsinkfile',
        help='User-defined sink file, i.e. file listing compounds to \
        consider as sink compounds. Sink compounds should be provided by \
        their IDs, as used in the reaction.erxn file. If no file is \
        provided then the sink file generated during the "convert" task \
        is used (default behavior). If a file is provided then **only** \
        compounds listed in this file will be used.',
        type=str, required=False, default=None)
    f_args.add_argument(
        '--onlyPathsStartingBy', dest='onlyPathsStartingBy',
        help='List of compounds IDs to consider. If specified, only paths \
        making use of at least one of these compounds as initial \
        substrate (first step of a pathway) are kept.',
        type=str, nargs='+', required=False, default=None)
    f_args.add_argument(
        '--notPathsStartingBy', dest='notPathsStartingBy',
        help='List of compounds IDs. If specifed, paths making use of \
        one of these compounds as unique initial substrate will be \
        filtered out',
        type=str, nargs='+', required=False, default=None)

    # Args: computing compound pictures
    i_args = argparse.ArgumentParser(prog='rp2paths', add_help=False)
    i_args.add_argument(
        '--outdir', dest='outdir',
        help='Folder to put all results',
        type=str, required=False,
        default=os.getcwd()+'/')
    i_args.add_argument(
        '--timeout', dest='timeout',
        help='Timeout before killing a process (in s)',
        type=int, required=False,
        default=900)
    i_args.add_argument(
        '--cmpdnamefile', dest='cmpdnamefile',
        help='File with name of compounds.',
        type=str, required=False,
        default=os.path.join(script_path, 'mnx-data', 'mnx-compounds-name.tsv'))

    # Args: computing dot files
    d_args = argparse.ArgumentParser(prog='rp2paths', add_help=False)
    d_args.add_argument(
        '--outdir', dest='outdir',
        help='Folder to put all results',
        type=str, required=False,
        default=os.getcwd()+'/')
    d_args.add_argument(
        '--timeout', dest='timeout',
        help='Timeout before killing a process (in s)',
        type=int, required=False,
        default=900)
    d_args.add_argument(
        '--cmpdnamefile', dest='cmpdnamefile',
        help='File with name of compounds.',
        type=str, required=False,
        default=os.path.join(script_path, 'mnx-data', 'mnx-compounds-name.tsv'))
    d_args.add_argument(
        '--customsinkfile', dest='customsinkfile',
        help='User-defined sink file, i.e. file listing compounds to \
        consider as sink compounds. Sink compounds should be provided by \
        their IDs, as used in the reaction.erxn file. If no file is \
        provided then the sink file generated during the "convert" task \
        is used (default behavior). If a file is provided then **only** \
        compounds listed in this file will be used.',
        type=str, required=False, default=None)
    d_args.add_argument(
        '--target',
        help='Target compound internal ID. This internal ID specifies \
        which compound should be considered as the targeted compound. The \
        default behavior is to consider as the target the first compound \
        used as a source compound in a first iteration of a metabolic \
        exploration. Let this value as it is except if you know what you \
        are doing.',
        type=str, required=False,
        default='TARGET_0000000001')

    # Args: computing all tasks in once
    a_args = argparse.ArgumentParser(prog='rp2paths', add_help=False)
    a_args.add_argument(
        dest='infile',
        help='File outputed by the RetroPath2.0 Knime workflow',
        type=str)
    a_args.add_argument(
        '--outdir', dest='outdir',
        help='Folder to put all results',
        type=str, required=False,
        default=os.getcwd()+'/')
    a_args.add_argument(
        '--forward', '-r', dest='forward',
        help='Consider reactions in the forward direction',
        required=False, action='store_true',
        default=False)
    a_args.add_argument(
        '--cofile', dest='cofile',
        help='Path to the cofactor file',
        type=str, required=False,
        default=os.path.join(script_path, 'cofactors.csv'))
    a_args.add_argument(
        '--minDepth', action='store_true', default=False,
        help='Use minimal depth scope, i.e. stop the scope computation as \
        as soon an a first minimal path linking target to sink is found \
        (default: False).')
    a_args.add_argument(
        '--customsinkfile', dest='customsinkfile',
        help='User-defined sink file, i.e. file listing compounds to \
        consider as sink compounds. Sink compounds should be provided by \
        their IDs, as used in the reaction.erxn file. If no file is \
        provided then the sink file generated during the "convert" task \
        is used (default behavior). If a file is provided then **only** \
        compounds listed in this file will be used.',
        type=str, required=False, default=None)
    a_args.add_argument(
        '--ebin', dest='ebin',
        help='Path to the binary that enumerate the EFMs',
        type=str, required=False,
        default=os.path.join(script_path, 'efmtool/launch_efm.sh'))
    a_args.add_argument(
        '--timeout', dest='timeout',
        help='Timeout before killing a process (in s)',
        type=int, required=False,
        default=900)
    a_args.add_argument(
        '--maxsteps', dest='maxsteps',
        help='Cutoff on the maximum number of steps in a pathways. 0 (default) for \
        unlimited number of steps.',
        type=int, default=0)
    a_args.add_argument(
        '--maxpaths', dest='maxpaths',
        help='cutoff on the maximum number of pathways. 0 (default) for \
        unlimited number of pathways.',
        required=False, type=int, default=0)
    a_args.add_argument(
        '--unfold_compounds', dest='unfold_compounds',
        help='Unfold pathways based on equivalencie of compounds (can lead \
        to combinatorial explosion).',
        default=False, action='store_true')
    a_args.add_argument(
        '--onlyPathsStartingBy', dest='onlyPathsStartingBy',
        help='List of compounds IDs to consider. If specified, only paths \
        making use of at least one of these compounds as initial \
        substrate (first step of a pathway) are kept.',
        type=str, nargs='+', required=False, default=None)
    a_args.add_argument(
        '--notPathsStartingBy', dest='notPathsStartingBy',
        help='List of compounds IDs. If specifed, paths making use of \
        one of these compounds as unique initial substrate will be \
        filtered out',
        type=str, nargs='+', required=False, default=None)
    a_args.add_argument(
        '--cmpdnamefile', dest='cmpdnamefile',
        help='File with name of compounds.',
        type=str, required=False,
        default=os.path.join(script_path, 'mnx-data', 'mnx-compounds-name.tsv'))
    a_args.add_argument(
        '--target',
        help='Target compound internal ID. This internal ID specifies \
        which compound should be considered as the targeted compound. The \
        default behavior is to consider as the target the first compound \
        used as a source compound in a first iteration of a metabolic \
        exploration. Let this value as it is except if you know what you \
        are doing.',
        type=str, required=False,
        default='TARGET_0000000001')

    # Master parser
    parser = argparse.ArgumentParser(
        prog='rp2paths',
        description='Full workflow that converts RetroPath2.0 output to a list \
        of pathways')

    subparser = parser.add_subparsers(dest='selected_parser')

    # Subparser: converting
    c_parser = subparser.add_parser(
        'convert',
        help='Format the output of the RetroPath2.0 workflow into a \
        format usable by the stoichiometry code',
        parents=[c_args],
        conflict_handler='resolve',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    c_parser.set_defaults(func=convert)

    # Subparser: removing cofactors
    r_parser = subparser.add_parser(
        'remove_cofactors',
        help='Remove cofactors from the pathways',
        parents=[r_args],
        conflict_handler='resolve',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    r_parser.set_defaults(func=remove_cofactors)

    # Subparser: computing the scope
    s_parser = subparser.add_parser(
        'scope',
        help='Computing the scope leading to a given compounds',
        parents=[s_args],
        conflict_handler='resolve',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    s_parser.set_defaults(func=scope)

    # Subparser: compute EFMs
    e_parser = subparser.add_parser(
        'efm',
        help='Enumerating EFMs according to a computed scope',
        parents=[e_args],
        conflict_handler='resolve',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    e_parser.set_defaults(func=efm)

    # Subparser: computing each possible pathways
    p_parser = subparser.add_parser(
        'paths',
        help='Computing each possible pathways according to a enumerated \
        EFMs',
        parents=[p_args],
        conflict_handler='resolve',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p_parser.set_defaults(func=paths)

    # Subparser: filtering paths
    f_parser = subparser.add_parser(
        'filter',
        help='Filter out unwanted pathways',
        parents=[f_args],
        conflict_handler='resolve',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    f_parser.set_defaults(func=filter)

    # Subparser: producing images
    i_parser = subparser.add_parser(
        'img',
        help='Computing compound pictures',
        parents=[i_args],
        conflict_handler='resolve',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    i_parser.set_defaults(func=img)

    # Subparser: producing images
    d_parser = subparser.add_parser(
        'dot',
        help='Computing dot file of pathways',
        parents=[d_args],
        conflict_handler='resolve',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    d_parser.set_defaults(func=dot)

    # Subparser: do all the tasks
    a_parser = subparser.add_parser(
        'all',
        help='Compute the full workflow',
        parents=[a_args],
        conflict_handler='resolve',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    a_parser.set_defaults(func=doall)

    # Add some other values that the user probably do not take care.
    #   basename: Basename of the file produced by external binaries
    #   reacfile: File containing reaction information
    #   cmpdfile: File containing all compound IDs
    #   sinkfile: File containing sink IDs (subset of all compound IDs)
    #   imgdir: Folder that will contains compound pictures
    #   pathsfile: File that will contains solution pathways
    #   dotfilebase: Basename for dot files
    #   unfold_stoichio: Switch in order to unfold pathways based on the
    #       stoichiometry matrix (can lead to combinatorial explosion).
    #       Setting this option to False will make the process to only
    #       consider the first pathway from amongst all pathways sharing
    #       a same topology. This reduces the combinatorics at the risk of
    #       missing some valid pathways (and even missing ALL valid
    #       pathways) because of the bootstraps filtering, i.e. the
    #       pathway popped out might be invalid while a further with same
    #       same topology could be OK (but will be not outputted if we do
    #       not unfold the topology).
    #       Notice that the unfolding option is only relevant when using
    #       the old scope, as the new scope always unfold.
    #       Considering this, I do recommend to enable unfolding as much as
    #       possible.
    parser.set_defaults(basename='out')
    parser.set_defaults(reacfile='reactions.erxn')
    parser.set_defaults(cmpdfile='compounds.txt')
    parser.set_defaults(sinkfile='sinks.txt')
    parser.set_defaults(imgdir='img')
    parser.set_defaults(pathsfile='out_paths.csv')
    parser.set_defaults(dotfilebase='out_graph')
    parser.set_defaults(unfold_stoichio=True)

    # Add logging
    parser.add_argument(
        '--loglevel', '-l', dest='loglevel',
        help='Set the logging level',
        type=str, required=False, default='ERROR',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])

    return parser
