# main_gui.py

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import random
import json
import threading  # ИЗМЕНЕНИЕ ###
import queue  # ИЗМЕНЕНИЕ ###
from state import State
from solver import solve

# --- Конфигурация ---
BOARD_SIZE = 4
CELL_SIZE = 80
COLORS = {
    1: "red", 2: "green", 3: "blue", 4: "yellow",
    5: "cyan", 6: "magenta", 7: "orange", 8: "purple",
    9: "brown", 10: "white", 11: "gray", 12: "pink",
    13: "lime", 14: "navy", 15: "teal", 0: "black"
}


class PuzzleGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Лабораторная работа №1 - Повороты шариков")

        self.start_state = None
        self.goal_state = None
        self.solution_path = []
        self.animation_step = 0

        ### ИЗМЕНЕНИЕ: Очередь для обмена данными между потоками ###
        self.result_queue = queue.Queue()

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(padx=10, pady=10)

        # --- Панель управления ---
        control_frame = tk.Frame(self.main_frame)
        control_frame.grid(row=0, column=0, columnspan=2, pady=5)

        self.load_start_btn = tk.Button(
            control_frame, text="Загрузить начальное", command=self.load_start_state)
        self.load_start_btn.pack(side=tk.LEFT, padx=5)
        self.load_goal_btn = tk.Button(
            control_frame, text="Загрузить целевое", command=self.load_goal_state)
        self.load_goal_btn.pack(side=tk.LEFT, padx=5)
        self.gen_btn = tk.Button(
            control_frame, text="Случайная генерация", command=self.generate_random_states)
        self.gen_btn.pack(side=tk.LEFT, padx=5)
        self.bfs_btn = tk.Button(
            control_frame, text="Решить (BFS)", command=lambda: self.start_solver_thread('bfs'))
        self.bfs_btn.pack(side=tk.LEFT, padx=5)
        self.dfs_btn = tk.Button(
            control_frame, text="Решить (DFS)", command=lambda: self.start_solver_thread('dfs'))
        self.dfs_btn.pack(side=tk.LEFT, padx=5)

        # --- Холсты для отображения состояний ---
        self.start_canvas = self.create_canvas("Начальное состояние", 1, 0)
        self.goal_canvas = self.create_canvas("Целевое состояние", 1, 1)

        # --- Статистика ---
        stats_frame = tk.LabelFrame(self.main_frame, text="Статистика поиска")
        stats_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
        self.stats_labels = {
            "Итераций": tk.Label(stats_frame, text="Итераций: -"),
            "Макс. узлов в O": tk.Label(stats_frame, text="Макс. узлов в O: -"),
            "Узлов в O в конце": tk.Label(stats_frame, text="Узлов в O в конце: -"),
            "Макс. узлов в памяти": tk.Label(stats_frame, text="Макс. узлов в памяти (O+C): -"),
            "Длина пути": tk.Label(stats_frame, text="Длина пути: -")
        }
        for label in self.stats_labels.values():
            label.pack(anchor="w")

        self.generate_random_states()

    def create_canvas(self, title_text, r, c):
        frame = tk.Frame(self.main_frame)
        frame.grid(row=r, column=c, padx=10)
        tk.Label(frame, text=title_text, font=("Arial", 14)).pack()
        canvas = tk.Canvas(frame, width=BOARD_SIZE * CELL_SIZE,
                           height=BOARD_SIZE * CELL_SIZE, bg='lightgrey')
        canvas.pack()
        return canvas

    def draw_board(self, canvas, state):
        canvas.delete("all")
        if not state:
            return
        board = state.board
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                color_id = board[r][c]
                canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5,
                                   fill=COLORS.get(color_id, "black"), outline="black")

    def load_state_from_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt")])
        if not filepath:
            return None
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                if len(data) != BOARD_SIZE or any(len(row) != BOARD_SIZE for row in data):
                    raise ValueError(
                        "Размер поля в файле не соответствует настройкам.")
                return State(data)
        except Exception as e:
            messagebox.showerror(
                "Ошибка загрузки", f"Не удалось загрузить файл: {e}")
            return None

    def load_start_state(self):
        state = self.load_state_from_file()
        if state:
            self.start_state = state
            self.draw_board(self.start_canvas, self.start_state)

    def load_goal_state(self):
        state = self.load_state_from_file()
        if state:
            self.goal_state = state
            self.draw_board(self.goal_canvas, self.goal_state)

    def generate_random_states(self):
        goal_board = [[(r * BOARD_SIZE + c + 1) % (BOARD_SIZE*BOARD_SIZE)
                       for c in range(BOARD_SIZE)] for r in range(BOARD_SIZE)]
        self.goal_state = State(goal_board)

        start_board = [list(row) for row in goal_board]
        num_shuffles = simpledialog.askinteger(
            "Генерация", "Введите количество случайных поворотов:", initialvalue=5, minvalue=1, maxvalue=50)
        if num_shuffles is None:
            return

        temp_state = State(start_board)
        for _ in range(num_shuffles):
            successors = temp_state.get_successors()
            temp_state = random.choice(successors)
        self.start_state = State(temp_state.board)

        self.draw_board(self.start_canvas, self.start_state)
        self.draw_board(self.goal_canvas, self.goal_state)

    ### ИЗМЕНЕНИЕ: Метод, запускающий поиск в отдельном потоке ###
    def start_solver_thread(self, method):
        if not self.start_state or not self.goal_state:
            messagebox.showwarning(
                "Внимание", "Загрузите начальное и целевое состояния.")
            return

        # Отключаем кнопки, чтобы избежать повторного запуска
        self.bfs_btn.config(state=tk.DISABLED)
        self.dfs_btn.config(state=tk.DISABLED)
        self.gen_btn.config(state=tk.DISABLED)
        self.title(f"Идет поиск ({method.upper()})...")

        # Создаем и запускаем поток
        thread = threading.Thread(
            target=self.solve_puzzle_worker,
            args=(self.start_state, self.goal_state, method),
            daemon=True
        )
        thread.start()

        # Начинаем проверять очередь на наличие результата
        self.after(100, self.check_result_queue)

    ### ИЗМЕНЕНИЕ: Функция-воркер, которая будет выполняться в фоновом потоке ###
    def solve_puzzle_worker(self, start, goal, method):
        path, stats = solve(start, goal, method)
        self.result_queue.put((path, stats))

    ### ИЗМЕНЕНИЕ: Функция для проверки очереди и обработки результата ###
    def check_result_queue(self):
        try:
            # Пытаемся получить результат без блокировки
            path, stats = self.result_queue.get_nowait()

            # Если мы здесь, значит поиск завершен
            self.update_stats(stats, path)

            # Включаем кнопки обратно
            self.bfs_btn.config(state=tk.NORMAL)
            self.dfs_btn.config(state=tk.NORMAL)
            self.gen_btn.config(state=tk.NORMAL)
            self.title("Лабораторная работа №1 - Повороты шариков")

            if path:
                self.solution_path = path
                self.animation_step = 0
                messagebox.showinfo(
                    "Успех!", f"Решение найдено за {len(path) - 1} шагов.")
                self.animate_solution()
            else:
                messagebox.showerror("Неудача", "Не удалось найти решение.")

        except queue.Empty:
            # Если очередь пуста, значит поиск еще идет.
            # Проверяем еще раз через 100 мс.
            self.after(100, self.check_result_queue)

    def animate_solution(self):
        if self.animation_step < len(self.solution_path):
            current_state = self.solution_path[self.animation_step]
            self.draw_board(self.start_canvas, current_state)
            self.title(
                f"Шаг {self.animation_step}/{len(self.solution_path)-1}: {current_state.move or 'Начало'}")
            self.animation_step += 1
            self.after(500, self.animate_solution)
        else:
            self.title("Анимация завершена")
            self.draw_board(self.start_canvas, self.start_state)

    def update_stats(self, stats, path):
        self.stats_labels["Итераций"].config(
            text=f"Итераций: {stats['iterations']}")
        self.stats_labels["Макс. узлов в O"].config(
            text=f"Макс. узлов в O: {stats['max_open_list']}")
        self.stats_labels["Узлов в O в конце"].config(
            text=f"Узлов в O в конце: {stats['final_open_list']}")
        self.stats_labels["Макс. узлов в памяти"].config(
            text=f"Макс. узлов в памяти (O+C): {stats['max_memory_nodes']}")
        self.stats_labels["Длина пути"].config(
            text=f"Длина пути: {len(path) - 1 if path else 'N/A'}")


if __name__ == "__main__":
    app = PuzzleGUI()
    app.mainloop()
