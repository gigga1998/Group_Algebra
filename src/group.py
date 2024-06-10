import random
import pandas as pd
from src.common import (SymmetryGroupElements, CyclicGroupElements, Element,
                        DihedralGroupElements, dihedral_mult, group_string_parser)
from src.function import Function


class Group:
    multable: pd.DataFrame
    neutral: str

    def __init__(self) -> None:
        """Init void group."""
        pass

    def __str__(self) -> str:
        """String cast."""
        return self.multable.to_string()

    @classmethod
    def from_pandas(cls, df, neutral):
        """Create group from df multable."""
        group = Group()
        group.multable = df
        group.neutral = neutral

        return group

    @classmethod
    def from_expression(cls, expr: str):
        """
        Create group from expression.
        
        expr has the followin type:
            Sn x Dm x Ck x ...

        examples:
            1. D3 x S2 x D3
            2. C2 x C4 x C6
            3. D5 x S11
        """

        group_list = [group_from_string(strg) for strg in group_string_parser(expr)]
        group = group_list[0]
        for gr in group_list[1:]:
            group *= gr
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
        """Get inv-symbol of current symbol."""
        """
        Return inverse elemen symbol for Elem(self, sym).
        """
        col = self.multable[sym]
        return col[col == self.neutral].index[0]

    def get_element(self, sym):
        """Get element with current symbol"""
        return Element(sym, self)

    def get_elements(self):
        """Get group elements."""
        return set(Element(sym, self) for sym in self.multable.columns)
    
    def get_symbols(self):
        """Get all symbols of group elements."""
        return set(self.multable.columns)

    def subgroup(self, symbols):
        """Generate sub-group."""
        subGroup_elemes = tuple(sym for sym in operation_closure(self, symbols))
        multable = [
            [self.multiply_simbols(lsym, rsym) for rsym in subGroup_elemes]
            for lsym in subGroup_elemes
        ]

        multable = pd.DataFrame(
            data=multable, columns=subGroup_elemes, index=subGroup_elemes
        )
        neutral = self.neutral
        return SubGroup(multable, neutral, self)

    def normal_subgroup(self, symbols):
        """Generate normal-subgroup."""
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
    
    def commutator(self, lsym, rsym):
        """Return commutator [lsym, rsym]."""
        inv_lsym = self.inv_symbol(lsym)
        inv_rsym = self.inv_symbol(rsym)
        mul = self.multiply_simbols

        return mul(mul(mul(inv_lsym, inv_rsym), lsym), rsym)
    
    def commutator_subgroup(self):
        """Return commutator sub-group."""
        group_syms = self.get_symbols()
        generator_set = set(
            self.commutator(lsym, rsym) for lsym in group_syms
            for rsym in group_syms
        )
        commutator_sub = self.normal_subgroup(generator_set)
        return commutator_sub
    
    def abelinization(self):
        """Return the abelinization of current Group."""
        commutator = self.commutator_subgroup()
        return self / commutator
    
    def __truediv__(self, subgroup):
        """Calculate factor-group."""
        assert self == subgroup.group

        group_symbols = self.get_symbols()
        subgroup_symbols = subgroup.get_symbols()

        group_symbols -= subgroup_symbols
        factor_group_symbols = [self.neutral]

        mult = self.multiply_simbols

        while group_symbols:
            random_symbol = random.choice(list(group_symbols))
            factor_group_symbols.append(random_symbol)
            group_symbols -= set(
                mult(random_symbol, symbol) for symbol in subgroup_symbols
                )
        
        def factor_mult(lsym, rsym):
            sym = mult(lsym, rsym)
            return f"[{find_equivalent(mult, subgroup_symbols, sym, factor_group_symbols)}]"

        multable = [
            [factor_mult(lsym, rsym) for rsym in factor_group_symbols]
            for lsym in factor_group_symbols
        ]
        factor_group_symbols = [f"[{sym}]" for sym in factor_group_symbols]
        multable = pd.DataFrame(
            multable, columns=factor_group_symbols , index=factor_group_symbols
        )
        neutral = f"[{self.neutral}]"

        return Group.from_pandas(multable, neutral)

    def __mul__(self, other):
        """Return direct product of groups."""
        tab1 = self.multable
        tab2 = other.multable

        syms1 = tab1.columns
        syms2 = tab2.columns

        new_syms = [(sym1, sym2) for sym1 in syms1 for sym2 in syms2]
        tab = []

        for pair1 in new_syms:
            row = []
            for pair2 in new_syms:
                first_sym = self.multiply_simbols(pair2[0], pair1[0])
                second_sym = other.multiply_simbols(pair2[1], pair1[1])
                row.append(f"({first_sym}, {second_sym})")
            tab.append(row)

        neutral = f"({self.neutral}, {other.neutral})"
        new_syms = [f"({pair[0]}, {pair[1]})" for pair in new_syms]
        df = pd.DataFrame(tab, columns=new_syms, index=new_syms)
        return Group.from_pandas(df, neutral)


class SubGroup(Group):
    def __init__(self, multable: pd.DataFrame, neutral: str, group: Group):
        self.multable = multable
        self.neutral = neutral
        self.group = group


class Homomorphism(Function):
    """Group homomorphism class."""

    def __init__(self, dct: dict, g1: Group, g2: Group):
        """Init g1 --> g2 homomorphism."""
        super().__init__(dct)
        homomorphism_test(dct, g1, g2)
        self.dom = g1.get_elements()
        self.cod = g2.get_elements()


def homomorphism_test(dct: dict, g1: Group, g2: Group):
    """Test that dct is homomorphism-dictionary."""
    dom = g1.get_symbols()
    cod = g2.get_symbols()

    if not set(dct.keys()) <= dom:
        raise Exception("Domain test exception!")

    if not set(dct[x] for x in dom) <= cod:
        raise Exception("Co-domain test exception!")

    for x in dom:
        for y in dom:
            if dct[g1.multiply_simbols(x, y)] != g2.multiply_simbols(dct[x], dct[y]):
                raise Exception("Homomorphism test exception!: f(ab) != f(a)f(b)")


def conj_closure(group: Group, collection_of_elemt_symbols):
    """Return subset X of G sush as for every g in G gXg**-1 = X."""
    mult = group.multiply_simbols
    inv = group.inv_symbol
    return set(
        mult(mult(g, x), inv(g)) for x in collection_of_elemt_symbols
        for g in group.get_symbols()
    )

def operation_closure(group: Group, collection_of_elemt_symbols):
    """Close collection af elements under group operations."""
    mult = group.multiply_simbols
    inv = group.inv_symbol
    closed_under_operations = set(
        x for x in collection_of_elemt_symbols
    )
    closed_under_operations = closed_under_operations.union(
        inv(x) for x in closed_under_operations
        )
    closed_under_operations.add(group.neutral)
    alphabet = closed_under_operations

    while True:
        multiSet = set(
            mult(lsym, rsym)
            for lsym in closed_under_operations
            for rsym in alphabet
        )

        if multiSet == closed_under_operations:
            break
        closed_under_operations = multiSet
    
    return closed_under_operations


def find_equivalent(multiplication, N, elem, elements):
    """Find euivalent symbol for elem in elements modulo N."""
    for rsym in N:
        for lsym in elements:
            if multiplication(lsym, rsym) == elem:
                return lsym
    return None


def symmetry_group(n: int):
    """Return symmetry group"""
    elems = SymmetryGroupElements(n)
    multable = [
                [
                    tuple(l_elem[r_elem[i] - 1] for i in range(n)) for r_elem in elems
                ] for l_elem in elems
            ]
    elems = [str(elem) for elem in elems]
    return Group.from_pandas(
                pd.DataFrame(multable, columns=elems, index=elems),
                elems[0]
            )


def dihedral_group(n: int):
    """Return symmetry group"""
    elems = DihedralGroupElements(n)
    multable = [
        [
            dihedral_mult(n, l_elem, r_elem) for r_elem in elems
        ] for l_elem in elems
    ]
    return Group.from_pandas(
        pd.DataFrame(multable, columns=elems, index=elems),
        elems[0]
    )


def cyclic_group(n: int):
    """Return symmetry group"""
    elems = CyclicGroupElements(n)
    multable = [
        [
            str((l_elem + r_elem) % n) for r_elem in elems
        ] for l_elem in elems
    ]
    elems = [str(elem) for elem in elems]
    return Group.from_pandas(
        pd.DataFrame(multable, columns=elems, index=elems),
        elems[0]
    )


def quaternion_group():
    """Return quaternion group."""
    elems = ('1', '-1', 'i', '-i', 'j', '-j', 'k', '-k')
    multable = (
        ('1', '-1', 'i', '-i', 'j', '-j', 'k', '-k'),
        ('-1', '1', '-i', 'i', '-j', 'j', '-k', 'k'),
        ('i', '-i', '-1', '1', 'k', '-k', '-j', 'j'),
        ('-i', 'i', '1', '-1', '-k', 'k', 'j', '-j'),
        ('j', '-j', '-k', 'k', '-1', '1', 'i', '-i'),
        ('-j', 'j', 'k', '-k', '1', '-1', '-i', 'i'),
        ('k', '-k', 'j', '-j', '-i', 'i', '-1', '1'),
        ('-k', 'k', '-j', 'j', 'i', '-i', '1', '-1'),
    )
    return Group.from_pandas(
        pd.DataFrame(multable, columns=elems, index=elems),
        elems[0]
    )


def group_from_string(string):
    """
    Return group from string.
    
    string has one of the following types:
        'Sn', 'Dn', 'Cn'
    """
    grou_type = string[0]
    n = string[1:]
    if grou_type == "C":
        return cyclic_group(int(n))

    if grou_type == "D":
        return dihedral_group(int(n))
    
    if grou_type == "S":
        return symmetry_group(int(n))
    
    if grou_type == "Q":
        return quaternion_group()
