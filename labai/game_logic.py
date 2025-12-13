#!/usr/bin/env python3
from typing import Tuple, List


class State:
    def __init__(self, tiles: Tuple[int, ...], rows: int, cols: int,
                 parent=None, move=None, depth=0):
        self.tiles = tiles      # 1 = шар, 0 = пусто
        self.rows = rows
        self.cols = cols
        self.parent = parent
        self.move = move
        self.depth = depth

    def __hash__(self): return hash(self.tiles)
    def __eq__(self, o): return isinstance(o, State) and self.tiles == o.tiles

    def expand(self) -> List['State']:
        n = []
        r, c = self.rows, self.cols
        for i in range(r-1):
            for j in range(c-1):
                a = i*c+j
                b = a+1
                ci = a+c
                d = ci+1
                t = list(self.tiles)
                # по часовой
                t[a], t[b], t[ci], t[d] = t[ci], t[a], t[d], t[b]
                n.append(State(tuple(t), r, c, self,
                               ("CW", i, j), self.depth+1))
                # против часовой
                t2 = list(self.tiles)
                t2[a], t2[b], t2[ci], t2[d] = t2[b], t2[d], t2[a], t2[ci]
                n.append(State(tuple(t2), r, c, self,
                               ("CCW", i, j), self.depth+1))
        return n

    def path(self):
        p = []
        s = self
        while s:
            p.append(s)
            s = s.parent
        return list(reversed(p))
