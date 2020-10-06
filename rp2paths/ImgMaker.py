"""Class for generating a single picture of compound.

Copyright (C) 2016-2017 Thomas Duigou, JL Faulon's research group, INRA

Use of this source code is governed by the MIT license that can be found in the
LICENSE.txt file.

"""

from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import rdDepictor


class ImgMaker(object):
    """Class for generating a single picture of compound."""

    def __init__(self, smiles, svgfile, legend,
                 width=400, height=200,
                 tryCairo=True, kekulize=True):
        """Initialize."""
        self.smiles = smiles
        self.svgfile = svgfile
        self.legend = legend
        self.width = width
        self.height = height
        self.tryCairo = tryCairo
        self.kekulize = kekulize

    def _CairoDrawer(self, rdmol):
        """Render an svg using cairo or agg renderer."""
        # Some drawing options
        options = Draw.DrawingOptions()
        options.bondLineWidth = 1
        # Prepare drawing
        useAGG, useCairo, Canvas = Draw._getCanvas()
        canvas = Canvas(size=(self.width, self.height),
                        imageType='svg',
                        fileName=self.svgfile)
        drawer = Draw.MolDrawing(canvas=canvas, drawingOptions=options)
        drawer.AddMol(rdmol)
        if self.legend is not None:
            from rdkit.Chem.Draw.MolDrawing import Font
            pos = (self.width/2, int(.1*self.height), 0)
            font = Font(face='serif', size=18)
            canvas.addCanvasText(self.legend, pos, font)
        canvas.flush()

    def _FallBackDrawer(self, rdmol):
        """Render an svg using a C++ renderer.

        Note: lower quality, but always work.
        """
        # Some size calculation
        legend_margin = 50
        width = self.width
        height = self.height - legend_margin
        # Make the raw svg
        drawer = Draw.rdMolDraw2D.MolDraw2DSVG(width, height)
        drawer.DrawMolecule(rdmol, legend=self.legend)
        drawer.FinishDrawing()
        svg = drawer.GetDrawingText()
        # Refine the raw svg
        from lxml import etree
        # Get content
        tree = etree.fromstring(bytes(svg, 'utf-8'))
        # Add top margin for the legend
        tree.attrib['width'] = str(width)
        tree.attrib['height'] = str(height + legend_margin)
        tree.attrib['viewBox'] = '0 -50 ' + str(width) + ' ' + str(height + 50)
        # Change legend font size and position
        for e in tree.findall('{http://www.w3.org/2000/svg}text'):
            if e.find('{http://www.w3.org/2000/svg}tspan').text == self.legend:
                del e.attrib['style']
                # Shift legend
                e.attrib['x'] = str(width / 2)
                e.attrib['y'] = str(-10)
                e.attrib['text-anchor'] = 'middle'
                # Change font
                e.attrib['font-size'] = str(18) + 'px'
                e.attrib['font-family'] = 'serif'
        # Got back to a string
        svg = etree.tounicode(tree)
        # Add some missing markup
        svg = '<?xml version="1.0" encoding="UTF-8"?>\n' + svg
        # Write
        with open(self.svgfile, 'w') as fh:
            fh.write(svg)

    def _MakeRdMol(self):
        """Sanitize and compute 2D coordinate of compound."""
        # Get a valid rdmol object
        rdmol = Chem.MolFromSmiles(self.smiles)
        if rdmol is None:
            rdmol = Chem.MolFromSmiles(self.smiles, sanitize=False)
            Chem.SanitizeMol(
                rdmol, sanitizeOps=Chem.SanitizeFlags.SANITIZE_ALL
                ^ Chem.SanitizeFlags.SANITIZE_KEKULIZE
                ^ Chem.SanitizeFlags.SANITIZE_SETAROMATICITY)
        # Kekulize if necessary
        if self.kekulize:
            try:
                Chem.Kekulize(rdmol)
            except BaseException:
                pass
        # Handle coordinate
        if not rdmol.GetNumConformers():
            rdDepictor.Compute2DCoords(rdmol)
        return rdmol

    def MakeSvg(self):
        """Generating a svg from a Smiles."""
        # Get the rdmol object
        rdmol = self._MakeRdMol()
        # Let choose the way/tool of drawing the compounds
        useAGG, useCairo, Canvas = Chem.Draw._getCanvas()
        if self.tryCairo and (useAGG or useCairo):
            self._CairoDrawer(rdmol=rdmol)
        else:
            self._FallBackDrawer(rdmol=rdmol)
