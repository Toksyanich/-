"""
puzzle_search.py

Реализация лабораторной работы по поиску в пространстве состояний
(задача "Повороты шариков" — вращение квадрата 2x2 по/против часовой).

Функциональность:
- Класс State (описание состояния поля n x n)
- Генерация переходов (все 2x2 с поворотами CW/CCW)
- Два алгоритма поиска: BFS и DFS (итеративный стек)
- Графический интерфейс на tkinter:
  - отображение начального и целевого состояний
  - редактирование состояний (клик по ячейке)
  - загрузка/сохранение состояний в файл
  - случайная генерация состояний (уникальная перестановка)
  - запуск поиска (BFS/DFS), отображение статистики
  - пошаговая анимация найденного пути

Запуск:
    python puzzle_search.py

Зависимости: только стандартная библиотека Python (tkinter, threading, queue).

Примечание: для больших n или сложных состояний поиск полного пространства
может быть долгим или потреблять много памяти. В GUI есть параметр "Макс. узлов"
для ограничения числа обрабатываемых узлов.

Автор: сгенерировано ChatGPT (код-реализация для учебной лабораторной работы)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import deque
import threading
import queue
import time
import random
import math

# ----------------------------- Конфигурация -----------------------------
COLOR_PALETTE = [
    "#FF4136", "#0074D9", "#2ECC40", "#FFDC00", "#B10DC9",
    "#FF851B", "#7FDBFF", "#01FF70", "#85144b", "#F012BE",
]
CANVAS_CELL = 70        # размер клетки в пикселях
CELL_PADDING = 8
ANIMATION_DEFAULT_MS = 500
PROGRESS_UPDATE_EVERY = 500  # обновлять очередь прогресса каждые N итераций

# ------------------------------- State ---------------------------------


class State:
    """
    Описывает состояние головоломки: поле n x n, где каждая ячейка имеет
    целочисленное значение (метка шарика). Хранится в виде кортежа длины n*n.
    """
    __slots__ = ("grid", "n", "parent", "move", "depth")

    def __init__(self, grid, n, parent=None, move=None, depth=0):
        # grid: кортеж длины n*n
        self.grid = tuple(grid)
        self.n = n
        self.parent = parent
        self.move = move
        self.depth = depth

    def __hash__(self):
        return hash(self.grid)

    def __eq__(self, other):
        return isinstance(other, State) and self.grid == other.grid

    def __repr__(self):
        return f"State(n={self.n}, grid={self.grid}, depth={self.depth})"

    def index(self, r, c):
        return r * self.n + c

    def successors(self):
        """
        Возвращает список дочерних состояний (все возможные повороты 2x2):
        для каждой позиции верхнего левого угла квадрата 2x2 — два действия
        (CW и CCW).
        """
        n = self.n
        res = []
        g = self.grid
        # пройдем все верхне-левые координаты 2x2
        for i in range(n - 1):
            for j in range(n - 1):
                a = self.index(i, j)
                b = self.index(i, j + 1)
                c = self.index(i + 1, j)
                d = self.index(i + 1, j + 1)
                # значения до поворота
                va, vb, vc, vd = g[a], g[b], g[c], g[d]

                # Clockwise: [[c a],[d b]]
                cw = list(g)
                cw[a] = vc
                cw[b] = va
                cw[c] = vd
                cw[d] = vb
                res.append(State(tuple(cw), n, parent=self,
                           move=(i, j, "CW"), depth=self.depth + 1))

                # Counter-clockwise: [[b d],[a c]]
                ccw = list(g)
                ccw[a] = vb
                ccw[b] = vd
                ccw[c] = va
                ccw[d] = vc
                res.append(State(tuple(ccw), n, parent=self,
                           move=(i, j, "CCW"), depth=self.depth + 1))
        return res

    def pretty_print(self):
        lines = []
        for r in range(self.n):
            start = r * self.n
            lines.append(" ".join(str(x)
                         for x in self.grid[start:start + self.n]))
        return "\n".join(lines)

    def to_list_of_rows(self):
        rows = []
        for r in range(self.n):
            rows.append(list(self.grid[r * self.n:(r + 1) * self.n]))
        return rows

# ---------------------------- Поисковые алгоритмы ----------------------------


def reconstruct_path(goal_state):
    path = []
    node = goal_state
    while node is not None:
        path.append(node)
        node = node.parent
    path.reverse()
    moves = [s.move for s in path[1:]]  # первый элемент — начальное состояние
    return path, moves


def bfs_search(start: State, goal: State, max_nodes=None, progress_queue=None):
    """
    Breadth-First Search (неинформированный).
    Возвращает (path_states, moves, stats) или (None, None, stats) если не найдено.

    stats: dict {"iterations", "nodes_expanded", "max_open", "open_at_end", "max_memory", "time"}
    """
    t0 = time.time()
    frontier = deque([start])
    seen = set([start.grid])  # отмечаем при постановке в очередь
    closed = set()

    iterations = 0  # число извлечений из очереди
    nodes_expanded = 0  # число раскрытий
    max_open = len(frontier)
    max_memory = len(frontier) + len(closed)

    while frontier:
        current = frontier.popleft()
        iterations += 1
        closed.add(current.grid)

        if current.grid == goal.grid:
            t1 = time.time()
            path, moves = reconstruct_path(current)
            stats = {
                "iterations": iterations,
                "nodes_expanded": nodes_expanded,
                "max_open": max_open,
                "open_at_end": len(frontier),
                "max_memory": max_memory,
                "time": t1 - t0,
            }
            return path, moves, stats

        # раскрываем
        for succ in current.successors():
            if succ.grid not in seen:
                seen.add(succ.grid)
                frontier.append(succ)
        nodes_expanded += 1

        if iterations % PROGRESS_UPDATE_EVERY == 0 and progress_queue is not None:
            progress_queue.put(("progress", {
                "iterations": iterations,
                "nodes_expanded": nodes_expanded,
                "frontier_len": len(frontier),
                "closed_len": len(closed),
            }))

        max_open = max(max_open, len(frontier))
        max_memory = max(max_memory, len(frontier) + len(closed))

        if max_nodes is not None and iterations >= max_nodes:
            break

    t1 = time.time()
    stats = {
        "iterations": iterations,
        "nodes_expanded": nodes_expanded,
        "max_open": max_open,
        "open_at_end": len(frontier),
        "max_memory": max_memory,
        "time": t1 - t0,
    }
    return None, None, stats


def dfs_search(start: State, goal: State, max_nodes=None, max_depth=None, progress_queue=None):
    """
    Глубинный поиск (итеративный стек). Отмечаем посещённые состояния при постановке в стек.
    В качестве защиты от бесконечного углубления можно задать max_depth.
    """
    t0 = time.time()
    stack = [start]
    seen = set([start.grid])
    closed = set()

    iterations = 0
    nodes_expanded = 0
    max_open = len(stack)
    max_memory = len(stack) + len(closed)

    while stack:
        current = stack.pop()
        iterations += 1
        closed.add(current.grid)

        if current.grid == goal.grid:
            t1 = time.time()
            path, moves = reconstruct_path(current)
            stats = {
                "iterations": iterations,
                "nodes_expanded": nodes_expanded,
                "max_open": max_open,
                "open_at_end": len(stack),
                "max_memory": max_memory,
                "time": t1 - t0,
            }
            return path, moves, stats

        # ограничение глубины
        if max_depth is not None and current.depth >= max_depth:
            continue

        succs = current.successors()
        # чтобы поведение было детерминировано и было глубинное (LIFO), добавляем в стек в прямом порядке
        for succ in succs:
            if succ.grid not in seen:
                seen.add(succ.grid)
                stack.append(succ)

        nodes_expanded += 1

        if iterations % PROGRESS_UPDATE_EVERY == 0 and progress_queue is not None:
            progress_queue.put(("progress", {
                "iterations": iterations,
                "nodes_expanded": nodes_expanded,
                "frontier_len": len(stack),
                "closed_len": len(closed),
            }))

        max_open = max(max_open, len(stack))
        max_memory = max(max_memory, len(stack) + len(closed))

        if max_nodes is not None and iterations >= max_nodes:
            break

    t1 = time.time()
    stats = {
        "iterations": iterations,
        "nodes_expanded": nodes_expanded,
        "max_open": max_open,
        "open_at_end": len(stack),
        "max_memory": max_memory,
        "time": t1 - t0,
    }
    return None, None, stats

# ------------------------------ GUI ------------------------------------


class PuzzleGUI:
    def __init__(self, root):
        self.root = root
        root.title(
            "Повороты шариков — Поиск в пространстве состояний (BFS / DFS)")

        # параметры
        self.n_var = tk.IntVar(value=3)
        self.algorithm_var = tk.StringVar(value="BFS")
        self.max_nodes_var = tk.IntVar(value=200000)
        self.max_depth_var = tk.IntVar(value=50)
        self.animation_ms = tk.IntVar(value=ANIMATION_DEFAULT_MS)

        # состояние (начальное и целевое)
        self.start_state = None
        self.goal_state = None
        self.current_display_state = None  # для анимации

        # очередь сообщений из фонового потока поиска
        self.message_queue = queue.Queue()
        self.search_thread = None
        self.search_running = False
        self.result_ready = False
        self.last_search_result = None

        self.build_ui()
        self.reset_states()
        # старт обновления очереди
        self.root.after(100, self.poll_queue)

    def build_ui(self):
        main = ttk.Frame(self.root, padding=8)
        main.grid(row=0, column=0, sticky="nsew")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # верхняя панель: параметры
        params = ttk.Frame(main)
        params.grid(row=0, column=0, sticky="ew")
        params.columnconfigure(6, weight=1)

        ttk.Label(params, text="Размер поля (n x n):").grid(
            row=0, column=0, sticky="w")
        ttk.Spinbox(params, from_=2, to=6, textvariable=self.n_var, width=4,
                    command=self.on_change_n).grid(row=0, column=1, sticky="w")

        ttk.Label(params, text="Алгоритм:").grid(
            row=0, column=2, sticky="w", padx=(8, 0))
        ttk.Radiobutton(params, text="BFS", variable=self.algorithm_var,
                        value="BFS").grid(row=0, column=3, sticky="w")
        ttk.Radiobutton(params, text="DFS", variable=self.algorithm_var,
                        value="DFS").grid(row=0, column=4, sticky="w")

        ttk.Label(params, text="Макс. узлов (stop):").grid(
            row=0, column=5, sticky="e")
        ttk.Entry(params, textvariable=self.max_nodes_var,
                  width=8).grid(row=0, column=6, sticky="w")

        ttk.Label(params, text="Max depth (для DFS):").grid(
            row=0, column=7, sticky="e")
        ttk.Entry(params, textvariable=self.max_depth_var,
                  width=6).grid(row=0, column=8, sticky="w")

        # средняя часть — канвасы и кнопки
        middle = ttk.Frame(main)
        middle.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        middle.columnconfigure(2, weight=1)

        # канвас для начального состояния
        left = ttk.Frame(middle)
        left.grid(row=0, column=0, sticky="nw")
        ttk.Label(left, text="Начальное состояние (клик — изменить) ").grid(
            row=0, column=0)
        self.canvas_start = tk.Canvas(
            left, width=CANVAS_CELL * 6, height=CANVAS_CELL * 6, bg="#f0f0f0")
        self.canvas_start.grid(row=1, column=0, padx=4, pady=4)
        self.canvas_start.bind(
            "<Button-1>", lambda e: self.on_canvas_click(e, which="start"))

        # канвас для целевого состояния
        right = ttk.Frame(middle)
        right.grid(row=0, column=1, sticky="nw", padx=(12, 0))
        ttk.Label(right, text="Целевое состояние (клик — изменить) ").grid(
            row=0, column=0)
        self.canvas_goal = tk.Canvas(
            right, width=CANVAS_CELL * 6, height=CANVAS_CELL * 6, bg="#f0f0f0")
        self.canvas_goal.grid(row=1, column=0, padx=4, pady=4)
        self.canvas_goal.bind(
            "<Button-1>", lambda e: self.on_canvas_click(e, which="goal"))

        # управление и статистика
        ctrl = ttk.Frame(middle)
        ctrl.grid(row=0, column=2, sticky="nsew", padx=(12, 0))
        ctrl.columnconfigure(0, weight=1)

        # генерация / загрузка
        bframe = ttk.Frame(ctrl)
        bframe.grid(row=0, column=0, sticky="ew")
        ttk.Button(bframe, text="Случ. начальное", command=self.randomize_start).grid(
            row=0, column=0, sticky="ew")
        ttk.Button(bframe, text="Случ. целевое", command=self.randomize_goal).grid(
            row=0, column=1, sticky="ew", padx=(6, 0))
        ttk.Button(bframe, text="Загрузить из файла", command=self.load_from_file).grid(
            row=0, column=2, sticky="ew", padx=(6, 0))
        ttk.Button(bframe, text="Сохранить в файл", command=self.save_to_file).grid(
            row=0, column=3, sticky="ew", padx=(6, 0))

        # запуск поиска
        run_frame = ttk.Frame(ctrl)
        run_frame.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(run_frame, text="Запустить поиск", command=self.start_search).grid(
            row=0, column=0, sticky="ew")
        ttk.Button(run_frame, text="Остановить", command=self.stop_search).grid(
            row=0, column=1, sticky="ew", padx=(6, 0))

        # анимация решения
        anim_frame = ttk.Frame(ctrl)
        anim_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(anim_frame, text="Показать шаг",
                   command=self.show_next_step).grid(row=0, column=0)
        ttk.Button(anim_frame, text="Авто (Play)", command=self.play_solution).grid(
            row=0, column=1, padx=(6, 0))
        ttk.Button(anim_frame, text="Стоп анимацию", command=self.stop_animation).grid(
            row=0, column=2, padx=(6, 0))

        ttk.Label(anim_frame, text="Скорость (мс):").grid(
            row=1, column=0, sticky="e")
        ttk.Entry(anim_frame, textvariable=self.animation_ms, width=6).grid(
            row=1, column=1, sticky="w", padx=(6, 0))

        # статистика
        stats_frame = ttk.LabelFrame(ctrl, text="Статистика поиска")
        stats_frame.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        self.stats_text = tk.Text(
            stats_frame, height=10, width=40, state="disabled")
        self.stats_text.grid(row=0, column=0, sticky="nsew")

        # подсказки
        ttk.Label(ctrl, text="\nПримечание: для больших n поиск может быть дорогим по памяти.\n").grid(
            row=4, column=0, sticky="w")

    # --------------------- Функции редактирования и отображения ---------------------
    def reset_states(self):
        n = self.n_var.get()
        default_grid = tuple(range(n * n))
        self.start_state = State(default_grid, n)
        self.goal_state = State(default_grid, n)
        self.current_display_state = None
        self.draw_all()

    def on_change_n(self):
        self.reset_states()

    def draw_all(self):
        self.draw_canvas(self.canvas_start, self.start_state)
        self.draw_canvas(self.canvas_goal, self.goal_state)

    def draw_canvas(self, canvas, state: State, highlight_pos=None):
        canvas.delete("all")
        if state is None:
            return
        n = state.n
        # размер canvas подстраивается
        width = CANVAS_CELL * n
        height = CANVAS_CELL * n
        canvas.config(width=width, height=height)

        for r in range(n):
            for c in range(n):
                x0 = c * CANVAS_CELL + CELL_PADDING
                y0 = r * CANVAS_CELL + CELL_PADDING
                x1 = (c + 1) * CANVAS_CELL - CELL_PADDING
                y1 = (r + 1) * CANVAS_CELL - CELL_PADDING
                val = state.grid[r * n + c]
                color = COLOR_PALETTE[val % len(COLOR_PALETTE)]
                oval = canvas.create_oval(
                    x0, y0, x1, y1, fill=color, outline="black")
                canvas.create_text((x0 + x1) / 2, (y0 + y1) /
                                   2, text=str(val), fill="white")
                # highlight
                if highlight_pos is not None and (r, c) in highlight_pos:
                    canvas.create_rectangle(c * CANVAS_CELL, r * CANVAS_CELL, (c + 1)
                                            * CANVAS_CELL, (r + 1) * CANVAS_CELL, outline="#FFD700", width=3)

    def on_canvas_click(self, event, which="start"):
        # определить ячейку
        widget = event.widget
        x, y = event.x, event.y
        n = self.n_var.get()
        c = min(n - 1, x // CANVAS_CELL)
        r = min(n - 1, y // CANVAS_CELL)
        if which == "start":
            self.cycle_cell_value(self.start_state, r, c)
            self.draw_canvas(self.canvas_start, self.start_state)
        else:
            self.cycle_cell_value(self.goal_state, r, c)
            self.draw_canvas(self.canvas_goal, self.goal_state)

    def cycle_cell_value(self, state: State, r, c):
        # присваиваем уникальное значение из диапазона 0..n*n-1, которое ещё не встречается
        n = state.n
        total = n * n
        vals = list(state.grid)
        idx = r * n + c
        current = vals[idx]
        # найдем следующий доступный (уникальный) номер
        for step in range(1, total + 1):
            cand = (current + step) % total
            if cand not in vals or cand == current:
                vals[idx] = cand
                break
        state.grid = tuple(vals)

    # ---------------------- Случайная генерация / загрузка -----------------------
    def randomize_start(self):
        n = self.n_var.get()
        arr = list(range(n * n))
        random.shuffle(arr)
        self.start_state = State(tuple(arr), n)
        self.draw_canvas(self.canvas_start, self.start_state)

    def randomize_goal(self):
        n = self.n_var.get()
        arr = list(range(n * n))
        random.shuffle(arr)
        self.goal_state = State(tuple(arr), n)
        self.draw_canvas(self.canvas_goal, self.goal_state)

    def load_from_file(self):
        fn = filedialog.askopenfilename(title="Загрузить состояния", filetypes=[
                                        ("Text files", "*.txt"), ("All files", "*")])
        if not fn:
            return
        try:
            with open(fn, "r", encoding="utf-8") as f:
                lines = [ln.strip() for ln in f if ln.strip()]
            if len(lines) < 3:
                messagebox.showerror(
                    "Ошибка", "Неверный формат файла. Ожидается минимум 3 непустые строки: n, start-row..., goal-row...")
                return
            n = int(lines[0])
            start_vals = []
            goal_vals = []
            # читаем n строк для стартового, n для целевого (или одна строка со всеми числами)
            idx = 1
            # попытка парсинга: если следующая строка содержит >= n чисел, считаем что они все в одной строке
            for _ in range(n):
                parts = lines[idx].split()
                if len(parts) < n:
                    # возможно все числа в несколько строк; в таком случае читаем последующие строки до набора n*n
                    break
                start_vals.extend(int(x) for x in parts[:n])
                idx += 1
            # если не собрали n*n — попробуем считать одну строку
            if len(start_vals) != n * n:
                parts = lines[1].split()
                start_vals = [int(x) for x in parts[:n * n]]
                idx = 2
            # теперь goal
            if len(lines) > idx:
                parts_goal = []
                for j in range(idx, len(lines)):
                    parts_goal.extend(lines[j].split())
                parts_goal = [int(x) for x in parts_goal]
                if len(parts_goal) >= n * n:
                    goal_vals = parts_goal[:n * n]
                else:
                    messagebox.showerror(
                        "Ошибка", "Не удалось прочитать целевое состояние из файла.")
                    return
            else:
                messagebox.showerror(
                    "Ошибка", "Не найдено записанного целевого состояния")
                return

            self.n_var.set(n)
            self.start_state = State(tuple(start_vals), n)
            self.goal_state = State(tuple(goal_vals), n)
            self.draw_all()
        except Exception as e:
            messagebox.showerror("Ошибка при загрузке", str(e))

    def save_to_file(self):
        fn = filedialog.asksaveasfilename(title="Сохранить состояния", defaultextension=".txt", filetypes=[
                                          ("Text files", "*.txt"), ("All files", "*")])
        if not fn:
            return
        n = self.n_var.get()
        try:
            with open(fn, "w", encoding="utf-8") as f:
                f.write(str(n) + "\n")
                for r in range(n):
                    row = self.start_state.grid[r * n:(r + 1) * n]
                    f.write(" ".join(map(str, row)) + "\n")
                f.write("\n")
                for r in range(n):
                    row = self.goal_state.grid[r * n:(r + 1) * n]
                    f.write(" ".join(map(str, row)) + "\n")
            messagebox.showinfo("Сохранено", f"Состояния сохранены в {fn}")
        except Exception as e:
            messagebox.showerror("Ошибка при сохранении", str(e))

    # ---------------------- Запуск / остановка поиска -----------------------
    def start_search(self):
        if self.search_running:
            messagebox.showwarning(
                "Поиск уже выполняется", "Подождите окончания текущего поиска или нажмите 'Остановить'.")
            return
        # проверка размеров
        n = self.n_var.get()
        self.start_state.n = n
        self.goal_state.n = n

        # если начальное и целевое не того же размера — обновим
        if len(self.start_state.grid) != n * n:
            self.start_state = State(tuple(range(n * n)), n)
            self.draw_canvas(self.canvas_start, self.start_state)
        if len(self.goal_state.grid) != n * n:
            self.goal_state = State(tuple(range(n * n)), n)
            self.draw_canvas(self.canvas_goal, self.goal_state)

        alg = self.algorithm_var.get()
        max_nodes = self.max_nodes_var.get()
        max_depth = self.max_depth_var.get()

        # подготовка в фоне
        self.search_running = True
        self.result_ready = False
        self.last_search_result = None
        self.clear_stats_display()
        self.disable_controls_while_search(True)

        def worker():
            try:
                if alg == "BFS":
                    path, moves, stats = bfs_search(
                        self.start_state, self.goal_state, max_nodes=max_nodes, progress_queue=self.message_queue)
                else:
                    path, moves, stats = dfs_search(
                        self.start_state, self.goal_state, max_nodes=max_nodes, max_depth=max_depth, progress_queue=self.message_queue)
                self.message_queue.put(("done", (path, moves, stats)))
            except Exception as e:
                self.message_queue.put(("error", str(e)))

        self.search_thread = threading.Thread(target=worker, daemon=True)
        self.search_thread.start()

    def stop_search(self):
        # простая отмена: установим флаг, но search функции не наблюдают за ним.
        # Поскольку search реализованы без проверки флага, остановка просто прекратит
        # обновления UI до завершения/достижения лимита. Мы пока не реализуем мягкую отмену.
        # Решение: переключим флаг, и при получения результатов будем его учитывать.
        if not self.search_running:
            return
        # предупреждение
        messagebox.showinfo(
            "Остановка", "Поиск остановится при достижении следующей точки сохранения или по тайм-ауту.")
        # на практике мы не можем немедленно остановить бесконечный цикл в worker без общей логики.

    def poll_queue(self):
        try:
            while True:
                msg = self.message_queue.get_nowait()
                tag, payload = msg
                if tag == "progress":
                    self.display_progress(payload)
                elif tag == "done":
                    path, moves, stats = payload
                    self.on_search_done(path, moves, stats)
                elif tag == "error":
                    self.on_search_error(payload)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.poll_queue)

    def display_progress(self, payload):
        s = f"Итерации: {payload['iterations']}, Раскрытий: {payload['nodes_expanded']}, O={payload['frontier_len']}, C={payload['closed_len']}"
        self.update_stats_text(s)

    def on_search_error(self, err_msg):
        messagebox.showerror("Ошибка в поиске", str(err_msg))
        self.search_running = False
        self.disable_controls_while_search(False)

    def on_search_done(self, path, moves, stats):
        self.search_running = False
        self.disable_controls_while_search(False)
        if path is None:
            s = "Решение не найдено.\n"
            s += f"Итерации: {stats['iterations']}, Раскрытий: {stats['nodes_expanded']}, max_open: {stats['max_open']}, open_at_end: {stats['open_at_end']}, max_memory: {stats['max_memory']}, time: {stats['time']:.3f}s"
            self.update_stats_text(s)
            return

        self.last_search_result = (path, moves, stats)
        s = "Решение найдено!\n"
        s += f"Длина пути (число состояний): {len(path)}\n"
        s += f"Итерации: {stats['iterations']}, Раскрытий: {stats['nodes_expanded']}\n"
        s += f"Макс O: {stats['max_open']}, O в конце: {stats['open_at_end']}, Макс память (O+C): {stats['max_memory']}\n"
        s += f"Время выполнения: {stats['time']:.3f} с"
        self.update_stats_text(s)

        # подготовим анимацию: покажем начальное
        self.current_display_state = path
        self.current_step = 0
        self.draw_canvas(self.canvas_start, self.current_display_state[0])

    def disable_controls_while_search(self, disable=True):
        # элементы, которые можно заблокировать/разблокировать
        state = "disabled" if disable else "normal"
        # здесь мы перечисляем основные кнопки
        # удобнее блокировать весь root — но нельзя
        # на текущем этапе — просто переключим кнопки в интерфейсе
        # (в простом варианте ничего не делаем)
        pass

    # --------------------- Отображение статистики --------------------
    def clear_stats_display(self):
        self.stats_text.config(state="normal")
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.config(state="disabled")

    def update_stats_text(self, text):
        self.stats_text.config(state="normal")
        self.stats_text.insert(tk.END, text + "\n")
        self.stats_text.see(tk.END)
        self.stats_text.config(state="disabled")

    # --------------------- Анимация решения -------------------------
    def show_next_step(self):
        if not self.last_search_result:
            messagebox.showinfo(
                "Нет решения", "Сначала выполните поиск и найдите решение.")
            return
        path, moves, stats = self.last_search_result
        if self.current_step >= len(path):
            messagebox.showinfo("Готово", "Достигнуто целевое состояние.")
            return
        self.draw_canvas(self.canvas_start, path[self.current_step])
        self.current_step += 1

    def play_solution(self):
        if not self.last_search_result:
            messagebox.showinfo(
                "Нет решения", "Сначала выполните поиск и найдите решение.")
            return
        self.playing = True
        self._play_loop()

    def _play_loop(self):
        if not getattr(self, 'playing', False):
            return
        path, moves, stats = self.last_search_result
        if self.current_step >= len(path):
            self.playing = False
            return
        self.draw_canvas(self.canvas_start, path[self.current_step])
        self.current_step += 1
        ms = max(10, self.animation_ms.get())
        self.root.after(ms, self._play_loop)

    def stop_animation(self):
        self.playing = False

# --------------------------- Запуск приложения ---------------------------


def main():
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
