"""
Utilitarity functions for the group theory task
"""

import itertools


class Pair:
    """
    Class for creating pairs of elements.
    """

    def __init__(self, elem1, elem2):
        self.first = elem1
        self.second = elem2

    def get1(self):
        return self.first

    def get2(self):
        return self.second

    def __str__(self):
        return f"({self.first}, {self.second})"

    def __repr__(self):
        return f"({self.first}, {self.second})"


class Element:
    """
    Class for creating elements of a group

    symbol: str
        Symbol of the element.

    Group: Group
        Group to which the element belongs.
    """

    def __init__(self, symbol, group):
        self.sym = symbol
        self.group = group

    def __mul__(self, other):
        if self.group == other.Group:
            new_sym = self.group.multiply_simbols(self.sym, other.sym)
            return Element(new_sym, self.group)
        else:
            print("Different this elements has different groups.")

    def __str__(self):
        return self.sym

    def __pow__(self, power):
        group = self.group
        sym = group.neutral

        if power < 0:
            inv_sym = self.inv().sym
            for _ in range(-power):
                sym = group.multiply_simbols(sym, inv_sym)
            return Element(sym, group)

        for _ in range(power):
            sym = group.multiply_simbols(sym, self.sym)
        return Element(sym, group)

    def __truediv__(self, other):
        return self * (other**-1)

    def inv(self):
        group = self.group
        group_table = group.multable
        sym = self.sym
        neutral_sym = group.neutral

        col = group_table[sym]

        inv_sym = col[col == neutral_sym].index[0]

        return Element(inv_sym, group)

    def __len__(self):
        length = 1
        power = self
        neutral_sym = self.group.neutral

        while power.sym != neutral_sym:
            length += 1
            power *= self
        return length


def SymmetryGroupElements(n: int) -> list[str]:
    """
    Return all perms of {1, 2, ..., n} set.

    Perm f: {1, 2, ..., n} -> {1, 2, ..., n} such as
    f(i) = j will be signed as (f(1), f(2), ..., f(n))
    """
    lst = (i for i in range(1, n + 1))
    return [tuple(elem) for elem in itertools.permutations(lst)]


def CyclicGroupElements(n: int) -> list[str]:
    """
    Return cyclic group elements.
    example:
        input: 5
        output: ['0', '1', '2', '3', '4']
    """
    return list(range(n))
