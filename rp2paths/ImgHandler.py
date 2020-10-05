"""Class for handling the generation of compound pictures.

Copyright (C) 2016-2017 Thomas Duigou, JL Faulon's research group, INRA

Use of this source code is governed by the MIT license that can be found in the
LICENSE.txt file.

"""

import os
import argparse
import csv
from rp2paths.pyEMSv2.reaction import StrReaction
from rp2paths.ImgMaker import ImgMaker


class ImgHandler(object):
    """Handling computation of pictures."""

    def __init__(self, pathsfile, cmpdfile, imgdir,
                 cmpdnamefile=None,
                 width=400, height=200,
                 tryCairo=True, kekulize=True):
        """Initialize."""
        self.pathsfile = pathsfile
        self.cmpdfile = cmpdfile
        self.imgdir = imgdir
        self.cmpdnamefile = cmpdnamefile
        self.tryCairo = tryCairo
        self.width = width
        self.height = height
        self.kekulize = kekulize
        self.cmpd_involved = set()
        self.cmpd_smiles = dict()  # Cmpd ID, SMILES
        self.cmpd_names = dict()  # Cmpd ID, name

    def _CheckArgs(self):
        if not os.path.isdir(self.imgdir):
            os.mkdir(self.imgdir)
        for filepath in [self.pathsfile, self.cmpdfile]:
            if not os.path.exists(filepath):
                raise IOError(filepath)

    def GetInvolvedCompoundsFromFile(self):
        """Get invovled compounds from pathsfile."""
        compounds = set()
        # Parse the pathway file for extracting involved compounds
        with open(self.pathsfile, 'r') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                rxnLine = '\t'.join([row['Unique ID'], row['Rule ID'],
                                    row['Left'], '=', row['Right']])
                rxn = StrReaction(rxnLine)
                compounds |= rxn.involved_compounds()
        self.cmpd_involved = compounds

    def GetSmilesOfCompoundsFromFile(self):
        """Extract SMILES of compounds from cmpdfile."""
        with open(self.cmpdfile, 'r') as fh:
            reader = csv.DictReader(fh, delimiter='\t', quoting=csv.QUOTE_NONE)
            for row in reader:
                cid = row['Compound ID']
                if cid in self.cmpd_involved:
                    smiles = row['Structure']
                    self.cmpd_smiles.update({cid: smiles})

    def GetCompoundsNameFromFile(self):
        """Get name of known compounds."""
        if self.cmpdnamefile is not None:
            with open(self.cmpdnamefile, 'r') as fh:
                reader = csv.DictReader(fh, delimiter='\t',
                                        quoting=csv.QUOTE_NONE)
                for row in reader:
                    cid = row['Compound ID']
                    if cid in self.cmpd_involved:
                        cname = row['Name']
                        self.cmpd_names.update({cid: cname})

    def MakeAllImg(self):
        """Generate all the picture of compounds."""
        for cid, smiles in self.cmpd_smiles.items():
            svgfile = os.path.join(self.imgdir, cid + '.svg')
            cname = self.cmpd_names.get(cid, cid)
            im = ImgMaker(smiles=smiles, svgfile=svgfile, legend=cname,
                          width=self.width, height=self.height,
                          tryCairo=self.tryCairo, kekulize=self.kekulize)
            im.MakeSvg()

    def compute(self):
        """Compute pictures."""
        self._CheckArgs()
        self.GetInvolvedCompoundsFromFile()
        self.GetSmilesOfCompoundsFromFile()
        self.GetCompoundsNameFromFile()
        self.MakeAllImg()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Handling the generation \
                                     of compound pictures')
    parser.add_argument('--pathsfile', required=True,
                        help='Path to file describing pathways')
    parser.add_argument('--cmpdfile', required=True,
                        help='Path to file containing SMILES compounds.')
    parser.add_argument('--imgdir', required=False, default='img',
                        help='Output folder that will contains compound \
                        pictures.')
    # Get arguments
    args = parser.parse_args()

    # Compute
    i = ImgHandler(pathsfile=args.pathsfile,
                   cmpdfile=args.cmpdfile,
                   imgdir=args.imgdir)
    i.compute()
