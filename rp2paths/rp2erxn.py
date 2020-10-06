"""Convert output of the RetroPath2.0 workflow.

Copyright (C) 2016-2017 Thomas Duigou, JL Faulon's research group, INRA

Use of this source code is governed by the MIT license that can be found in the
LICENSE.txt file.

"""

import sys
import csv
import argparse
from rdkit import Chem
from rp2paths.IDsHandler import IDsHandler


class Compound(object):
    """Class handling info on compounds.

    The key information is the SMILES representation of the compound,
    i.e. the SMILES should be used in order to distinct compounds.
    """

    # Class attribute that handle the IDs of compounds
    ids_handler = IDsHandler(length=10, prefix='CMPD')

    def __init__(self, smiles):
        """Initialization."""
        self.cids = list()
        self.uid = self.ids_handler.MakeNewID()
        self.smiles = smiles
        # self.smiles = Compound._Compute_Smiles(smiles)
        # self.inchi = Compound._Compute_InChI(smiles)
        self.is_sink = False

    @staticmethod
    def _Compute_InChI(smiles):
        return Chem.MolToInchi(Chem.MolFromSmiles(smiles))

    @staticmethod
    def _Compute_Smiles(smiles):
        return Chem.MolToSmiles(Chem.MolFromSmiles(smiles))

    def SetIsSink(self, is_sink):
        """Set wether a compound is a sink or not."""
        assert type(is_sink) == bool
        self.is_sink = is_sink

    def IsSink(self):
        """Return wether or not the compound should be consider as a sink."""
        return self.is_sink

    def AddCid(self, cid):
        """Add a compound ID."""
        if cid not in self.cids:
            # Remove unwanted characters from compound ID
            cid = cid.replace(",", "_")
            cid = cid.replace(":", "_")
            cid = cid.replace(" ", "_")
            cid = cid.replace("[", "_")
            cid = cid.replace("]", "_")
            self.cids.append(cid)

    def GetCids(self):
        """Return a set of (equivalent) compound ID(s).

        If the real compound ID is not known, then the uniq internal
        ID is returned.
        """
        if len(self.cids) != 0:
            return self.SortCids(self.cids)  # This is a list
        return [self.uid]

    @staticmethod
    def SortCids(cids):
        """Sort the compound IDs.

        A special case is handle if the compound IDs are all coming from
        MetaNetX ("MNXM" prefix).
        """
        # Check wether all IDs are coming from MetaNetX (MNXM prefix)
        mnx_case = True
        for cid in cids:
            if not cid.startswith('MNXM'):
                mnx_case = False
                break
        # Sort IDs
        if mnx_case:
            return sorted(cids, key=lambda x: int(x[4:]))
        else:
            return sorted(cids)

    def GetSmiles(self):
        """Return the SMILES."""
        return self.smiles

    def SetUid(self, new_uid):
        """Change the value of the unique ID."""
        self.uid = new_uid


class Transformation(object):
    """Handle information on a given transformation."""

    # This class attribute will (i) contains all the compounds object
    #   and (ii) will be shared between all the instance objects of the class
    all_compounds = dict()

    @classmethod
    def SetAllCompounds(cls, compounds):
        """Set the list used compounds.

        compounds: a dict of Compounds object (key: smiles str)
        """
        cls.all_compounds = compounds

    @classmethod
    def CmpdToStr(cls, smiles, coeff):
        """Return a string representation of a compound in a reaction."""
        cids = cls.all_compounds[smiles].GetCids()
        return str(coeff) + '.[' + ','.join(cids) + ']'

    @staticmethod
    def _ParseReactionSide(side):
        # Get list of smiles
        csmiles = side.split('.')
        # Look for number of occurence
        res = dict()
        for smi in csmiles:
            if smi not in res.keys():
                res[smi] = 0
            res[smi] += 1
        return res

    @staticmethod
    def __CanonizeReactionSMILES(rxn_smiles):
        """Canonize a SMILES reaction."""
        left, right = rxn_smiles.split('>>')
        lsmiles = left.split('.')
        rsmiles = right.split('.')
        return '.'.join(sorted(lsmiles)) + '>>' + '.'.join(sorted(rsmiles))

    def __init__(self, row):
        """Initialization."""
        self.trs_id = row['Transformation ID']
        self.rxn_smiles = Transformation.__CanonizeReactionSMILES(row['Reaction SMILES'])
        # Get involved compounds
        left_side, right_side = self.rxn_smiles.split('>>')
        self.left = Transformation._ParseReactionSide(left_side)
        self.right = Transformation._ParseReactionSide(right_side)
        # ..
        self.diameter = row['Iteration']
        self.rule_ids = row['Rule ID'].lstrip('[').rstrip(']').split(', ')
        self.ec_numbers = row['EC number'].lstrip('[').rstrip(']').split(', ')
        self.score = row['Score']
        self.iteration = row['Iteration']

    def ToStr(self, reverse=False):
        """Printing."""
        # Prepare left & right
        left_side = ':'.join(sorted([Transformation.CmpdToStr(smi, coeff) for smi, coeff in self.left.items()]))
        right_side = ':'.join(sorted([Transformation.CmpdToStr(smi, coeff) for smi, coeff in self.right.items()]))
        # ..
        ls = list()
        if not reverse:
            ls += [self.trs_id]  # Transformation ID
            ls += [','.join(sorted(list(set(self.rule_ids))))]  # Rule IDs
            ls += [left_side]
            ls += ['=']
            ls += [right_side]
        else:
            ls += [self.trs_id]  # Transformation ID
            ls += [','.join(sorted(list(set(self.rule_ids))))]  # Rule IDs
            ls += [right_side]
            ls += ['=']
            ls += [left_side]
        return '\t'.join(ls)


def compute(infile, cmpdfile='compounds.txt', rxnfile='reactions.txt',
            sinkfile='sinks.txt', reverse=False):
    """Convert the output from the RetroPath2.0 workflow."""
    # Get content
    content = dict()
    with open(infile, 'r') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            # Skip if we are in a "header"
            if row['Initial source'] == 'Initial source':
                continue
            # Regroup by transformation ID
            tid = row['Transformation ID']
            if tid not in content.keys():
                content[tid] = [row]
            else:
                content[tid].append(row)

    # 1) Check consistency and 2) Populate compounds
    all_cmpds = dict()
    for tid in sorted(content.keys()):  # Order determine CMPD IDs
        first = True
        for row in content[tid]:
            # ..
            if first:
                first = False
                # Parse the Reaction SMILES
                tmp = row['Reaction SMILES'].split('>>')
                subs_from_rxn = set(tmp[0].split('.'))
                prods_from_rxn = set(tmp[1].split('.'))
                # Prep for parsing Substrate and Product columns
                subs_from_cmpd = set()
                prods_from_cmpd = set()
            # Accumulate compounds from Substrate and Product columns
            subs_from_cmpd.add(row['Substrate SMILES'])
            prods_from_cmpd.add(row['Product SMILES'])
        # Double check that each SMILES substrate/product is also present
        #   in the description of the reaction
        try:
            assert subs_from_rxn == subs_from_cmpd
        except AssertionError:
            print('Assertion error: differences in substrates')
            print(tid)
            print(subs_from_rxn, subs_from_cmpd)
            sys.exit(0)
        try:
            assert prods_from_rxn == prods_from_cmpd
        except BaseException:
            print('Assertion error: differences in products')
            print(tid)
            print(prods_from_rxn, prods_from_cmpd)
            sys.exit(0)
        # Populate
        for smi in sorted(list(subs_from_rxn | prods_from_rxn)):
            if smi not in all_cmpds.keys():
                cmpd = Compound(smi)
                all_cmpds[smi] = cmpd

    # Populate transformations
    all_trs = dict()
    for tid in content.keys():
        first = True
        for row in content[tid]:
            if first:
                first = False
                trs = Transformation(row)
        all_trs[tid] = trs

    # Update Sink information
    for tid in content.keys():
        for row in content[tid]:
            if row['In Sink'] == '1':
                cids = row['Sink name'].lstrip('[').rstrip(']').split(', ')
                smi = row['Product SMILES']
                for cid in cids:
                    all_cmpds[smi].AddCid(cid)
                all_cmpds[smi].SetIsSink(True)

    # Make accessible compounds information from Transformation objects
    Transformation.SetAllCompounds(compounds=all_cmpds)

    # Retrieve target compounds (substrate appearing in first iteration)
    #   then set a specific compound IDs
    target_ids_handler = IDsHandler(length=10, prefix='TARGET')
    target_visited = set()
    for tid, trs in all_trs.items():
        if trs.iteration == '0':
            for target_smi in trs.left.keys():
                if target_smi not in target_visited:
                    target_visited.add(target_smi)
                    new_uid = target_ids_handler.MakeNewID()
                    all_cmpds[target_smi].SetUid(new_uid)

    # Write the compounds file
    with open(cmpdfile, 'w') as fh:
        header = ['Compound ID', 'Structure']
        writer = csv.DictWriter(fh, fieldnames=header,
                                delimiter='\t', quoting=csv.QUOTE_NONE)
        writer.writeheader()
        for cmpd in sorted(all_cmpds.values(), key=lambda x: x.GetCids()):
            for cid in cmpd.GetCids():
                towrite = {'Compound ID': cid,
                           'Structure': cmpd.GetSmiles()}
                writer.writerow(towrite)
                # fh.write(cid + '\t' + cmpd.GetSmiles() + '\n')

    # Write the sink file
    with open(sinkfile, 'w') as fh:
        for cmpd in sorted(all_cmpds.values(), key=lambda x: x.GetCids()):
            if cmpd.IsSink():
                for cid in cmpd.GetCids():
                    fh.write(cid + '\n')

    # Write the reactions file
    with open(rxnfile, 'w') as fh:
        for trs in sorted(all_trs.values(), key=lambda x: x.trs_id):
            fh.write(trs.ToStr(reverse=reverse) + '\n')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Format the output of the RetroPath2.0 workflow into \
        a format usable by the stoichiometry code.')
    parser.add_argument(
        '--infile', '-i', dest='infile',
        help='a result file outputed by the RetroPath2.0 workflow',
        type=str, required=True)
    parser.add_argument(
        '--reverse', '-r', dest='reverse',
        help='switch, if used, the reactions will be outputed in the reverse \
        directions',
        required=False, action='store_true', default=False)
    parser.add_argument(
        '--compound_outfile', '-co', dest='compound_outfile',
        help='output file that will contains compound IDs',
        type=str, required=True)
    parser.add_argument(
        '--react_outfile', '-ro', dest='react_outfile',
        help='output file that will contains the reactions',
        type=str, required=True)
    parser.add_argument(
        '--sink_outfile', '-so', dest='sink_outfile',
        help='output file that will contains the sink compounds',
        type=str, required=True)
    args = parser.parse_args()

    compute(infile=args.infile, cmpdfile=args.compound_outfile,
            rxnfile=args.react_outfile, sinkfile=args.sink_outfile,
            reverse=args.reverse)
