from ctypes import ArgumentError
import math
import numpy as np
from src.group import Group
from src.common import Pair


class DihedralGroup(Group):
    def __init__(self, n: int):
        self.n = n
        self.rotations = [f"r{x}" for x in range(0, n)]
        self.reflections = [f"s{x}" for x in range(0, n)]
        self.elements = self.rotations + self.reflections
        self.identity = "e"

    def get_pairtable(self) -> dict:
        pairtable = {}
        for a in self.elements:
            for b in self.elements:
                pairtable[Pair(a, b)] = self.mult(a, b)
        return pairtable

    def _symb2mat(self, symbol: str) -> np.ndarray:
        _s = symbol[0]
        _k = int(symbol[1:])
        c = 2 * math.pi * _k / self.n
        if _s == "r":
            return np.array(
                [
                    [round(math.cos(c)), round(-math.sin(c))],
                    [round(math.sin(c)), round(math.cos(c))],
                ]
            )
        if _s == "s":
            return np.array(
                [
                    [round(math.cos(c)), round(math.sin(c))],
                    [round(math.sin(c)), round(-math.cos(c))],
                ]
            )
        else:
            raise ArgumentError(
                "Wrong symbol to get rotation matrix for this diheral group"
            )

    def get_mattable(self) -> dict:
        mattable = {}
        for a in self.elements:
            mattable[a] = {}
            for b in self.elements:
                mattable[a][b] = self._symb2mat(a) @ self._symb2mat(b)
        return mattable

    def get_multable(self) -> dict:
        multable = {}
        for a in self.elements:
            multable[a] = {}
            for b in self.elements:
                multable[a][b] = self.mult(a, b)
        return multable

    def mult(self, a: str, b: str) -> str:
        if a == self.identity:
            return b
        if b == self.identity:
            return a
        if a in self.rotations and b in self.rotations:
            _idx = (self.rotations.index(a) + self.rotations.index(b)) % self.n
            return self.rotations[_idx]
        if a in self.reflections and b in self.reflections:
            _idx = (self.reflections.index(a) - self.reflections.index(b)) % self.n
            return self.rotations[_idx]
        if a in self.rotations and b in self.reflections:
            _idx = (self.rotations.index(a) + self.reflections.index(b)) % self.n
            return self.reflections[_idx]
        if a in self.reflections and b in self.rotations:
            _idx = (self.reflections.index(a) - self.rotations.index(b)) % self.n
            return self.reflections[_idx]
        return self.identity


if __name__ == "__main__":
    import pandas as pd

    d = DihedralGroup(1)
    print(pd.DataFrame(d.get_multable()))
