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
from rp2paths.rp2erxn import compute as rp2erxn_compute
from rp2paths.Scope import compute as Scope_compute
from rp2paths.EFMHandler import EFMHandler
from rp2paths.ImgHandler import ImgHandler
from rp2paths.DotHandler import DotHandler
from rp2paths.PathFilter import PathFilter


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

    def _launch_external_program(self, command, baselog, timeout,
                                 use_shell=False):
        """Make a system call to an external program."""
        p = subprocess.Popen(command, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=False,
                             preexec_fn=os.setsid)
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
            os.killpg(p.pid, signal.SIGKILL)

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

    def __init__(self, infile, cmpdfile, reacfile, sinkfile, reverse):
        """Initializing."""
        self.infile = infile
        self.cmpdfile = cmpdfile
        self.reacfile = reacfile
        self.sinkfile = sinkfile
        self.reverse = reverse
        self._check_args()

    def _check_args(self):
        """Checking that arguments are usable."""
        if not os.path.exists(self.infile):
            raise IOError(self.infile)

    def compute(self, timeout):
        """Process the conversion."""
        rp2erxn_compute(self.infile, self.cmpdfile,
                        self.reacfile, self.sinkfile,
                        self.reverse)

    def set_absolute_infile_path(self):
        """Change the path of the infile."""
        self.infile = os.path.abspath(self.infile)


class TaskScope(GeneralTask):
    """Handling the execution of the scope task."""

    def __init__(self, reacfile, sinkfile, target, minDepth=False,
                 customsinkfile=None):
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
                      minDepth=self.minDepth)
        self._check_output()


class TaskEfm(GeneralTask):
    """Handling the execution of the efm task."""

    def __init__(self, ebin, basename):
        """Initialize."""
        self.ebin = ebin
        self.basename = basename

    def _check_args(self):
        if not os.path.exists(self.ebin):
            raise IOError(self.ebin)

    def compute(self, timeout):
        """Enumerate EFMs."""
        if not os.path.exists(self.basename + '_mat'):
            raise IOError('No stoichiometry matrix found: ' + self.basename + '_mat')

        command = [self.ebin, self.basename, self.basename]
        self._launch_external_program(command=command, baselog='efm',
                                      timeout=timeout, use_shell=True)


class TaskPath(object):
    """Handling result generated by the EFM enumeration tool."""

    def __init__(self, basename, outfile,
                 unfold_stoichio=False, unfold_compounds=False,
                 maxsteps=0, maxpaths=150):
        """Initialization."""
        self.basename = basename
        self.full_react_file = basename + '_full_react'
        self.react_file = basename + '_react'
        self.efm_file = basename + '_efm'
        self.outfile = outfile
        self.unfold_stoichio = unfold_stoichio
        self.unfold_compounds = unfold_compounds
        self.maxsteps = maxsteps if maxsteps != 0 else float('+inf')
        self.maxpaths = maxpaths

    def _check_args(self):
        """Perform some checking on arguments."""
        assert type(self.unfold_stoichio) is bool
        assert type(self.unfold_compounds) is bool
        assert self.maxsteps > 0
        assert type(self.maxpaths) is int and self.maxpaths >= 0
        for filepath in (self.full_react_file, self.react_file, self.efm_file):
            if not os.path.exists(filepath):
                raise IOError(filepath)

    def compute(self, timeout):
        """Generate pathways from EFM enumerations."""
        efmh = EFMHandler(
            full_react_file=self.full_react_file,
            react_file=self.react_file,
            efm_file=self.efm_file,
            outfile=self.outfile,
            unfold_stoichio=self.unfold_stoichio,
            unfold_compounds=self.unfold_compounds,
            maxsteps=self.maxsteps,
            maxpaths=self.maxpaths
        )
        efmh.ParseEFMs()
        efmh.WriteCsv()


class TaskFilter(GeneralTask):
    """Filter out unwanted pathways."""

    def __init__(self, pathfile, sinkfile,
                 customsinkfile=None,
                 onlyPathsStartingBy=None,
                 notPathsStartingBy=None):
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
            notPathsStartingBy=self.notPathsStartingBy
        )
        pf.GetPathwaysFromFile()
        pf.GetSinkCompoundsFromFile()
        pf.FilterOutPathways()
        pf.RewritePathFile()


class TaskImg(GeneralTask):
    """Handling computation of pictures."""

    def __init__(self, pathsfile, cmpdfile, imgdir, cmpdnamefile=None):
        """Initialize."""
        self.pathsfile = pathsfile
        self.cmpdfile = cmpdfile
        self.imgdir = imgdir
        self.cmpdnamefile = cmpdnamefile
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
            kekulize=self.kekulize
        )
        imgh.GetInvolvedCompoundsFromFile()
        imgh.GetSmilesOfCompoundsFromFile()
        imgh.GetCompoundsNameFromFile()
        imgh.MakeAllImg()


class TaskDot(object):
    """Generating pathways as dot files."""

    def __init__(self, pathsfile, chassisfile, target, outbasename,
                 imgdir=None, cmpdnamefile=None, customchassisfile=None):
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
            cmpdnamefile=self.cmpdnamefile)
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


def convert(args):
    """Convert output from RetroPath2.0 workflow."""
    task = TaskConvert(infile=args.infile, cmpdfile=args.cmpdfile,
                       reacfile=args.reacfile, sinkfile=args.sinkfile,
                       reverse=args.reverse)
    task.set_absolute_infile_path()
    launch(tasks=[task], outdir=args.outdir, timeout=None)


def scope(args):
    """Compute the scope using new version."""
    task = TaskScope(reacfile=args.reacfile, sinkfile=args.sinkfile,
                     target=args.target, minDepth=args.minDepth,
                     customsinkfile=args.customsinkfile)
    launch(tasks=[task], outdir=args.outdir, timeout=None)


def efm(args):
    """Enumerate EFMs."""
    task = TaskEfm(ebin=args.ebin, basename=args.basename)
    launch(tasks=[task], outdir=args.outdir, timeout=args.timeout)


def paths(args):
    """Compute possible heterologous pathways."""
    task = TaskPath(basename=args.basename, outfile=args.pathsfile,
                    unfold_stoichio=args.unfold_stoichio,
                    unfold_compounds=args.unfold_compounds,
                    maxsteps=args.maxsteps, maxpaths=args.maxpaths)
    launch(tasks=[task], outdir=args.outdir, timeout=None)


def filter(args):
    """Filter out some paths according to some criteria."""
    task = TaskFilter(pathfile=args.pathsfile, sinkfile=args.sinkfile,
                      customsinkfile=args.customsinkfile,
                      onlyPathsStartingBy=args.onlyPathsStartingBy,
                      notPathsStartingBy=args.notPathsStartingBy)
    launch(tasks=[task], outdir=args.outdir, timeout=None)


def img(args):
    """Compute compound and pathway pictures."""
    task = TaskImg(pathsfile=args.pathsfile, cmpdfile=args.cmpdfile,
                   imgdir=args.imgdir, cmpdnamefile=args.cmpdnamefile)
    launch(tasks=[task], outdir=args.outdir, timeout=None)


def dot(args):
    """Compute dot files of pathways."""
    task = TaskDot(pathsfile=args.pathsfile, chassisfile=args.sinkfile,
                   target=args.target, outbasename=args.dotfilebase,
                   imgdir=args.imgdir, cmpdnamefile=args.cmpdnamefile,
                   customchassisfile=args.customsinkfile)
    launch(tasks=[task], outdir=args.outdir, timeout=None)


def doall(args):
    """Compute all the tasks at once."""
    c_task = TaskConvert(
        infile=args.infile, cmpdfile=args.cmpdfile,
        reacfile=args.reacfile, sinkfile=args.sinkfile,
        reverse=args.reverse)
    c_task.set_absolute_infile_path()
    s_task = TaskScope(
        reacfile=args.reacfile, sinkfile=args.sinkfile,
        target=args.target, minDepth=args.minDepth,
        customsinkfile=args.customsinkfile)
    e_task = TaskEfm(
        ebin=args.ebin, basename=args.basename)
    p_task = TaskPath(
        basename=args.basename, outfile=args.pathsfile,
        unfold_stoichio=args.unfold_stoichio,
        unfold_compounds=args.unfold_compounds,
        maxsteps=args.maxsteps, maxpaths=args.maxpaths)
    f_task = TaskFilter(
        pathfile=args.pathsfile, sinkfile=args.sinkfile,
        customsinkfile=args.customsinkfile,
        onlyPathsStartingBy=args.onlyPathsStartingBy,
        notPathsStartingBy=args.notPathsStartingBy)
    i_task = TaskImg(
        pathsfile=args.pathsfile, cmpdfile=args.cmpdfile,
        imgdir=args.imgdir, cmpdnamefile=args.cmpdnamefile)
    d_task = TaskDot(
        pathsfile=args.pathsfile, chassisfile=args.sinkfile,
        target=args.target, outbasename=args.dotfilebase,
        imgdir=args.imgdir, cmpdnamefile=args.cmpdnamefile,
        customchassisfile=args.customsinkfile)
    launch(
        tasks=[c_task, s_task, e_task, p_task, f_task, i_task, d_task],
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
        '--reverse', '-r', dest='reverse',
        help='Consider reactions in the reverse direction',
        required=False, action='store_false',
        default=True)

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
        default=os.path.join(script_path, 'efmtool/launch_efm.sh'))
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
        help='Cutoff on the maximum number of steps in a pathways. 0 for \
        unlimited number of steps.',
        type=int, default=0)
    p_args.add_argument(
        '--maxpaths', dest='maxpaths',
        help='cutoff on the maximum number of pathways',
        required=False, type=int, default=150)
    p_args.add_argument(
        '--timeout', dest='timeout',
        help='Timeout before killing a process (in s)',
        type=int, required=False,
        default=900)
    p_args.add_argument(
        '--reverse', '-r', dest='reverse',
        help='Consider reactions in the reverse direction',
        required=False, action='store_false',
        default=True)
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
        '--reverse', '-r', dest='reverse',
        help='Consider reactions in the reverse direction',
        required=False, action='store_false',
        default=True)
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
        help='Cutoff on the maximum number of steps in a pathways. 0 for \
        unlimited number of steps.',
        type=int, default=0)
    a_args.add_argument(
        '--maxpaths', dest='maxpaths',
        help='cutoff on the maximum number of pathways',
        required=False, type=int, default=150)
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

    return parser
