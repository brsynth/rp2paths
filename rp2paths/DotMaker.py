"""Class for generating a single dot file.

Copyright (C) 2016-2017 Thomas Duigou, JL Faulon's research group, INRA

Use of this source code is governed by the MIT license that can be found in the
LICENSE.txt file.

"""

import os
import copy
import pydotplus
import graphviz
from rp2paths.DotStyle import Chassis as DS_Chassis
from rp2paths.DotStyle import Intermediate as DS_Intermediate
from rp2paths.DotStyle import Target as DS_Target
from rp2paths.DotStyle import Reaction as DS_Reaction
from rp2paths.DotStyle import Consumption as DS_Consumption
from rp2paths.DotStyle import Production as DS_Production
from rp2paths.IDsHandler import IDsHandler
from lxml import etree


class DotMaker(object):
    """Class for generating a single dot file."""

    def __init__(self, pid, pathway, chassis, target, imgdir=None,
                 cmpd_names=None,
                 chassis_style=DS_Chassis().GetStyle(),
                 intermediate_style=DS_Intermediate().GetStyle(),
                 target_style=DS_Target().GetStyle(),
                 reaction_style=DS_Reaction().GetStyle(),
                 consumption_style=DS_Consumption().GetStyle(),
                 production_style=DS_Production().GetStyle()):
        """Initialize."""
        self.pid = pid
        self.pathway = pathway
        self.chassis = set(chassis)
        self.target = target
        # Path to img folder
        self.imgdir = imgdir
        # Handling name of known compounds
        self.cmpd_names = cmpd_names
        # Default style for nodes
        self.chassis_style = chassis_style
        self.intermediate_style = intermediate_style
        self.target_style = target_style
        self.reaction_style = reaction_style
        # Default style for edges
        self.consumption_style = consumption_style
        self.production_style = production_style
        # Handling node IDs
        self.substrate_ids = IDsHandler(length=3, prefix='s', sep='_')
        self.intemediate_ids = IDsHandler(length=3, prefix='c', sep='_')
        self.product_ids = IDsHandler(length=3, prefix='p', sep='_')
        self.reaction_ids = IDsHandler(length=3, prefix='r', sep='_')
        self.name_to_ids = dict()
        self.graph = None

    @staticmethod
    def ParseReactionName(rxnName):
        """Return the label to be printed for a reaction."""
        first_name = rxnName.split(',')[0]  # In any case, names should be comma separated
        if first_name.startswith('MNXR'):  # Special case for MNXR reaction
            return first_name.split('_')[0]
        else:
            return first_name

    @staticmethod
    def MakeURL(entity, id):
        """Generate URL to MetaNetX."""
        if entity == 'Compound':
            if id.startswith('MNXM'):
                url = 'http://www.metanetx.org/cgi-bin/mnxweb/chem_info?chem=' + id
            elif id.startswith('CHEBI'):
                url = 'https://www.ebi.ac.uk/chebi/searchId.do?chebiId=' + id
            else:
                url = None
        elif entity == 'Reaction':
            if id.startswith('MNXR'):
                url = 'http://www.metanetx.org/cgi-bin/mnxweb/equa_info?equa=' + id
            else:
                url = None
        else:
            url = None
        return url

    def GetCompoundName(self, cid):
        """Return the name of the compound if known."""
        if (self.cmpd_names is not None) and \
                (cid in self.cmpd_names.keys()) and \
                (self.cmpd_names[cid] != ''):
            return self.cmpd_names[cid]
        else:
            return cid

    def MakeImgPath(self, cid):
        """Generate the image path of a compound node."""
        if self.imgdir is None:
            return None
        return os.path.join(self.imgdir, cid + '.svg')

    def MakeNodeID(self, nodeType):
        """Generate IDs for dot nodes."""
        if nodeType == 'Chassis':
            return self.substrate_ids.MakeNewID()
        elif nodeType == 'Intermediate':
            return self.intemediate_ids.MakeNewID()
        elif nodeType == 'Target':
            return self.product_ids.MakeNewID()
        elif nodeType == 'Reaction':
            return self.reaction_ids.MakeNewID()

    def RegisterNodeID(self, name, nid):
        """Store ID of a node."""
        # assert name not in self.name_to_ids.keys()
        self.name_to_ids.update({name: nid})

    def GetNodeID(self, name):
        """Return the node ID corresponding to a label."""
        return self.name_to_ids.get(name, None)

    def InitGraph(self, name, style={}):
        """Initialize the dot graph."""
        self.graph = pydotplus.graphviz.Graph(graph_name=name, **style)
        # self.graph = graphviz.Digraph(name=name, graph_attr=style)

    def AddNode(self, nid, label, style, url=None, img=None):
        """Add a new node to the dot graph."""
        attrs = dict()
        attrs.update(style)
        attrs.update({'label': label})
        if url is not None:
            attrs.update({'href': url})
        if img is not None:
            attrs.update({'image': img})
        self.graph.add_node(
            pydotplus.graphviz.Node(name=nid, **attrs))
        # self.graph.node(name=nid, **attrs)

    def AddEdge(self, startid, endid, style):
        """Add an edge to the dot graph."""
        attrs = dict()
        attrs.update(style)
        self.graph.add_edge(
            pydotplus.graphviz.Edge(src=startid, dst=endid, **attrs))
        # self.graph.edge(tail_name=startid, head_name=endid, **attrs)

    def MakeDot(self, graphname=None):
        """Generate a dot file for a given pathway."""
        # Init graph
        if graphname is None:
            graphname = 'pathway_' + self.pid
        self.InitGraph(name=graphname)

        # # Build reaction nodes
        # for rxn in self.pathway:
        #     rname = rxn.enzyme
        #     rid = self.MakeNodeID(nodeType='Reaction')
        #     self.RegisterNodeID(name=rname, nid=rid)
        #     rlabel = DotMaker.ParseReactionName(rname)
        #     url = DotMaker.MakeURL(entity='Reaction', id=rlabel)
        #     self.AddNode(nid=rid, label=rlabel, style=self.reaction_style,
        #                  url=url)

        # Get and sort compounds
        subs = set()
        prods = set()
        for rxn in self.pathway:
            subs |= rxn.involved_substrates()
            prods |= rxn.involved_products()
        assert self.target in prods
        # Intermediate compounds: all those not in chassis and not target
        intermediates = (subs | prods) - (self.chassis | set([self.target]))
        substrates = subs - intermediates

        # Build chassis compound nodes
        for cid in sorted(list(substrates)):
            nid = self.MakeNodeID(nodeType='Chassis')
            self.RegisterNodeID(name=cid, nid=nid)
            url = DotMaker.MakeURL(entity='Compound', id=cid)
            cname = self.GetCompoundName(cid=cid)
            # img = self.MakeImgPath(cid=cid)
            img = None  # Do not show image of chasssis compounds
            self.AddNode(nid=nid, label=cname, style=self.chassis_style,
                         url=url, img=img)

        # Build intermediate compound nodes
        for cname in sorted(list(intermediates)):
            nid = self.MakeNodeID(nodeType='Intermediate')
            self.RegisterNodeID(name=cname, nid=nid)
            img = self.MakeImgPath(cid=cname)
            self.AddNode(nid=nid, label=cname, style=self.intermediate_style,
                         img=img)

        # Add target compound node
        nid = self.MakeNodeID(nodeType='Target')
        self.RegisterNodeID(name=self.target, nid=nid)
        img = self.MakeImgPath(cid=self.target)
        self.AddNode(nid=nid, label=self.target, style=self.target_style,
                     img=img)

        # Add edges
        for rxn in self.pathway:

            # Build reaction node on the fly (easiest way to handle
            #   reactions that appears multiple times)
            rname = rxn.enzyme
            rid = self.MakeNodeID(nodeType='Reaction')
            # self.RegisterNodeID(name=rname, nid=rid)
            rlabel = DotMaker.ParseReactionName(rname)
            url = DotMaker.MakeURL(entity='Reaction', id=rlabel)
            self.AddNode(nid=rid, label=rlabel, style=self.reaction_style,
                         url=url)

            # Add edges to substrates and products
            # rname = rxn.enzyme
            # rid = self.GetNodeID(rname)
            subs = rxn.involved_substrates()
            for cname in subs:
                cid = self.GetNodeID(name=cname)
                self.AddEdge(startid=cid, endid=rid,
                             style=self.consumption_style)
            prods = rxn.involved_products()
            for cname in prods:
                cid = self.GetNodeID(name=cname)
                self.AddEdge(startid=rid, endid=cid,
                             style=self.production_style)

    def WriteDot(self, dotfile):
        """Write the resulting graph as .dot file."""
        src = graphviz.Source(self.graph.to_string())
        src.engine = 'dot'
        src.save(dotfile)

    @staticmethod
    def _RefineSvg(svgstring):
        """Add svg attribute so that href links open in new tab."""
        tree = etree.fromstring(bytes(svgstring, 'utf-8'))
        for g in tree.\
                find('{http://www.w3.org/2000/svg}g').\
                findall('{http://www.w3.org/2000/svg}g'):
            if g.get('class') == 'node':
                parent = g.find('{http://www.w3.org/2000/svg}g')
                if parent is not None:  # In case there is nothing to change..
                    a = parent.getchildren().pop()
                    if a.get('{http://www.w3.org/1999/xlink}href') is not None:
                        a.set('{http://www.w3.org/1999/xlink}show', 'new')
        return etree.tounicode(tree)

    def WriteSvg(self, svgfile):
        """Write the resulting graph as .svg file."""
        # Hide labels if we are using images
        graph = copy.deepcopy(self.graph)
        for node in graph.get_nodes():
            if 'image' in node.get_attributes():
                node.set('tooltip', node.get('label'))
                node.set('label', '')
        # Get the svg content
        src = graphviz.Source(graph.to_string())
        src.engine = 'dot'
        svgstring = src.pipe(format='svg').decode('utf-8')
        svgstring = DotMaker._RefineSvg(svgstring)
        # Write
        with open(svgfile, 'w') as fh:
            fh.write(svgstring)

    def WritePng(self, pngfile):
        """Write the resulting graph as .png file.

        CAUTIONS: implementation not complete
        """
        # Hide labels if we are using images
        graph = copy.deepcopy(self.graph)
        for node in graph.get_nodes():
            if 'image' in node.get_attributes():
                node.set('label', '')
        # Now write
        src = graphviz.Source(graph.to_string())
        src.engine = 'dot'
        with open(pngfile, 'bw') as fh:
            fh.write(src.pipe(format='png'))
