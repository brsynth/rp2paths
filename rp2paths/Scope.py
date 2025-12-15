"""
scope (c) University of Manchester 2016

scope is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  Pablo Carbonell, SYNBIOCHEM
@description: Compute scope
"""
from os import path, unlink
import argparse
import re
import numpy as np
import pandas as pd
import csv
from logging import getLogger


def arguments():
    """Parsing command line arguments."""
    parser = argparse.ArgumentParser(description='New scope, Pablo Carbonell, \
                                     SYNBIOCHEM, 2016')
    parser.add_argument('out_folder',
                        help='Out folder')
    parser.add_argument('sink_file',
                        help='Sink file')
    parser.add_argument('reaction_file',
                        help='Reaction file')
    parser.add_argument('target',
                        help='Target')
    parser.add_argument('-maxIter', default=None,
                        help='Limit the maximum iteration depth')
    parser.add_argument('-minDepth', action='store_true',
                        help='Stop at the smallest iteration with non-empty \
                        scope')
    parser.add_argument('-keepBoots', action='store_true',
                        help='Remove bootstrap reactions unless flag is set')
    arg = parser.parse_args()
    # arg.target = '['+arg.target+']'  # TD: not anymore needed
    return arg


def reactants(reac):
    """Extract reactant from a reaction."""
    rl = {}
    for x in reac.split(':'):
        v = x.split('.')
        try:
            n = int(v[0])
        except BaseException:
            continue
        c = v[1].strip("[]")
        rl[c] = n
    return rl


def readSinks(sinkFile):
    """Get the list of compounds to consider as sink."""
    sinks = set()
    for line in open(sinkFile):
        m = line.rstrip().split('\t')
        sinks.add(m[0])
    return sinks


def readReaction(rxnFile, maxIter=-1, keepBoots=False):
    """Get the reaction to consider for the scope."""
    maxDepth = 0
    rxn = {}
    rxnFull = {}
    for line in open(rxnFile):
        m = line.rstrip().split('\t')
        rid = m[0]
        rinfo = rid.split('_')
        niter = 0
        try:
            niter = int(rinfo[2])
            if niter > maxDepth:
                maxDepth = niter
        except BaseException:
            pass
        if maxIter != -1:
            if niter > maxIter:
                continue
        subs = m[2]
        rsubs = reactants(subs)
        prods = m[4]
        rprods = reactants(prods)
        if not keepBoots:
            boots = set(rprods) & set(rsubs)
            if any(boots):
                continue
        entry = {}
        for x in rsubs:
            entry[x] = -rsubs[x]
        for x in rprods:
            entry[x] = rprods[x]
        rxnFull[rid] = line
        rxn[rid] = entry
    return rxn, rxnFull, maxDepth


def inSoup(rxn, pending, soup):
    '''Verify if new reactions can be fired.'''
    newPending = set(pending)
    newSoup = set(soup)
    for r in pending:
        subs = set()
        prods = set()
        for c in rxn[r]:
            if rxn[r][c] < 0:
                subs.add(c)
            else:
                prods.add(c)
        if len(subs - soup) == 0:
            newPending -= set([r])
            newSoup |= prods
    return newPending, newSoup


def reachableReactions(rxn, sinks):
    """Look for reachable reactions."""
    soup = sinks
    pending = set(rxn)
    newPending, newSoup = inSoup(rxn, pending, soup)
    iteration = 0
    while (len(newPending - pending) > 0 or len(newSoup - soup) > 0):
        pending = newPending
        soup = newSoup
        newPending, newSoup = inSoup(rxn, pending, soup)
        iteration += 1

    return newPending, newSoup, iteration


def addFoldedSinks(sinks, rxn):
    for r in rxn:
        for c in rxn[r]:
            if set(c.split(',')) & sinks:
                sinks.add(c)
    return sinks


def cleanOutFiles(outFolder):
    """Initially clean the output files."""
    for f in ['out_react', 'out_comp', 'out_rever', 'out_mat', 'out_infp',
              'out_discarded', 'out_full_react']:
        if path.exists(path.join(outFolder, f)):
            unlink(path.join(outFolder, f))


class Scope(object):
    """Class for handling scope data."""

    def __init__(self, rxn, reachable=None):
        """Generate stoichiometric matrix."""
        if reachable is not None:
            rSorted = sorted(reachable)
        else:
            rSorted = sorted(rxn)
        cList = set()
        for r in rSorted:
            cList |= set(rxn[r])
        cSorted = sorted(cList)
        smat = np.zeros((len(cSorted), len(rSorted)))
        for r in rSorted:
            for c in rxn[r]:
                smat[cSorted.index(c), rSorted.index(r)] = rxn[r][c]
        self.dfmat = pd.DataFrame(data=smat, index=cSorted, columns=rSorted)

    def removeSinks(self, sinks):
        """Remove rows in sinks."""
        sinkRows = []
        for c in sinks:
            if c in self.dfmat.index:
                # sinkRows.append(int(np.where(self.dfmat.index == c)[0]))
                sinkRows.append(int(np.where(self.dfmat.index == c)[0][0]))
        cSorted2 = sorted(list(set(self.dfmat.index) - sinks))
        sinkRows.sort()
        smat = np.delete(self.dfmat.values, sinkRows, 0)
        self.dfmat = pd.DataFrame(data=smat, index=cSorted2,
                                  columns=self.dfmat.columns)

    def foldCols(self):
        """Remove duplicated columns."""
        smat = self.dfmat.values
        sh = smat.shape
        colFP = {}
        for i in range(0, sh[1]):
            fp = '_'.join(map(str, smat[:, i]))
            if fp not in colFP:
                colFP[fp] = []
            colFP[fp].append(i)
        duplicateCols = []
        rxnLabels = []
        for fp in colFP:
            rLab = []
            for j in range(0, len(colFP[fp])):
                ix = colFP[fp][j]
                rLab.append(self.dfmat.columns[ix])
                if j >= 1:
                    duplicateCols.append(ix)
            rxnLabels.append(','.join(rLab))
        rSorted2 = sorted(rxnLabels)
        smat = np.delete(smat, sorted(duplicateCols), 1)
        self.dfmat = pd.DataFrame(data=smat, index=self.dfmat.index,
                                  columns=rSorted2)

    def addOutput(self, target):
        """Add output row."""
        ix = np.where(self.dfmat.index == target)[0]
        outRow = np.zeros((len(self.dfmat.index), 1))
        outRow[ix] = -1.0
        smat = np.hstack([self.dfmat.values, outRow])
        self.dfmat = pd.DataFrame(
            data=smat, index=self.dfmat.index,
            #   columns=np.hstack([self.dfmat.columns, 'O'+target]))  # TD: not needed
            columns=np.hstack([self.dfmat.columns, 'O[' + target + ']']))

    def outFiles(self, niter, rxnFull, outFolder):
        """Write scope."""
        logger = getLogger(__name__)
        logger.debug('Writing output files to %s', outFolder)
        smat = self.dfmat.values
        with open(path.join(outFolder, 'out_react'), 'w', newline='') as out_react:
            cv = csv.writer(out_react, delimiter=' ', quoting=csv.QUOTE_ALL)
            cv.writerow(self.dfmat.columns)
        with open(path.join(outFolder, 'out_comp'), 'w', newline='') as out_comp:
            cv = csv.writer(out_comp, delimiter=' ', quoting=csv.QUOTE_ALL)
            # cv.writerow(map(lambda h:  h, self.dfmat.index))  # TD
            cv.writerow(map(lambda h: '[' + h + ']', self.dfmat.index))
        with open(path.join(outFolder, 'out_rever'), 'w', newline='') as out_rever:
            cv = csv.writer(out_rever, delimiter=' ', quoting=csv.QUOTE_MINIMAL)
            cv.writerow(np.zeros(len(self.dfmat.columns), dtype=int))
        with open(path.join(outFolder, 'out_mat'), 'w', newline='') as out_mat:
            cv = csv.writer(out_mat, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
            for i in range(0, len(self.dfmat.index)):
                cv.writerow(np.array(smat[i, :], dtype=int))
        with open(path.join(outFolder, 'out_info'), 'w', newline='') as out_info:
            out_info.write('iteration = %d\n' % (niter,))
        with open(path.join(outFolder, 'out_discarded'), 'w', newline='') as out_discarded:
            pass  # add discarded compounds/reactions?
        with open(path.join(outFolder, 'out_full_react'), 'w', newline='') as out_full_react:
            for rxn in self.dfmat.columns:
                for rid in set(rxn.split(',')) & set(rxnFull):
                    out_full_react.write(rxnFull[rid])


def compute(out_folder, sink_file, reaction_file, target,
            maxIter=-1, minDepth=False, keepBoots=False, forward=False, logger=getLogger(__name__)):
    """Compute scope."""
    """ Extract the sub-network where reactions can be fired, either because
    substrates are in sink or they are products of other reactions can be fired"""

    logger.debug('Computing scope for target %s', target)
    logger.debug('Using reaction file %s', reaction_file)
    logger.debug('Using sink file %s', sink_file)
    logger.debug('Output folder %s', out_folder)
    logger.debug('Max iterations %s', str(maxIter))
    logger.debug('Min depth flag %s', str(minDepth))
    logger.debug('Keep bootstraps flag %s', str(keepBoots))
    logger.debug('Forward flag %s', str(forward))

    rxn, rxnFull, maxDepth = readReaction(reaction_file, keepBoots=keepBoots)
    logger.debug('Total reactions read: %d', len(rxn))
    logger.debug('Maximum reaction depth: %d', maxDepth)
    logger.debug('Reaction details:')
    for rid in rxn:
        logger.debug('Reaction %s: %s', rid, str(rxn[rid]))
    logger.debug('Full reaction details:')
    for rid in rxnFull:
        logger.debug('Reaction %s: %s', rid, str(rxn[rid]))
    
    cleanOutFiles(out_folder)
    if minDepth:
        startDepth = 0
    else:
        startDepth = maxDepth
    if maxIter == -1:
        endDepth = maxDepth
    else:
        startDepth = endDepth = maxIter
    for depth in range(startDepth, endDepth+1):
        logger.debug('Computing scope at depth %d', depth)
        rxn, rxnFull, maxDepth = readReaction(reaction_file, maxIter=depth,
                                              keepBoots=keepBoots)
        logger.debug('Total reactions read: %d', len(rxn))
        logger.debug('Maximum reaction depth: %d', maxDepth)
        logger.debug('Reaction details:')
        for rid in rxn:
            logger.debug('Reaction %s: %s', rid, str(rxn[rid]))
        logger.debug('Full reaction details:')
        for rid in rxnFull:
            logger.debug('Reaction %s: %s', rid, str(rxn[rid]))
        if not forward:
            sinks = readSinks(sink_file)
        else: # empty sink
            sinks = set()
            sinks.add(target)
        sinks = addFoldedSinks(sinks, rxn)
        nonReachableReactions, broth, niter = reachableReactions(rxn, sinks)
        if target not in broth:
            nonReachableReactions = set(rxn)
        scope = Scope(rxn, reachable=set(rxn) - nonReachableReactions)
        if not forward:
            scope.removeSinks(sinks)
        scope.foldCols()
        scope.addOutput(target)
        logger.debug('Scope matrix shape: %s', str(scope.dfmat.shape))
        if scope.dfmat.shape[0] > 0:
            scope.outFiles(niter, rxnFull, out_folder)
            break


if __name__ == '__main__':
    arg = arguments()

    compute(
        out_folder=arg.out_folder,
        sink_file=arg.sink_file,
        reaction_file=arg.reaction_file,
        target=arg.target,
        maxIter=arg.maxIter,
        minDepth=arg.minDepth,
        keepBoots=arg.keepBoots
    )
