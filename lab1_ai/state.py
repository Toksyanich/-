# state.py

import copy


class State:
    """
    Класс для представления состояния головоломки "Повороты шариков".
    """

    def __init__(self, board, parent=None, move=None):
        # Используем кортежи для неизменяемости и хеширования
        self.board = tuple(map(tuple, board))
        self.parent = parent
        self.move = move
        self.rows = len(board)
        self.cols = len(board[0])

    def __eq__(self, other):
        """Проверка на равенство состояний."""
        return self.board == other.board

    def __hash__(self):
        """Хеш состояния, необходим для хранения в множестве (set)."""
        return hash(self.board)

    def get_successors(self):
        """
        Генерирует все возможные дочерние состояния из текущего.
        Возвращает список объектов State.
        """
        successors = []
        # Итерируемся по всем возможным левым верхним углам квадрата 2x2
        for r in range(self.rows - 1):
            for c in range(self.cols - 1):
                # Поворот по часовой стрелке (CW)
                new_board_cw = [list(row) for row in self.board]
                temp = new_board_cw[r][c]
                new_board_cw[r][c] = new_board_cw[r+1][c]
                new_board_cw[r+1][c] = new_board_cw[r+1][c+1]
                new_board_cw[r+1][c+1] = new_board_cw[r][c+1]
                new_board_cw[r][c+1] = temp
                move_desc_cw = f"Поворот 2x2 в ({r},{c}) ПЧС"
                successors.append(
                    State(new_board_cw, parent=self, move=move_desc_cw))

                # Поворот против часовой стрелки (CCW)
                new_board_ccw = [list(row) for row in self.board]
                temp = new_board_ccw[r][c]
                new_board_ccw[r][c] = new_board_ccw[r][c+1]
                new_board_ccw[r][c+1] = new_board_ccw[r+1][c+1]
                new_board_ccw[r+1][c+1] = new_board_ccw[r+1][c]
                new_board_ccw[r+1][c] = temp
                move_desc_ccw = f"Поворот 2x2 в ({r},{c}) ППЧС"
                successors.append(
                    State(new_board_ccw, parent=self, move=move_desc_ccw))

        return successors
