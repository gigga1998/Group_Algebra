import unittest
from src.dihedral_group import DihedralGroup


class TestDihedralGroup(unittest.TestCase):
    def test_d1(self):
        d1 = DihedralGroup(1)
        self.assertEqual(d1.mult("r0", "r0"), "r0")
        self.assertEqual(d1.mult("r0", "s0"), "s0")
        self.assertEqual(d1.mult("s0", "r0"), "s0")
        self.assertEqual(d1.mult("s0", "s0"), "r0")
