import pandas as pd
from src.common import SymmetryGroupElements, CyclicGroupElements, Element, Pair


class Group:
    @classmethod
    def new_group(cls, multable, neutral):
        """
        multable -- 2d multiplication table.
        example: [
                  ['a', 'b'],
                  ['b', 'a']
                 ]
        """
        symbols = multable[0]
        group = Group("Empty")

        group.multable = pd.DataFrame(
            data=multable,
            columns=symbols,
            index=symbols,
        )
        group.neutral = neutral
        return group

    def __init__(self, statement: str):
        if statement == "Empty":
            self.multable = None
            self.neutral = None
        else:
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
        col = self.multable[sym]
        return col[col == self.neutral].index[0]

    def get_element(self, sym):
        return Element(sym, self)

    def get_elements(self):
        return set(Element(sym, self) for sym in self.multable.columns)

    def generate_subgroup(self, symbols):
        subGroup = set(sym for sym in symbols)
        subGroup |= set(self.inv_symbol(sym) for sym in symbols)
        alphabet = frozenset(subGroup)
        subGroup.add(self.neutral)

        while True:
            multiSet = set(
                self.multiply_simbols(lsym, rsym)
                for lsym in subGroup
                for rsym in alphabet
            )

            if multiSet == subGroup:
                break
            subGroup = multiSet

        subGroup_elemes = tuple(subGroup)
        multable = [
            [self.multiply_simbols(lsym, rsym) for rsym in subGroup_elemes]
            for lsym in subGroup_elemes
        ]
        subGroup = Group("Empty")
        subGroup.multable = pd.DataFrame(
            data=multable, columns=subGroup_elemes, index=subGroup_elemes
        )
        subGroup.neutral = self.neutral
        return subGroup

    def __mul__(self, other):
        tab1 = self.multable
        tab2 = other.multable

        syms1 = tab1.columns
        syms2 = tab2.columns

        new_syms = [Pair(sym1, sym2) for sym1 in syms1 for sym2 in syms2]
        tab = []

        for pair1 in new_syms:
            row = []
            for pair2 in new_syms:
                first_sym = self.multiply_simbols(pair2.get1(), pair1.get1())
                second_sym = other.multiply_simbols(pair2.get2(), pair1.get2())
                row.append(f"({first_sym}, {second_sym})")
            tab.append(row)

        neutral = f"({self.neutral}, {other.neutral})"
        return Group.new_group(tab, neutral)


