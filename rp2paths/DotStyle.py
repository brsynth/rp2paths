"""Class for setting the appearance of a dot file.

Copyright (C) 2016-2017 Thomas Duigou, JL Faulon's research group, INRA

Use of this source code is governed by the MIT license that can be found in the
LICENSE.txt file.

"""


class NodeStyle(object):
    """General class for node style."""

    def __init__(self, **kwargs):
        """Initialize."""
        self.style = dict()
        for key, value in kwargs:
            self.style.extend(key, value)

    def GetStyle(self):
        """Return a dictionnary of key, value of .dot attributes."""
        return self.style


class Chassis(NodeStyle):
    """Style for a chassis compound node."""

    def __init__(self, **kwargs):
        """Initialize."""
        super().__init__(**kwargs)
        self.style.update({
            'shape': 'rectangle',
            'fontcolor': 'green',
            'color': 'green',
            'fontsize': '18',
            'penwidth': '0'
        })


class Intermediate(NodeStyle):
    """Style for an intermediate compound node."""

    def __init__(self, **kwargs):
        """Initialize."""
        super().__init__(**kwargs)
        self.style = {
            'shape': 'rectangle',
            'fontsize': '18',
            'penwidth': '0'
        }


class Target(NodeStyle):
    """Style for a target compound node."""

    def __init__(self, **kwargs):
        """Initialize."""
        super().__init__(**kwargs)
        self.style = {
            'shape': 'rectangle',
            'color': 'red',
            'fontsize': '18',
            'penwidth': '1'
        }


class Reaction(NodeStyle):
    """Style for a reaction node."""

    def __init__(self, **kwargs):
        """Initialize."""
        super().__init__(**kwargs)
        self.style = {
            'shape': 'oval',
            'fontsize': '24'
        }


class EdgeStyle(object):
    """General class for edge style."""

    def __init__(self, **kwargs):
        """Initialize."""
        self.style = dict()
        for key, value in kwargs:
            self.style.extend(key, value)

    def GetStyle(self):
        """Return a dictionnary of key, value of .dot attributes."""
        return self.style


class Consumption(EdgeStyle):
    """Style for a consumption edge."""

    def __init__(self, **kwargs):
        """Initialize."""
        super().__init__(**kwargs)
        self.style = {
            'color': 'green',
            'penwidth': '2',
            'arrowsize': '2'
        }


class Production(EdgeStyle):
    """Style for a production edge."""

    def __init__(self, **kwargs):
        """Initialize."""
        super().__init__(**kwargs)
        self.style = {
            'color': 'red',
            'penwidth': '2',
            'arrowsize': '2'
        }
