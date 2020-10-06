"""Handling and generating pathways as dot files.

Copyright (C) 2016-2017 Thomas Duigou, JL Faulon's research group, INRA

Use of this source code is governed by the MIT license that can be found in the
LICENSE.txt file.

"""

import os
import argparse
import csv
from rp2paths.pyEMSv2.reaction import StrReaction
from rp2paths.DotMaker import DotMaker


class DotHandler(object):
    """Handling and generating pathways as dot files."""

    def __init__(self, pathsfile, chassisfile,
                 target=None, outbasename='out_graph',
                 imgdir=None, cmpdnamefile=None):
        """Initialize."""
        self.pathsfile = pathsfile
        self.chassisfile = chassisfile
        self.outbasename = outbasename
        self.target = target
        self.imgdir = imgdir
        self.chassis = set()
        self.pathways = dict()
        self.cmpdnamefile = cmpdnamefile
        self.cmpd_names = dict()

    def _CheckArgs(self):
        """Perform some checking on arguments."""
        if not os.path.exists(self.pathsfile):
            raise IOError(self.pathsfile)
        if not os.path.exists(self.chassisfile):
            raise IOError(self.chassisfile)
        if not os.path.isdir(self.imgdir):
            raise IOError(self.imgdir)

    def GetPathwaysFromFile(self):
        """Get pathways definition from pathsfile."""
        with open(self.pathsfile, 'r') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                pathID = row['Path ID']
                rxnLine = '\t'.join([row['Unique ID'], row['Rule ID'],
                                    row['Left'], '=', row['Right']])
                if pathID not in self.pathways.keys():
                    self.pathways[pathID] = list()
                self.pathways[pathID].append(StrReaction(rxnLine))

    def GetChassisCompoundsFromFile(self):
        """Get list of chassis compounds from chassisfile."""
        with open(self.chassisfile, 'r') as fh:
            reader = csv.reader(fh)
            for row in reader:
                self.chassis.add(row.pop(0))

    def GetCompoundsNameFromFile(self):
        """Get name of known compounds."""
        if self.cmpdnamefile is not None:
            with open(self.cmpdnamefile, 'r') as fh:
                reader = csv.DictReader(fh, delimiter='\t',
                                        quoting=csv.QUOTE_NONE)
                for row in reader:
                    cid = row['Compound ID']
                    cname = row['Name']
                    self.cmpd_names[cid] = cname

    def MakeAllDot(self, dot=True, svg=False, png=False):
        """Generate all dot files."""
        for pid, pathway in sorted(self.pathways.items(), key=lambda x: x[0]):
            dm = DotMaker(pid=pid, pathway=pathway,
                          chassis=self.chassis,
                          target=self.target,
                          imgdir=self.imgdir,
                          cmpd_names=self.cmpd_names)
            dm.MakeDot()
            if dot:
                dotfile = self.outbasename + pid + '.dot'
                dm.WriteDot(dotfile=dotfile)
            if svg:
                svgfile = self.outbasename + pid + '.svg'
                dm.WriteSvg(svgfile=svgfile)
            if png:
                pngfile = self.outbasename + pid + '.png'
                dm.WritePng(pngfile=pngfile)

    def compute(self):
        """Do it."""
        self._CheckArgs()
        self.GetPathwaysFromFile()
        self.GetChassisCompoundsFromFile()
        self.MakeAllDot()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Handling and generating \
                                     pathways as dot files')
    parser.add_argument('--pathsfile', required=True,
                        help='Path to file describing pathways')
    parser.add_argument('--chassisfile', required=True,
                        help='Path to file containing chassis compound IDs.')
    parser.add_argument('--target', required=False, default=None,
                        help='ID of the target compound.')
    # Get arguments
    args = parser.parse_args()

    # Compute
    d = DotHandler(pathsfile=args.pathsfile,
                   chassisfile=args.chassisfile,
                   target=args.target)
    d.compute()
