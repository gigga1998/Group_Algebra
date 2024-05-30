
import pandas as pd
import itertools

class Pair():
    def __init__(self, elem1, elem2):
        self.first = elem1
        self.second = elem2

    def get1(self):
        return self.first

    def get2(self):
        return self.second
    
    def to_str(self):
        return f"({self.first}, {self.second})"
        

class Element():

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
        return self * (other ** -1)

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

        while (power.sym != neutral_sym):
            length += 1
            power *= self
        return length


class Group():

    def __init__(self, multable, neutral):
        """
        multable -- 2d multiplication table.
        example: [
                  ['a', 'b'],
                  ['b', 'a']
                 ]
        """
        symbols = multable[0]
        self.multable = pd.DataFrame(
            data=multable,
            columns=symbols,
            index=symbols,
        )
        self.neutral = neutral

    def __init__(self, statement: str):
        gr = statement[0]
        n = int(statement[1:])
        if gr == "S":
            elems = SymmetryGroupElements(n)
            multable = []
            for l_elem in elems:
                row = []
                for r_elem in elems:
                    mult_res = tuple(l_elem[r_elem[i] - 1] for i in range(n))
                    row.append(str(mult_res))
                multable.append(row)
            elems = [str(elem) for elem in elems]
            self.multable = pd.DataFrame(
                data=multable,
                columns=elems,
                index=elems,
            )
            self.neutral = elems[0]
        
        if gr == "C":
            elems = CyclicGroupElements(n)
            multable = []
            for l_elem in elems:
                row = []
                for r_elem in elems:
                    row.append(str((l_elem + r_elem) % n))
                multable.append(row)
            elems = [str(elem) for elem in elems]
            self.multable = pd.DataFrame(
                data=multable,
                columns=elems,
                index=elems,
            )
            self.neutral = elems[0]


    def multiply_simbols(self, sym1, sym2):
        """
        Return result of sym1 * sym2.
        If multable is
                        | 'e' | 'a' | 'b' | 'c' | 'd' | 'f'
                    ----|-----|-----|-----|-----|-----|-----
                     'e'| 'e' | 'a' | 'b' | 'c' | 'd' | 'f'
                    ----|-----|-----|-----|-----|-----|-----
                     'a'| 'a' | 'e' |     |     |     |
                    ----|-----|-----|-----|-----|-----|-----
                     'b'| 'b' |     | 'e' |     |     |
                    ----|-----|-----|-----|-----|-----|-----
                     'c'| 'c' |     |     | 'd' |     |
                    ----|-----|-----|-----|-----|-----|-----
                     'd'| 'd' |     |     |     |     |
                    ----|-----|-----|-----|-----|-----|-----
                     'f'| 'f' |     |     |     |     |
                    ----|-----|-----|-----|-----|-----|-----

                    
        """
        return self.multable[sym2][sym1]
    
    def inv_symbol(self, sym):
        """
        Return inverse elemen symbol for Elem(self, sym).
        """
        return self.multable[sym][self.multable[sym] == self.neutral].index[0]
    
    def get_element(self, sym):
        return Element(sym, self)
    
    def get_elements(self):
        return set(
            Element(sym, self) for sym in self.multable.columns
            )
    
    def generate_subgroup(self, symbols):
        copy_elements = elements
        for elem in copy_elements:
            elements = elements.union(set(
                self.multiply_simbols()
            ))
        
    def __mul__(self, other):
        tab1 = self.multable
        tab2 = other.multable

        syms1 = tab1.columns
        syms2 = tab2.columns

        new_syms = [
            Pair(sym1, sym2) for sym1 in syms1 for sym2 in syms2
        ]
        tab = []

        for pair1 in new_syms:
            row = []
            for pair2 in new_syms:
                first_sym = self.multiply_simbols(
                    pair2.get1(),
                    pair1.get1()
                )
                second_sym = other.multiply_simbols(
                    pair2.get2(),
                    pair1.get2()
                )
                row.append(f"({first_sym}, {second_sym})")
            tab.append(row)

        return Group(tab)

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
    return [i for i in range(n)]

if __name__ == "__main__":
    grp = Group("S3")
    elme = grp.get_element('(2, 3, 1)')
    print(elme / elme)