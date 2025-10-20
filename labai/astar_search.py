#!/usr/bin/env python3
"""
A* Search Algorithm Implementation for Lab 3
Два варианта эвристических функций для головоломки с шариками
"""

import heapq
from dataclasses import dataclass
from typing import Tuple, List, Optional, Callable


class State:
    def __init__(self, tiles: Tuple[int, ...], rows: int, cols: int,
                 parent=None, move=None, depth=0):
        self.tiles = tiles
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


@dataclass
class Stats:
    iterations: int
    max_open: int
    open_end: int
    max_memory: int
    time_s: float
    path: Optional[List[State]]
    heuristic_name: str = ""


class HeuristicFunctions:
    """Класс с эвристическими функциями для A*"""

    @staticmethod
    def heuristic_h1(state: State, goal: Tuple[int, ...]) -> int:
        """
        h1 - Количество шариков не в целевой позиции (Misplaced Tiles)
        Это допустимая эвристика для нашей задачи.
        Сложность: O(n)
        """
        count = 0
        for i in range(len(state.tiles)):
            if state.tiles[i] != goal[i] and state.tiles[i] == 1:
                count += 1
        return count

    @staticmethod
    def heuristic_h2(state: State, goal: Tuple[int, ...]) -> int:
        """
        h2 - Сумма манхэттенских расстояний шариков от целевых позиций
        (Manhattan Distance / Sum of distances)
        Это также допустимая эвристика.
        Сложность: O(n)
        """
        total_distance = 0
        r, c = state.rows, state.cols

        # Находим целевые позиции шариков
        goal_positions = {}
        for i in range(len(goal)):
            if goal[i] == 1:
                goal_positions[i] = (i // c, i % c)

        # Для каждого шарика в текущем состоянии
        for i in range(len(state.tiles)):
            if state.tiles[i] == 1:
                curr_pos = (i // c, i % c)
                # Находим соответствующую целевую позицию
                if i in goal_positions:
                    target_pos = goal_positions[i]
                    dist = abs(curr_pos[0] - target_pos[0]) + \
                        abs(curr_pos[1] - target_pos[1])
                    total_distance += dist

        return total_distance


def astar(start: State, goal: Tuple[int, ...],
          heuristic: Callable[[State, Tuple[int, ...]], int],
          heuristic_name: str = "Custom") -> Stats:
    """
    Алгоритм A*
    f(n) = g(n) + h(n), где:
        g(n) = стоимость пути от стартового узла (depth)
        h(n) = эвристическая оценка расстояния до цели
        f(n) = общая оценка

    Args:
        start: Начальное состояние
        goal: Целевое состояние (кортеж)
        heuristic: Функция эвристики h(n)
        heuristic_name: Название эвристики для статистики

    Returns:
        Статистика поиска
    """
    open_list = []  # Приоритетная очередь: (f_value, counter, state)
    open_set = {start.tiles}
    closed_set = set()

    h_start = heuristic(start, goal)
    f_start = start.depth + h_start

    heapq.heappush(open_list, (f_start, 0, start))

    iterations = 0
    max_open = 1
    max_memory = 1
    counter = 1  # Для разрешения конфликтов при одинаковых f-значениях

    while open_list:
        f_val, _, current = heapq.heappop(open_list)
        open_set.discard(current.tiles)

        iterations += 1

        # Проверка цели
        if current.tiles == goal:
            return Stats(
                iterations=iterations,
                max_open=max_open,
                open_end=len(open_list),
                max_memory=max_memory,
                time_s=float(iterations),
                path=current.path(),
                heuristic_name=heuristic_name
            )

        closed_set.add(current.tiles)

        # Раскрытие узла
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

        current_open_size = len(open_list)
        max_open = max(max_open, current_open_size)
        max_memory = max(max_memory, len(open_set) + len(closed_set))

    return Stats(
        iterations=iterations,
        max_open=max_open,
        open_end=len(open_list),
        max_memory=max_memory,
        time_s=float(iterations),
        path=None,
        heuristic_name=heuristic_name
    )


def astar_h1(start: State, goal: Tuple[int, ...]) -> Stats:
    """A* с эвристикой h1 (Misplaced Tiles - количество неправильных шариков)"""
    return astar(start, goal, HeuristicFunctions.heuristic_h1,
                 "A*(h1) - Misplaced Tiles")


def astar_h2(start: State, goal: Tuple[int, ...]) -> Stats:
    """A* с эвристикой h2 (Manhattan Distance - сумма расстояний)"""
    return astar(start, goal, HeuristicFunctions.heuristic_h2,
                 "A*(h2) - Manhattan Distance")
