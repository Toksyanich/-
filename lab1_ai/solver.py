# solver.py

from collections import deque
from state import State


def solve(start_state, goal_state, method='bfs'):
    """
    Решает головоломку с использованием BFS или DFS.

    :param start_state: Начальное состояние (объект State)
    :param goal_state: Целевое состояние (объект State)
    :param method: 'bfs' (поиск в ширину) или 'dfs' (поиск в глубину)
    :return: (путь, статистика) или (None, статистика) если путь не найден
    """
    # Структуры данных для поиска
    if method == 'bfs':
        open_list = deque([start_state])  # Очередь для BFS
    elif method == 'dfs':
        open_list = [start_state]  # Стек для DFS
    else:
        raise ValueError(
            "Неизвестный метод поиска. Используйте 'bfs' или 'dfs'.")

    closed_set = set()

    # Статистика
    iterations = 0
    max_open_list_size = 0
    max_closed_list_size = 0

    while open_list:
        iterations += 1

        # Обновление статистики
        if len(open_list) > max_open_list_size:
            max_open_list_size = len(open_list)
        if len(closed_set) > max_closed_list_size:
            max_closed_list_size = len(closed_set)

        # Получаем узел для раскрытия
        if method == 'bfs':
            current_state = open_list.popleft()
        else:  # dfs
            current_state = open_list.pop()

        # Проверка на цель
        if current_state == goal_state:
            # Восстанавливаем путь
            path = []
            temp = current_state
            while temp is not None:
                path.append(temp)
                temp = temp.parent
            path.reverse()

            stats = {
                "iterations": iterations,
                "max_open_list": max_open_list_size,
                "final_open_list": len(open_list),
                "max_memory_nodes": max_open_list_size + max_closed_list_size
            }
            return path, stats

        closed_set.add(current_state)

        # Раскрываем узел
        successors = current_state.get_successors()
        for successor in successors:
            if successor not in closed_set:
                # Проверим, нет ли уже такого состояния в open_list (для оптимизации)
                # В простом варианте можно не проверять, но это может увеличить память
                # Для BFS это не нужно, для DFS может предотвратить циклы на небесконечных графах
                if successor not in open_list:
                    open_list.append(successor)

    # Решение не найдено
    stats = {
        "iterations": iterations,
        "max_open_list": max_open_list_size,
        "final_open_list": len(open_list),
        "max_memory_nodes": max_open_list_size + max_closed_list_size
    }
    return None, stats
