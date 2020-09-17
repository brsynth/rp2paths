"""Class used to manipulate Elementary Flux Modes.

Copyright (C) 2016-2017 Thomas Duigou, JL Faulon's research group, INRA

Use of this source code is governed by the MIT license that can be found in the
LICENSE.txt file.

"""

from itertools import product
from rp2paths.pyEMSv2.reaction import EquivReaction


class Elemodes:
    """Class representing EFMs."""

    def __init__(self, react_name_file, full_react_file, efm_file, maxsteps):
        """Initialization from file.

        react_name_file, efm_file: file produced by the efm tool.
        """
        self.react_names = Elemodes._ReadReactNamesFromFile(react_name_file)
        self.erxns = Elemodes._GetFullReactionsFromFile(full_react_file)
        self.efms = Elemodes._ReadEfmFromFile(efm_file, self.react_names)

        pathways = list()
        for efm in self.efms:
            if len(efm) > maxsteps:  # Skip EFMs that are too long
                continue
            path = list()
            for step in efm:
                path.append(self.erxns[rxn] for rxn in step)
            pathways.append(path)  # path: list of generators of EquivReactions
        self.efms = sorted(pathways, key=lambda x: len(x))

    @staticmethod
    def _ReadReactNamesFromFile(filepath):
        """Read the ID of the reactions present in the _react file."""
        with open(filepath, 'r') as fh:
            lines = fh.readlines()
        assert len(lines) == 1  # Everything should be on one line
        res = []
        names = lines[0].rstrip().split()
        for i in range(len(names) - 1):
            res.append(sorted(names[i].strip('"').split(',')))
        res.append([names[-1].strip('"')])  # PC: Don't unfold target's name
        return res

    @staticmethod
    def _GetFullReactionsFromFile(full_react_file):
        """Get the list of involved reactions."""
        with open(full_react_file, 'r') as fh:
            tmpr = EquivReaction.from_file(fh)
        erxns = dict()
        for r in tmpr:
            erxns[r.name] = r
        return erxns

    @staticmethod
    def _ReadEfmFromFile(filepath, react_names):
        efms = []
        with open(filepath, 'r') as fh:
            for line in fh:
                line = line.strip()
                if line[-1] == '1':  # Discard pathways not producing target
                    path = []
                    for i in range(len(line) - 1):
                        if line[i] == '1':
                            path.append(react_names[i])
                    efms.append(path)
        return efms

    def UnfoldedPathways(self):
        """Generator that returns all unfolded pathways."""
        for efm in self.efms:
            for path in product(*efm):
                yield path

    def StoichioPathways(self):
        """Generator that returns the unique "stoichiometric" pathways.

        A "stoichiometric pathway" is a unique path from the stiochiometric
        matrix point of view. A given stoichiometric pathway might corresponds
        to several possible combinaison of reactions. In such a case then only
        the first combinaison is kept.

        Use the UnfoldPathways method in order to get all the combinaison
        instead.
        """
        for efm in self.efms:
            yield tuple(next(x) for x in efm)

    def UnfoldCompounds(self, pathway):
        """Generator that returns all possible path by unfolding compounds."""
        steps = (erxn.unfold() for erxn in pathway)
        for path in product(*steps):
            yield path

    def SampleCompounds(self, pathway):
        """Generator that returns a possible path.

        Generator that returns a possible path by taking the first possible
        compound of each reaction.
        """
        yield tuple(erxn.unfold()[0] for erxn in pathway)

    def GetPathways(self, unfold_stoichio=False, unfold_compounds=False,
                    maxsteps=15):
        """Generator that returns pathways from enumeration.

        Generator that returns pathways from enumeration results. If specified,
        pathways are unfolded according to (i) stoichiometric matrix and/or
        (ii) equivalent compounds.
        """
        # Get a generator of pathways (compounds are still folded)
        if unfold_stoichio:
            gpathways = self.UnfoldedPathways()
        else:
            gpathways = self.StoichioPathways()
        # Now for each possible pathway, get a generator with unfolded cmpds
        for pathway in gpathways:
            if unfold_compounds:
                gpath = self.UnfoldCompounds(pathway)
            else:
                gpath = self.SampleCompounds(pathway)
            # Finally write each "totally unfolded" pathway
            for path in gpath:
                # Skip pathways that are too long
                if len(path) > maxsteps:
                    continue
                yield path
