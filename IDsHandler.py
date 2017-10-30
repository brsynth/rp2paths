"""Class for handling IDs.

Copyright (C) 2016-2017 Thomas Duigou, JL Faulon's research group, INRA

Use of this source code is governed by the MIT license that can be found in the
LICENSE.txt file.

"""


class IDsHandler(object):
    """Handler in order to generate IDs."""

    def __init__(self, length=10, prefix='ID', sep='_'):
        """Initialization."""
        self.cpt = 1  # Counter of ID (first generated will be 1)
        self.length = length  # Length of the number part of the ID
        self.prefix = prefix  # Prefixe of each ID
        self.sep = sep  # Separator between prefix and number parts

    def MakeNewID(self):
        """Return a new ID and update the counter."""
        number_part = "0" * (self.length - len(str(self.cpt))) + str(self.cpt)
        new_id = self.prefix + self.sep + number_part
        self.cpt = self.cpt + 1
        return new_id
