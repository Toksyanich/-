import tkinter as tk
from tkinter import messagebox
import main  # Импортируем твой файл с логикой

# --- НАСТРОЙКИ ОТОБРАЖЕНИЯ ---
CELL_SIZE = 100  # Размер клетки в пикселях
PADDING = 5
COLOR_UNKNOWN = "#404040"  # Цвет неисследованной территории (Туман войны)
COLOR_VISITED = "#FFFFFF"  # Цвет посещенной клетки
COLOR_WALL = "#000000"

# Цвета объектов
COLOR_AGENT = "#0000FF"    # Синий кружок
COLOR_PIT = "#000000"      # Черная дыра
COLOR_WUMPUS = "#FF0000"   # Красный монстр
COLOR_GOLD = "#FFD700"     # Золото
COLOR_BREEZE = "#87CEEB"   # Голубой текст (Ветер)
COLOR_STENCH = "#90EE90"   # Зеленый текст (Вонь)


class WumpusGUI:
    def __init__(self, master, rows, cols, prob):
        self.master = master
        self.rows = rows
        self.cols = cols

        self.master.title("Wumpus World AI Visualization")

        # 1. Инициализация логики (Твой код)
        self.world = main.WampusWorld(rows, cols, prob)
        self.agent = main.Agent(self.world, 0, 0, rows, cols)

        # 2. Создание Канваса (Поля для рисования)
        canvas_width = cols * CELL_SIZE
        canvas_height = rows * CELL_SIZE
        self.canvas = tk.Canvas(
            master, width=canvas_width, height=canvas_height, bg="gray")
        self.canvas.pack(side=tk.LEFT)

        # 3. Панель управления (Справа)
        self.panel = tk.Frame(master)
        self.panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        self.lbl_status = tk.Label(
            self.panel, text="Готов к запуску", font=("Arial", 12))
        self.lbl_status.pack(pady=10)

        self.btn_step = tk.Button(
            self.panel, text="Сделать 1 шаг", command=self.do_step, height=2, width=15)
        self.btn_step.pack(pady=5)

        self.btn_run = tk.Button(self.panel, text="Авто-игра",
                                 command=self.auto_play, height=2, width=15, bg="lightgreen")
        self.btn_run.pack(pady=5)

        self.btn_restart = tk.Button(
            self.panel, text="Рестарт", command=self.restart, height=2, width=15, bg="salmon")
        self.btn_restart.pack(pady=20)

        self.is_running = False
        self.game_over = False

        # Первая отрисовка
        self.draw_grid()

    def restart(self):
        self.master.destroy()
        root = tk.Tk()
        app = WumpusGUI(root, self.rows, self.cols,
                        self.world.probability_of_pit)
        root.mainloop()

    def draw_grid(self):
        self.canvas.delete("all")  # Очистить поле

        # Получаем реальную карту (для читерского отображения или проверки)
        real_map = self.world.get_world()

        for x in range(self.rows):
            for y in range(self.cols):
                # Координаты для рисования (y - это колонка/горизонталь, x - строка/вертикаль)
                # В Tkinter X идет вправо, Y идет вниз.
                # В твоем массиве x - строка, y - столбец.
                x1 = y * CELL_SIZE
                y1 = x * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                # Определяем цвет фона (Туман войны)
                if (x, y) in self.agent.visited:
                    bg_color = COLOR_VISITED
                else:
                    bg_color = COLOR_UNKNOWN  # Скрыто
                    # Если хочешь видеть всё сразу (God Mode) - раскомментируй строку ниже:
                    # bg_color = "#D3D3D3"

                self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=bg_color, outline="black")

                # Если клетка посещена (или мы в режиме отладки), рисуем содержимое
                # Но чтобы было интереснее, давай рисовать содержимое всегда (полупрозрачно),
                # а ярко - если посетили.

                cell_content = real_map[x][y]

                # Рисуем Ямы и Монстров (Видны только если посещены или Гейм Овер)
                if (x, y) in self.agent.visited or self.game_over:
                    if "pit" in cell_content:
                        self.canvas.create_oval(
                            x1+10, y1+10, x2-10, y2-10, fill=COLOR_PIT)
                        self.canvas.create_text(
                            x1+50, y1+50, text="PIT", fill="white")

                    if "vantus" in cell_content:
                        self.canvas.create_rectangle(
                            x1+20, y1+20, x2-20, y2-20, fill=COLOR_WUMPUS)
                        self.canvas.create_text(
                            x1+50, y1+50, text="VANTUS", fill="white")

                    if "gold" in cell_content:
                        self.canvas.create_polygon(
                            x1+50, y1+10, x2-10, y1+50, x1+50, y2-10, x1+10, y1+50, fill=COLOR_GOLD)
                        self.canvas.create_text(
                            x1+50, y1+50, text="GOLD", fill="black")

                # Рисуем Сенсоры (Ветер/Вонь) - видны, если клетка посещена
                if (x, y) in self.agent.visited:
                    percepts_text = ""
                    if "wind" in cell_content:
                        self.canvas.create_text(
                            x1+20, y1+15, text="~~~~", fill=COLOR_BREEZE, font=("Arial", 14, "bold"))
                    if "stink" in cell_content:
                        self.canvas.create_text(
                            x1+80, y1+15, text="sss", fill=COLOR_STENCH, font=("Arial", 14, "bold"))

                # Рисуем АГЕНТА (поверх всего)
                if self.agent.x == x and self.agent.y == y:
                    self.canvas.create_oval(
                        x1+30, y1+30, x2-30, y2-30, fill=COLOR_AGENT, outline="white", width=2)
                    self.canvas.create_text(
                        x1+50, y1+85, text="YOU", fill=COLOR_AGENT)

    def do_step(self):
        if self.game_over:
            return

        # Вызываем шаг агента из твоего файла
        # Твой метод step() возвращает True (продолжаем) или False (стоп)
        try:
            result = self.agent.step()
        except Exception as e:
            print(f"Ошибка в логике агента: {e}")
            result = False

        self.draw_grid()

        # Обновляем статус
        self.lbl_status.config(text=f"Позиция: {self.agent.x}, {self.agent.y}")

        if result is False:
            self.game_over = True
            self.is_running = False
            # Проверяем причину остановки
            cell = self.world.get_world()[self.agent.x][self.agent.y]
            if "gold" in cell and "shine" in cell:
                messagebox.showinfo("Победа!", "Агент нашел золото и выжил!")
            elif "pit" in cell:
                messagebox.showerror("Game Over", "Агент упал в яму!")
            elif "vantus" in cell:
                messagebox.showerror("Game Over", "Агента съел Вампус!")
            else:
                messagebox.showwarning(
                    "Конец", "Агент зашел в тупик и сделал харакири.")

    def auto_play(self):
        if self.game_over:
            return
        self.is_running = True
        self.run_loop()

    def run_loop(self):
        if self.is_running and not self.game_over:
            self.do_step()
            # Задержка между шагами (в миллисекундах)
            self.master.after(800, self.run_loop)


def main_gui():
    root = tk.Tk()
    # Параметры мира (как у тебя в main)
    ROWS = 4
    COLS = 4
    PROB_PIT = 0.2

    app = WumpusGUI(root, ROWS, COLS, PROB_PIT)
    root.mainloop()


if __name__ == "__main__":
    main_gui()
