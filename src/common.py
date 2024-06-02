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

    def to_str(self):
        return f"({self.first}, {self.second})"


class Element:
    """
    Class for creating elements of a group

    symbol: str
        Symbol of the element.

    Group: Group
        Group to which the element belongs.
    """
    def __init__(self, symbol, Group):
        self.sym = symbol
        self.Group = Group

    def __mul__(self, other):
        if self.Group == other.Group:
            new_sym = self.Group.multiply_simbols(self.sym, other.sym)
            return Element(new_sym, self.Group)
        else:
            print("Different this elements has different groups.")

    def __str__(self):
        return self.sym

    def __pow__(self, power):
        Group = self.Group
        sym = Group.neutral

        if power < 0:
            inv_sym = self.inv().sym
            for _ in range(-power):
                sym = Group.multiply_simbols(sym, inv_sym)
            return Element(sym, Group)

        for _ in range(power):
            sym = Group.multiply_simbols(sym, self.sym)
        return Element(sym, Group)

    def __truediv__(self, other):
        return self * (other**-1)

    def inv(self):
        Group = self.Group
        Group_table = Group.multable
        sym = self.sym
        neutral_sym = Group.neutral

        col = Group_table[sym]

        inv_sym = col[col == neutral_sym].index[0]

        return Element(inv_sym, Group)

    def __len__(self):
        length = 1
        power = self
        neutral_sym = self.Group.neutral

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
