"""Class for handling reaction.

Copyright (C) 2017 JL Faulon's research group, INRA

Use of this source code is governed by the MIT license that can be found in the
LICENSE.txt file.

"""


class Compound(object):
    """General class representing a Compound."""

    def __init__(self, coeff, compound):
        self.coeff = coeff
        self.compound = compound

    def has_compounds(self, comps):
        return False

    def represented_compound(self):
        return 0


class StrCompound(Compound):
    """Compound represented by a string."""

    def __init__(self, coeff, compound):
        super(StrCompound, self).__init__(coeff, compound)

    def has_compounds(self, comps):
        return self.compound in comps

    def represented_compound(self):
        return 1

    def __str__(self):
        return '.'.join([str(self.coeff), self.compound])

    def __eq__(self, other):
        return self.coeff == other.coeff and self.compound == other.compound


class EquivCompound(Compound):
    """Compound represented by a list."""

    def __init__(self, coeff, compounds):
        super(EquivCompound, self).__init__(coeff, compounds)

    def has_compounds(self, comps):
        for comp in self.compound:
            if comp in comps:
                return True
        return False

    def represented_compound(self):
        return len(self.compound)

    def __str__(self):
        comps = '[' + ','.join(self.compound) + ']'
        return '.'.join([str(self.coeff), comps])

    def __lt__(self, c2):
        assert(isinstance(c2, EquivCompound))

        return [self.coeff] + self.compound < [c2.coeff] + c2.compound

    def __eq__(self, other):
        if self.coeff != other.coeff:
            return False
        s = set(self.compound)
        ss = set(other.compound)
        sss = s & ss
        return sss == s and sss == ss


class Reaction(object):
    """General class representing a Reaction."""

    def __init__(self, reaction):
        """Create a reaction from a string description."""
        r = reaction.rstrip().split('\t')

        self.name = r[0]
        self.enzyme = r[1]
        self.subs = self._parse_compounds(r[2])
        assert r[3] == "="
        self.prods = self._parse_compounds(r[4])

    def has_compounds(self, comps, sub=True):
        if sub:
            for comp in self.subs:
                if comp.has_compounds(comps):
                    return True
        else:
            for comp in self.prods:
                if comp.has_compounds(comps):
                    return True
        return False

    def __str__(self):
        subs = ':'.join([str(e) for e in self.subs])
        prods = ':'.join([str(e) for e in self.prods])

        return '\t'.join([self.name, self.enzyme, subs, '=', prods])

    def __eq__(self, other):
        return (self.name == other.name and
                self.enzyme == other.enzyme and
                self.subs == other.subs and
                self.prods == other.prods)

    def compounds(self):
        return self.subs + self.prods

    def possible_combinations(self):
        """Return the number of possible unfolding combinations."""
        return 0

    def as_str(self, reverse=False):
        """Return the reaction as string.

        Optional argument reverse allows to return the reaction in
        the reverse direction
        """
        subs = ":".join([str(e) for e in self.subs])
        prods = ":".join([str(e) for e in self.prods])
        if reverse is False:
            return '\t'.join([self.name, self.enzyme, subs, '=', prods])
        else:
            return '\t'.join([self.name, self.enzyme, prods, '=', subs])


class StrReaction(Reaction):
    """Reaction possessing only string compounds."""

    def __init__(self, reaction=''):
        super(StrReaction, self).__init__(reaction)

    @staticmethod
    def create(name, enzyme, subs, prods):
        react = StrReaction('')
        self.name = name
        self.enzyme = enzyme
        self.subs = subs
        self.prods = prods
        return res

    @staticmethod
    def from_file(f):
        """ Parse a file containing a list of reactions """
        res = []
        for line in f:
            res.append(StrReaction(line.rstrip()))
        return res

    def _parse_compounds(self, string):
        res = []
        elts = string.split(':')

        for elt in elts:
            c = elt.split('.')
            res.append(StrCompound(int(c[0]), c[1]))

        return res

    def involved_substrates(self):
        return set([s.compound for s in self.subs])

    def involved_products(self):
        return set([p.compound for p in self.prods])

    def involved_compounds(self):
        return self.involved_substrates() | self.involved_products()

    def possible_combinations(self):
        """
        Return the number of possible unfolding combinations
        """
        return 1

    def __lt__(self, r2):
        assert(isinstance(r2, StrReaction))

        return self.name < r2.name


class EquivReaction(Reaction):
    """Reaction possessing only list compounds."""

    def __init__(self, reaction=''):
        super(EquivReaction, self).__init__(reaction)

    @staticmethod
    def create(name, enzyme, subs, prods):
        react = EquivReaction('')
        self.name = name
        self.enzyme = enzyme
        self.subs = subs
        self.prods = prods
        return res

    @staticmethod
    def from_file(f):
        """Parse a file containing a list of reactions."""
        res = []
        for line in f:
            res.append(EquivReaction(line.rstrip()))
        return res

    @staticmethod
    def from_file_to_dict(f):
        """Parse a file containing a list of reactions."""
        res = {}
        for line in f:
            line = line.rstrip('\n')
            r = EquivReaction(line)
            # Handle reactions folded on name
            for name in r.name.split(','):
                res[name] = r
        return res

    def _parse_compounds(self, string):
        res = []
        elts = string.split(':')

        for elt in elts:
            c = elt.split('.')
            comps = c[1].lstrip('[').rstrip(']').split(',')
            res.append(EquivCompound(int(c[0]), comps))

        res.sort()  # PC: sorting helps in order to take a template that connects 2 folded reactions
        return res

    def involved_substrates(self):
        res = set()
        for sub in self.subs:
            for comp in sub.compound:
                res.add(comp)
        return res

    def involved_products(self):
        res = set()
        for prod in self.prods:
            for comp in prod.compound:
                res.add(comp)
        return res

    def involved_compounds(self):
        res = self.involved_substrates() | self.involved_products()
        return res

    def possible_combinations(self):
        """Return the number of possible unfolding combinations."""
        res = 1
        for sub in self.subs:
            res *= sub.represented_compound()
        for prod in self.prods:
            res *= prod.represented_compound()

        return res

    def _unfold_rec(self, base, l):
        if not l:
            return [base]

        res = []
        for i in range(len(l[0].compound)):
            res += self._unfold_rec(base + ":" + str(l[0].coeff) + "."
                                    + l[0].compound[i], l[1:])
        return res

    def unfold(self):
        usubs = []

        for elt in self.subs[0].compound:
            usubs += self._unfold_rec(str(self.subs[0].coeff) + "." + elt,
                                      self.subs[1:])

        res = []
        for i in range(len(usubs)):
            usubs[i] += "\t=\t"

        for elt in self.prods[0].compound:
            for e in usubs:
                res += self._unfold_rec(e + str(self.prods[0].coeff)
                                          + "." + elt, self.prods[1:])

        for i in range(len(res)):
            res[i] = '\t'.join([self.name + '_' + str(i), self.enzyme, res[i]])

        return [StrReaction(e) for e in res]


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: " + sys.argv[0] + " filename")
        sys.exit(1)

    reactions = []
    with open(sys.argv[1], 'r') as f:
        for line in f:
            reactions.append(Reaction(line.rstrip()))

    for react in reactions:
        print(react)
