"""
Inmplementation of groups 
"""

import pandas as pd
from src.common import SymmetryGroupElements, CyclicGroupElements, Element, Pair


class Group:
    multable: pd.DataFrame
    neutral: str

    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return self.multable.to_string()

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
        group = Group()

        group.multable = pd.DataFrame(
            data=multable,
            columns=symbols,
            index=symbols,
        )
        group.neutral = neutral
        return group

    @classmethod
    def from_expression(cls, expr: str):
        group = Group()
        gr = expr[0]
        n = int(expr[1:])
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
            group.multable = pd.DataFrame(
                data=multable,
                columns=elems,
                index=elems,
            )
            group.neutral = elems[0]
            return group

        if gr == "C":
            elems = CyclicGroupElements(n)
            multable = []
            for l_elem in elems:
                row = []
                for r_elem in elems:
                    row.append(str((l_elem + r_elem) % n))
                multable.append(row)
            elems = [str(elem) for elem in elems]
            group.multable = pd.DataFrame(
                data=multable,
                columns=elems,
                index=elems,
            )
            group.neutral = elems[0]
            return group

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

    def get_symbols(self):
        return set(self.multable.columns)

    def subgroup(self, symbols):
        sub_group_elemes = tuple(sym for sym in operation_closure(self, symbols))
        multable = [
            [self.multiply_simbols(lsym, rsym) for rsym in sub_group_elemes]
            for lsym in sub_group_elemes
        ]

        multable = pd.DataFrame(
            data=multable, columns=sub_group_elemes, index=sub_group_elemes
        )
        neutral = self.neutral
        return SubGroup(multable, neutral, self)

    def normal_subgroup(self, symbols):
        subGroup_elemes = operation_closure(self, symbols)

        while True:
            subgroup_conj_closure = conj_closure(self, subGroup_elemes)

            if subgroup_conj_closure == subGroup_elemes:
                break

            subGroup_elemes = subgroup_conj_closure
            subGroup_op_closure = operation_closure(self, subGroup_elemes)

            if subGroup_elemes == subGroup_op_closure:
                break

            subGroup_elemes = subGroup_op_closure

        subGroup_elemes = tuple(sym for sym in subGroup_elemes)
        multable = [
            [self.multiply_simbols(lsym, rsym) for rsym in subGroup_elemes]
            for lsym in subGroup_elemes
        ]
        multable = pd.DataFrame(
            data=multable, columns=subGroup_elemes, index=subGroup_elemes
        )
        neutral = self.neutral
        return SubGroup(multable, neutral, self)

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


class SubGroup(Group):
    def __init__(self, multable: pd.DataFrame, neutral: str, group: Group):
        self.multable = multable
        self.neutral = neutral
        self.group = group


def conj_closure(group: Group, collection_of_elemt_symbols):
    """
    Return subset X of G sush as for every g in G gXg**-1 = X.
    """
    mult = group.multiply_simbols
    inv = group.inv_symbol
    return set(
        mult(mult(g, x), inv(g))
        for x in collection_of_elemt_symbols
        for g in group.get_symbols()
    )


def operation_closure(group: Group, collection_of_elemt_symbols):
    mult = group.multiply_simbols
    inv = group.inv_symbol
    closed_under_operations = set(x for x in collection_of_elemt_symbols)
    closed_under_operations = closed_under_operations.union(
        inv(x) for x in closed_under_operations
    )
    closed_under_operations.add(group.neutral)
    alphabet = closed_under_operations

    while True:
        multiSet = set(
            mult(lsym, rsym) for lsym in closed_under_operations for rsym in alphabet
        )

        if multiSet == closed_under_operations:
            break
        closed_under_operations = multiSet

    return closed_under_operations
