#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Tuple, List, Optional, Callable
from collections import deque
import heapq

from game_logic import State


@dataclass
class Stats:
    iterations: int        # число итераций / развёртываний
    max_open: int          # макс. размер O
    open_end: int          # размер O при завершении
    max_memory: int        # макс. (O+C)
    time_s: float
    path: Optional[List[State]]
    heuristic_name: str = ""


def bfs(start: State, goal: Tuple[int, ...]) -> Stats:
    Q = deque([start])
    seen = {start.tiles}
    closed = set()
    it = 0
    mo = 1
    mm = 1

    while Q:
        s = Q.popleft()
        it += 1

        if s.tiles == goal:
            # O = Q, C = closed
            return Stats(it, mo, len(Q), max(mm, len(Q) + len(closed)), float(it), s.path())

        closed.add(s.tiles)

        for n in s.expand():
            if n.tiles not in seen and n.tiles not in closed:
                Q.append(n)
                seen.add(n.tiles)

        mo = max(mo, len(Q))
        mm = max(mm, len(Q) + len(closed))

    return Stats(it, mo, len(Q), mm, float(it), None)


def dfs(start: State, goal: Tuple[int, ...]) -> Stats:
    S = [start]
    seen = {start.tiles}
    closed = set()
    it = 0
    mo = 1
    mm = 1

    while S:
        s = S.pop()
        it += 1

        if s.tiles == goal:
            # O = S, C = closed
            return Stats(it, mo, len(S), max(mm, len(S) + len(closed)), float(it), s.path())

        closed.add(s.tiles)

        for n in reversed(s.expand()):
            if n.tiles not in closed and n.tiles not in seen:
                S.append(n)
                seen.add(n.tiles)

        mo = max(mo, len(S))
        mm = max(mm, len(S) + len(closed))

    return Stats(it, mo, len(S), mm, float(it), None)


def iddfs(start: State, goal: Tuple[int, ...], limit=20) -> Stats:
    total = 0
    mo = 1   # max size of "O" ~ текущий путь (стек)
    # max memory (O+C). Для DLS с проверкой по пути C как множества нет -> O
    mm = 1
    found = None

    def dls(node, d, lim, pathset):
        nonlocal total, mo, mm, found

        total += 1

        # O в глубинном ограниченном поиске можно трактовать как текущий стек/путь
        mo = max(mo, len(pathset))
        mm = max(mm, len(pathset))

        if node.tiles == goal:
            found = node
            return True

        if d == lim:
            return False

        for n in node.expand():
            if n.tiles in pathset:
                continue
            pathset.add(n.tiles)
            if dls(n, d + 1, lim, pathset):
                return True
            pathset.remove(n.tiles)

        return False

    for l in range(limit + 1):
        if dls(start, 0, l, {start.tiles}):
            # O при завершении (по методичке) для IDDFS можно считать 0, т.к. поиск завершён
            return Stats(total, mo, 0, mm, float(total), found.path())

    return Stats(total, mo, 0, mm, float(total), None)


# ---------------- A* ----------------

class HeuristicFunctions:
    @staticmethod
    def heuristic_h1(state: State, goal: Tuple[int, ...]) -> int:
        count = 0
        for i in range(len(state.tiles)):
            if state.tiles[i] != goal[i] and state.tiles[i] == 1:
                count += 1
        return count

    @staticmethod
    def heuristic_h2(state: State, goal: Tuple[int, ...]) -> int:
        """
        h2 - минимальная сумма манхэттенских расстояний (сопоставление одинаковых шариков),
        затем перевод в оценку ходов: ceil(total_dist / 4)
        """
        r, c = state.rows, state.cols

        cur = [(i // c, i % c) for i, v in enumerate(state.tiles) if v == 1]
        tgt = [(i // c, i % c) for i, v in enumerate(goal) if v == 1]

        k = len(cur)
        if k != len(tgt):
            return abs(k - len(tgt))
        if k == 0:
            return 0

        cost = [[abs(cur[i][0] - tgt[j][0]) + abs(cur[i][1] - tgt[j][1]) for j in range(k)]
                for i in range(k)]

        # Точное сопоставление DP по битмаске до 15 шариков
        if k <= 15:
            INF = 10**9
            dp = [INF] * (1 << k)
            dp[0] = 0
            for mask in range(1 << k):
                i = mask.bit_count()
                if i >= k:
                    continue
                base = dp[mask]
                if base >= INF:
                    continue
                for j in range(k):
                    if not (mask & (1 << j)):
                        nm = mask | (1 << j)
                        v = base + cost[i][j]
                        if v < dp[nm]:
                            dp[nm] = v
            total_dist = dp[(1 << k) - 1]
        else:
            used = [False] * k
            total_dist = 0
            for i in range(k):
                best_j = -1
                best = 10**9
                for j in range(k):
                    if not used[j] and cost[i][j] < best:
                        best = cost[i][j]
                        best_j = j
                used[best_j] = True
                total_dist += best

        return (total_dist + 3) // 4


def astar(start: State, goal: Tuple[int, ...],
          heuristic: Callable[[State, Tuple[int, ...]], int],
          heuristic_name: str = "Custom") -> Stats:
    # O: open_set, C: closed_set
    open_list = []  # heap: (f, counter, state)
    open_set = {start.tiles}
    closed_set = set()

    h_start = heuristic(start, goal)
    f_start = start.depth + h_start

    heapq.heappush(open_list, (f_start, 0, start))

    iterations = 0
    max_open = 1
    max_memory = 1
    counter = 1

    while open_list:
        f_val, _, current = heapq.heappop(open_list)
        open_set.discard(current.tiles)

        iterations += 1

        if current.tiles == goal:
            return Stats(
                iterations=iterations,
                max_open=max_open,
                # размер O на момент завершения
                open_end=len(open_set),
                max_memory=max_memory,
                time_s=float(iterations),
                path=current.path(),
                heuristic_name=heuristic_name
            )

        closed_set.add(current.tiles)

        for neighbor in current.expand():
            if neighbor.tiles in closed_set:
                continue

            g_neighbor = neighbor.depth
            h_neighbor = heuristic(neighbor, goal)
            f_neighbor = g_neighbor + h_neighbor

            if neighbor.tiles not in open_set:
                heapq.heappush(open_list, (f_neighbor, counter, neighbor))
                open_set.add(neighbor.tiles)
                counter += 1

        # Метрики по методичке: O и O+C считаем по множествам (уникальные узлы)
        max_open = max(max_open, len(open_set))
        max_memory = max(max_memory, len(open_set) + len(closed_set))

    return Stats(
        iterations=iterations,
        max_open=max_open,
        open_end=len(open_set),
        max_memory=max_memory,
        time_s=float(iterations),
        path=None,
        heuristic_name=heuristic_name
    )


def astar_h1(start: State, goal: Tuple[int, ...]) -> Stats:
    return astar(start, goal, HeuristicFunctions.heuristic_h1,
                 "A*(h1) - Misplaced Tiles")


def astar_h2(start: State, goal: Tuple[int, ...]) -> Stats:
    return astar(start, goal, HeuristicFunctions.heuristic_h2,
                 "A*(h2) - Manhattan Distance")
