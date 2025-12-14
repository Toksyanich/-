#!/usr/bin/env python3
import random
from typing import Tuple, List, Optional


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


def _rotate_tiles(tiles: Tuple[int, ...], rows: int, cols: int,
                  direction: str, i: int, j: int) -> Tuple[int, ...]:
    """Return a new tile tuple after rotating the 2x2 block at (i, j)."""
    a = i * cols + j
    b = a + 1
    c = a + cols
    d = c + 1
    t = list(tiles)
    if direction == "CW":
        t[a], t[b], t[c], t[d] = t[c], t[a], t[d], t[b]
    elif direction == "CCW":
        t[a], t[b], t[c], t[d] = t[b], t[d], t[a], t[c]
    else:
        raise ValueError(f"Unknown direction: {direction}")
    return tuple(t)


def apply_move(tiles: Tuple[int, ...], rows: int, cols: int,
               move: Tuple[str, int, int]) -> Tuple[int, ...]:
    """Apply a single move (direction, i, j) to tiles and return a new tuple."""
    direction, i, j = move
    return _rotate_tiles(tiles, rows, cols, direction, i, j)


def tiles_to_string(tiles: Tuple[int, ...], rows: int, cols: int) -> str:
    """Serialize tiles as row chunks joined with '/' for logging/CSV."""
    parts = []
    for r in range(rows):
        row = tiles[r * cols:(r + 1) * cols]
        parts.append(''.join(str(int(x)) for x in row))
    return '/'.join(parts)


def state_to_string(state: State) -> str:
    return tiles_to_string(state.tiles, state.rows, state.cols)


def _default_goal(rows: int, cols: int) -> Tuple[int, ...]:
    """Deterministic default goal: first row is 1, the rest 0."""
    total = rows * cols
    goal = [0] * total
    for j in range(cols):
        goal[j] = 1
    return tuple(goal)


def _iter_moves(rows: int, cols: int) -> List[Tuple[str, int, int]]:
    moves = []
    for i in range(rows - 1):
        for j in range(cols - 1):
            moves.append(("CW", i, j))
            moves.append(("CCW", i, j))
    return moves


def _is_reverse(move: Tuple[str, int, int], prev_move: Optional[Tuple[str, int, int]]) -> bool:
    if not prev_move:
        return False
    dir_now, i_now, j_now = move
    dir_prev, i_prev, j_prev = prev_move
    if i_now != i_prev or j_now != j_prev:
        return False
    return (dir_now == "CW" and dir_prev == "CCW") or (dir_now == "CCW" and dir_prev == "CW")


def generate_puzzle(rows: int, cols: int, depth: int, rng: random.Random,
                    goal: Optional[Tuple[int, ...]] = None, max_tries: int = 5000):
    """
    Generate a start/goal pair where the optimal solution depth is exactly `depth`.

    Returns (start_state, goal_state, moves_used).
    """
    from algoritms import bfs  # local import to avoid circular dependency

    goal_tiles = tuple(goal) if goal is not None else _default_goal(rows, cols)
    goal_state = State(goal_tiles, rows, cols)
    moves = _iter_moves(rows, cols)

    for _ in range(max_tries):
        tiles = goal_tiles
        used_moves: List[Tuple[str, int, int]] = []
        prev_move: Optional[Tuple[str, int, int]] = None
        visited = {tiles}

        for _ in range(depth):
            candidates = [mv for mv in moves if not _is_reverse(mv, prev_move)]
            next_states = [(mv, apply_move(tiles, rows, cols, mv)) for mv in candidates]
            fresh = [(mv, t) for mv, t in next_states if t not in visited]
            mv, new_tiles = rng.choice(fresh if fresh else next_states)
            tiles = new_tiles
            used_moves.append(mv)
            prev_move = mv
            visited.add(tiles)

        start_state = State(tiles, rows, cols)
        stats = bfs(start_state, goal_tiles)
        opt_depth = len(stats.path) - 1 if stats.path else None
        if opt_depth == depth:
            return start_state, goal_state, used_moves

    raise RuntimeError(f"Failed to generate puzzle with depth={depth} in {max_tries} tries")
