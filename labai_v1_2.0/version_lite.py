import tkinter as tk
from collections import deque
import threading
import time
import random

# ------------------- Модель состояния -------------------


class State:
    def __init__(self, board, parent=None, move=None):
        # board — двумерный список или кортеж 2x2
        self.board = tuple(tuple(row) for row in board)
        self.parent = parent
        self.move = move  # 'CW' или 'CCW'

    def __hash__(self):
        return hash(self.board)

    def __eq__(self, other):
        return isinstance(other, State) and self.board == other.board

    def successors(self):
        # Для 2x2 поля возможен только один квадрат 2x2
        b = [list(row) for row in self.board]
        # вращение по часовой
        cw = [row[:] for row in b]
        cw[0][0], cw[0][1], cw[1][1], cw[1][0] = b[1][0], b[0][0], b[0][1], b[1][1]
        yield State(cw, self, 'CW')
        # вращение против часовой
        ccw = [row[:] for row in b]
        ccw[0][0], ccw[0][1], ccw[1][1], ccw[1][0] = b[0][1], b[1][1], b[1][0], b[0][0]
        yield State(ccw, self, 'CCW')

# ------------------- Поисковые алгоритмы -------------------


def bfs_search(start, goal):
    frontier = deque([start])
    explored = set([start])
    iterations = 0
    max_open = 1
    max_mem = 1
    while frontier:
        iterations += 1
        current = frontier.popleft()
        if current.board == goal.board:
            return current, iterations, max_open, max_mem
        for succ in current.successors():
            if succ not in explored:
                explored.add(succ)
                frontier.append(succ)
        max_open = max(max_open, len(frontier))
        max_mem = max(max_mem, len(frontier) + len(explored))
    return None, iterations, max_open, max_mem


def dfs_search(start, goal, max_depth=50):
    stack = [(start, 0)]
    explored = set([start])
    iterations = 0
    max_open = 1
    max_mem = 1
    while stack:
        iterations += 1
        current, depth = stack.pop()
        if current.board == goal.board:
            return current, iterations, max_open, max_mem
        if depth < max_depth:
            for succ in current.successors():
                if succ not in explored:
                    explored.add(succ)
                    stack.append((succ, depth + 1))
        max_open = max(max_open, len(stack))
        max_mem = max(max_mem, len(stack) + len(explored))
    return None, iterations, max_open, max_mem


def reconstruct_path(goal_node):
    # Возвращает список состояний (как 2D списки) от начала до цели
    if goal_node is None:
        return []
    path_nodes = []
    node = goal_node
    while node is not None:
        # преобразуем tuple->list
        path_nodes.append([list(row) for row in node.board])
        node = node.parent
    path_nodes.reverse()
    return path_nodes

# ------------------- GUI -------------------


class PuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Повороты шариков 2x2 — BFS/DFS")
        self.size = 2
        self.start_board = [[1, 2], [3, 4]]
        self.goal_board = [[1, 2], [3, 4]]
        self.running = False
        self.algorithm = tk.StringVar(value="BFS")

        # анимация
        self.solution_path = []  # список досок (2D list)
        self.current_step = 0
        self.playing = False
        self.animation_ms = tk.IntVar(value=500)

        self._build_ui()

    def _build_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=8, pady=8)

        tk.Label(frame, text="Начальное состояние").grid(row=0, column=0)
        tk.Label(frame, text="Целевое состояние").grid(row=0, column=1)

        self.start_canvas = self._make_canvas(
            frame, 1, 0, self.start_board, editable=True)
        self.goal_canvas = self._make_canvas(
            frame, 1, 1, self.goal_board, editable=False)

        ctrl = tk.Frame(self.root)
        ctrl.pack(pady=6)
        tk.Button(ctrl, text="Случайные состояния",
                  command=self.random_boards).grid(row=0, column=0, padx=4)
        tk.Radiobutton(ctrl, text="BFS", variable=self.algorithm,
                       value="BFS").grid(row=0, column=1)
        tk.Radiobutton(ctrl, text="DFS", variable=self.algorithm,
                       value="DFS").grid(row=0, column=2)
        tk.Button(ctrl, text="Запустить поиск", command=self.run_search).grid(
            row=0, column=3, padx=6)

        # анимационные кнопки
        anim = tk.Frame(self.root)
        anim.pack(pady=4)
        tk.Button(anim, text="Показать шаг", command=self.show_next_step).grid(
            row=0, column=0, padx=4)
        tk.Button(anim, text="Авто (Play)", command=self.play_solution).grid(
            row=0, column=1, padx=4)
        tk.Button(anim, text="Стоп анимацию", command=self.stop_animation).grid(
            row=0, column=2, padx=4)
        tk.Label(anim, text="Скорость (мс):").grid(row=0, column=3)
        tk.Entry(anim, textvariable=self.animation_ms,
                 width=6).grid(row=0, column=4, padx=4)

        self.stats_label = tk.Label(self.root, text="")
        self.stats_label.pack(pady=6)

    def _make_canvas(self, parent, r, c, board, editable):
        canvas = tk.Canvas(parent, width=140, height=140, bg="white")
        canvas.grid(row=r, column=c, padx=10, pady=10)
        self._draw_board_on_canvas(canvas, board)
        if editable:
            canvas.bind("<Button-1>", lambda e: self.click_cell(e, board))
        return canvas

    def _draw_board_on_canvas(self, canvas, board):
        canvas.delete("all")
        cell = 60
        for i in range(self.size):
            for j in range(self.size):
                x0, y0 = j*cell, i*cell
                canvas.create_rectangle(
                    x0, y0, x0+cell, y0+cell, outline="black", fill="lightblue")
                canvas.create_text(x0+cell/2, y0+cell/2,
                                   text=str(board[i][j]), font=("Arial", 20))

    def redraw(self):
        # Если идёт анимация, рисуем текущую доску из solution_path
        if self.solution_path and 0 <= self.current_step < len(self.solution_path):
            board_to_draw = self.solution_path[self.current_step]
        else:
            board_to_draw = self.start_board
        self._draw_board_on_canvas(self.start_canvas, board_to_draw)
        self._draw_board_on_canvas(self.goal_canvas, self.goal_board)

    def click_cell(self, event, board):
        j = event.x // 60
        i = event.y // 60
        max_val = self.size*self.size
        board[i][j] = (board[i][j] % max_val) + 1
        # при ручном редактировании отменяем предыдущий найденный путь
        self.solution_path = []
        self.current_step = 0
        self.redraw()

    def random_boards(self):
        nums = [1, 2, 3, 4]
        random.shuffle(nums)
        self.start_board = [nums[:2], nums[2:]]
        random.shuffle(nums)
        self.goal_board = [nums[:2], nums[2:]]
        self.solution_path = []
        self.current_step = 0
        self.redraw()

    def run_search(self):
        if self.running:
            return
        self.running = True
        self.stats_label.config(text="Поиск...")
        threading.Thread(target=self._search_thread, daemon=True).start()

    def _search_thread(self):
        start = State(self.start_board)
        goal = State(self.goal_board)
        t0 = time.time()
        if self.algorithm.get() == "BFS":
            result, iterations, max_open, max_mem = bfs_search(start, goal)
        else:
            result, iterations, max_open, max_mem = dfs_search(start, goal)
        dt = time.time() - t0
        path = reconstruct_path(result)
        # обновляем UI в основном потоке
        self.root.after(0, lambda: self.on_search_done(
            path, iterations, max_open, max_mem, dt))
        self.running = False

    def on_search_done(self, path, iterations, max_open, max_mem, dt):
        if not path:
            self.stats_label.config(
                text=f"Решение не найдено за {iterations} итераций")
            return
        self.solution_path = path
        self.current_step = 0
        self.redraw()
        stats = f"Решено ({self.algorithm.get()}) за {iterations} итераций, путь: {len(path)-1} шагов, макс O={max_open}, макс память={max_mem}, время {dt:.3f}s"
        self.stats_label.config(text=stats)

    # ----------------- Анимация -----------------
    def show_next_step(self):
        if not self.solution_path:
            self.stats_label.config(
                text="Сначала выполните поиск и найдите решение.")
            return
        if self.current_step < len(self.solution_path)-1:
            self.current_step += 1
            self.redraw()
        else:
            self.stats_label.config(text="Достигнуто целевое состояние.")

    def play_solution(self):
        if not self.solution_path:
            self.stats_label.config(
                text="Сначала выполните поиск и найдите решение.")
            return
        if self.playing:
            return
        self.playing = True
        self._play_loop()

    def _play_loop(self):
        if not self.playing:
            return
        if self.current_step < len(self.solution_path)-1:
            self.current_step += 1
            self.redraw()
            ms = max(10, self.animation_ms.get())
            self.root.after(ms, self._play_loop)
        else:
            self.playing = False
            self.stats_label.config(text="Анимация завершена.")

    def stop_animation(self):
        self.playing = False


if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.mainloop()
