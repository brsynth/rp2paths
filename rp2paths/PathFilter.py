"""Class for filtering pathways based on several criteria.

Copyright (C) 2016-2017 Thomas Duigou, JL Faulon's research group, INRA

Use of this source code is governed by the MIT license that can be found in the
LICENSE.txt file.

"""

import os
import csv
from rp2paths.pyEMSv2.reaction import StrReaction


class PathFilter(object):
    """Class for filtering pathways based on several criteria."""

    def __init__(self, pathfile, sinkfile,
                 filter_bootstraps=True,
                 filter_inconsistentsubstrates=True,
                 onlyPathsStartingBy=None,
                 notPathsStartingBy=None):
        """Initialize."""
        self.pathfile = pathfile
        self.sinkfile = sinkfile
        self.pathways = dict()
        self.sinks = set()
        # Filter flags
        self.filter_bootstraps = filter_bootstraps
        self.filter_inconsistentsubstrates = filter_inconsistentsubstrates
        self.onlyPathsStartingBy = onlyPathsStartingBy
        self.notPathsStartingBy = notPathsStartingBy

    def _CheckArgs(self):
        if not os.path.exists(self.pathfile):
            raise IOError(self.pathfile)

    def GetPathwaysFromFile(self):
        """Get pathways definition from pathsfile."""
        with open(self.pathfile, 'r') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                pathID = row['Path ID']
                rxnLine = '\t'.join([row['Unique ID'], row['Rule ID'],
                                    row['Left'], '=', row['Right']])
                if pathID not in self.pathways.keys():
                    self.pathways[pathID] = list()
                self.pathways[pathID].append(StrReaction(rxnLine))

    def GetSinkCompoundsFromFile(self):
        """Get list of chassis compounds from sinkfile."""
        with open(self.sinkfile, 'r') as fh:
            reader = csv.reader(fh)
            for row in reader:
                self.sinks.add(row.pop(0))

    @staticmethod
    def HasBootstrapReaction(path, sinks):
        """Test wether a pathway contains bootstrap reactions."""
        for r in path:
            boots = set(r.involved_substrates()) & set(r.involved_products())
            if any(boots - sinks):
                return True
        return False

    @staticmethod
    def HasInconsistentSubstrates(path, sinks):
        """Test wether initial substrates are all amongst sink compounds."""
        all_substrates = set()
        all_products = set()
        for r in path:
            all_substrates |= set(r.involved_substrates())
            all_products |= set(r.involved_products())
        init_substrates = all_substrates - all_products
        if any([s not in sinks for s in init_substrates]):
            return True
        return False

    @staticmethod
    def HasSubstratesInFirstStep(path, sinks, subIDs):
        """Test whether specific substrates are used as initial substrates.

        Test whether specific substrates are used as initial substrates, i.e.
        substrate used in first step of pathway.

        sinks: list of string, compounds to consider as sinks compounds
        subIDs: list of string, compound IDs to test
        """
        start_substrates = set()
        for r in path:
            substrates = set(r.involved_substrates())
            # If all substrates are in Sink then this reaction is involved at
            #   the beginning of the pathway
            if all(s in sinks for s in substrates):
                start_substrates |= substrates
        if any([s in subIDs for s in start_substrates]):
            return True
        return False

    @staticmethod
    def HasSingleSubstrate(path, sinks, subIDs):
        """Test whether any subIDs compounds are used as unique substrate."""
        for r in path:
            substrates = set(r.involved_substrates())
            if (
                len(substrates) == 1
                and any([s in subIDs for s in substrates])
            ):
                return True
        return False

    def FilterOutPathways(self):
        """Keep only pathway passing all the filters, delete the others."""
        pids_to_rm = set()
        # Find pathways to delete
        for pid, path in self.pathways.items():
            if (
                self.filter_bootstraps
                and PathFilter.HasBootstrapReaction(path, self.sinks)
            ):
                print("PathFilter: filtering out one pathway",
                      "(has bootstrap reaction)")
                pids_to_rm.add(pid)
            elif (
                self.filter_inconsistentsubstrates
                and PathFilter.HasInconsistentSubstrates(path, self.sinks)
            ):
                print("PathFilter: filtering out one pathway",
                      "(has inconsistent initial substrates)")
                pids_to_rm.add(pid)
            elif (
                self.onlyPathsStartingBy is not None
                and not PathFilter.HasSubstratesInFirstStep(path, self.sinks, self.onlyPathsStartingBy)
            ):
                print("PathFilter: filtering out one pathway",
                      "(does not use any wanted substrate in first step)")
                pids_to_rm.add(pid)
            elif (
                self.notPathsStartingBy is not None
                and PathFilter.HasSubstratesInFirstStep(path, self.sinks, self.notPathsStartingBy)
                and PathFilter.HasSingleSubstrate(path, self.sinks, self.notPathsStartingBy)
            ):
                print("PathFilter: filtering out one pathway",
                      "(use an unwanted single substrate in first step)")
                pids_to_rm.add(pid)
        # Delete unwanted pathways
        for pid in pids_to_rm:
            del self.pathways[pid]

    def RewritePathFile(self):
        """Rewrite the pathsfile.

        Rewrite the pathfile so that it will contain only kept pathways.
        Notice that pathway IDs are also regenerated.
        """
        # Prepare output file
        fields = ['Path ID', 'Unique ID', 'Rule ID', 'Left', 'Right']
        fh = open(self.pathfile, 'w')
        writer = csv.DictWriter(fh, fieldnames=fields, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        # Write with new piud
        new_pid = 0
        for pid, path in sorted(self.pathways.items(),
                                key=lambda x: int(x[0])):
            new_pid += 1
            for rxn in path:
                writer.writerow(
                    {'Path ID': new_pid,
                     'Unique ID': rxn.name,
                     'Rule ID': rxn.enzyme,
                     'Left': ':'.join([str(c) for c in rxn.subs]),
                     'Right': ':'.join([str(c) for c in rxn.prods])
                     })

    def compute(self):
        """Apply filters."""
        self._CheckArgs()
        self.GetPathwaysFromFile()
        self.GetSinkCompoundsFromFile()
        self.FilterOutPathways()
        self.RewritePathFile()


if __name__ == '__main__':

    pf = PathFilter(pathfile='test3/out_paths.csv', sinkfile='test3/sinks.txt',
                    filter_bootstraps=True, filter_inconsistentsubstrates=True)
    pf.compute()
