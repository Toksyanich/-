import tkinter as tk
from tkinter import messagebox
import os
import main  # Твой файл логики

# --- НАСТРОЙКИ ---
CELL_SIZE = 100  # Размер клетки
COLOR_UNKNOWN = "#2b2b2b"  # Темно-серый (Туман)
COLOR_VISITED = "#ffffff"  # Белый (Открыто)


class WumpusGUI:
    def __init__(self, master, rows, cols, prob):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.prob = prob  # Сохраняем вероятность для рестарта

        self.master.title("Wumpus World AI")

        # Загрузка иконок
        self.icons = {}
        self.load_assets()

        # Интерфейс: Канвас слева, Панель справа
        canvas_width = cols * CELL_SIZE
        canvas_height = rows * CELL_SIZE
        self.canvas = tk.Canvas(
            master, width=canvas_width, height=canvas_height, bg="gray")
        self.canvas.pack(side=tk.LEFT)

        self.panel = tk.Frame(master, bg="#e0e0e0")
        self.panel.pack(side=tk.RIGHT, fill=tk.Y, expand=True)

        # --- КНОПКИ ---
        tk.Label(self.panel, text="Меню", bg="#e0e0e0", font=(
            "Arial", 14, "bold")).pack(pady=10, padx=20)

        self.btn_step = tk.Button(
            self.panel, text="Сделать Шаг", command=self.do_step, width=15, height=2)
        self.btn_step.pack(pady=5)

        self.btn_run = tk.Button(self.panel, text="Авто-игра",
                                 command=self.auto_play, width=15, height=2, bg="lightgreen")
        self.btn_run.pack(pady=5)

        # !!! КНОПКА РЕСТАРТА ВЕРНУЛАСЬ !!!
        self.btn_restart = tk.Button(
            self.panel, text="Рестарт", command=self.reset_game, width=15, height=2, bg="salmon")
        self.btn_restart.pack(pady=20)

        self.status_var = tk.StringVar()
        self.status_var.set("Нажмите старт")
        tk.Label(self.panel, textvariable=self.status_var,
                 bg="#e0e0e0", wraplength=150, justify="left").pack(pady=10)

        # Инициализация первой игры
        self.start_new_game()

    def start_new_game(self):
        """Создает объекты мира и агента заново"""
        self.world = main.WampusWorld(self.rows, self.cols, self.prob)
        self.agent = main.Agent(self.world, 0, 0, self.rows, self.cols)
        self.is_running = False
        self.game_over = False
        self.suicide_pos = None
        self.status_var.set("Новая игра началась.")
        self.draw_grid()

    def reset_game(self):
        """Функция для кнопки Рестарт"""
        self.is_running = False  # Остановить авто-игру если была
        self.start_new_game()

    def load_assets(self):
        """Загрузка картинок"""
        image_files = {
            "agent": "icons/agent.png",
            "vantus": "icons/wumpus.png",
            "pit": "icons/pit.png",
            "gold": "icons/gold.png",
            "wind": "icons/wind.png",
            "stink": "icons/stench.png",
            "victory": "icons/victory.png"
        }

        for key, filename in image_files.items():
            if os.path.exists(filename):
                try:
                    img = tk.PhotoImage(file=filename)
                    # Если иконки слишком большие, можно уменьшить:
                    # img = img.subsample(2, 2)
                    self.icons[key] = img
                except Exception:
                    self.icons[key] = None
            else:
                self.icons[key] = None

    def draw_grid(self):
        self.canvas.delete("all")
        real_map = self.world.get_world()

        for x in range(self.rows):
            for y in range(self.cols):
                x1 = y * CELL_SIZE
                y1 = x * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                cx = x1 + CELL_SIZE // 2
                cy = y1 + CELL_SIZE // 2

                # --- ЛОГИКА ОТОБРАЖЕНИЯ (FOG OF WAR) ---
                # Клетка видна, если:
                # 1. Агент её посетил
                # 2. ИЛИ Игра окончена (self.game_over == True)
                is_visible = ((x, y) in self.agent.visited) or self.game_over

                # 1. Рисуем фон
                # 1. Рисуем фон (С ИЗМЕНЕНИЯМИ ДЛЯ ХАРАКИРИ)
                if (x, y) == self.suicide_pos:
                    # Если это место самоубийства — КРАСНЫЙ
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2, fill="#ff4d4d", outline="black")
                elif is_visible:
                    # Если обычная посещенная — БЕЛЫЙ
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2, fill=COLOR_VISITED, outline="#ccc")
                else:
                    # Если не видно — ТЕМНЫЙ
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2, fill=COLOR_UNKNOWN, outline="black")

                # 2. Рисуем содержимое (если клетка видна)
                if is_visible:
                    cell = real_map[x][y]

                    # ЯМА
                    if "pit" in cell:
                        if self.icons["pit"]:
                            self.canvas.create_image(
                                cx, cy, image=self.icons["pit"])
                        else:
                            self.canvas.create_oval(
                                x1+10, y1+10, x2-10, y2-10, fill="black")
                            self.canvas.create_text(
                                cx, cy, text="PIT", fill="white")

                    # ЗОЛОТО
                    if "gold" in cell:
                        if self.icons["gold"]:
                            self.canvas.create_image(
                                cx, cy, image=self.icons["gold"])
                        else:
                            self.canvas.create_oval(
                                x1+20, y1+20, x2-20, y2-20, fill="gold")
                            self.canvas.create_text(cx, cy, text="GOLD")

                    # ВАНТУС
                    if "vantus" in cell:
                        if self.icons["vantus"]:
                            self.canvas.create_image(
                                cx, cy, image=self.icons["vantus"])
                        else:
                            self.canvas.create_rectangle(
                                x1+15, y1+15, x2-15, y2-15, fill="red")
                            self.canvas.create_text(cx, cy, text="WUMPUS")

                    # СЕНСОРЫ (Если это не конец игры, или просто хотим видеть карту полностью)
                    # Ветер (слева сверху)
                    if "wind" in cell:
                        if self.icons["wind"]:
                            self.canvas.create_image(
                                x1+20, y1+20, image=self.icons["wind"])
                        else:
                            self.canvas.create_text(
                                x1+20, y1+20, text="~~", fill="blue")

                    # Вонь (справа сверху)
                    if "stink" in cell:
                        if self.icons["stink"]:
                            self.canvas.create_image(
                                x2-20, y1+20, image=self.icons["stink"])
                        else:
                            self.canvas.create_text(
                                x2-20, y1+20, text="SS", fill="green")

                # 3. АГЕНТ (Рисуем только если игра идет, или на последней позиции)
                if self.agent.x == x and self.agent.y == y:

                    # Проверяем, нашел ли он золото
                    # (Есть блеск/золото в текущей клетке)
                    cell_content = real_map[x][y]
                    found_gold = "gold" in cell_content and "shine" in cell_content

                    if found_gold and self.icons["victory"]:
                        # === РИСУЕМ THE WEEKND НА ВСЮ КЛЕТКУ ===
                        # cx, cy - это центр клетки, картинка ляжет ровно по центру
                        self.canvas.create_image(
                            cx, cy, image=self.icons["victory"])
                    else:
                        # Обычная отрисовка агента
                        if self.icons["agent"]:
                            self.canvas.create_image(
                                cx, cy, image=self.icons["agent"])
                        else:
                            self.canvas.create_oval(
                                x1+30, y1+30, x2-30, y2-30, fill="blue", outline="white", width=2)
                            self.canvas.create_text(
                                cx, y2-10, text="YOU", fill="blue")

    def do_step(self):
        if self.game_over:
            return

        try:
            result = self.agent.step()
        except Exception as e:
            print(f"Ошибка: {e}")
            result = False

        # Обновляем инфо
        self.status_var.set(
            f"Позиция: [{self.agent.x}, {self.agent.y}]\nОщущения: {self.world.get_percepts(self.agent.x, self.agent.y)}")

        # Если игра закончилась
        if result is False:
            self.game_over = True
            self.is_running = False
            # --- ПРОВЕРКА НА ХАРАКИРИ ---
            cell = self.world.get_world()[self.agent.x][self.agent.y]
            # Если в клетке нет смерти (ямы/вантуса) и нет победы (золота), значит это тупик
            is_death = "pit" in cell or "vantus" in cell
            is_win = "gold" in cell and "shine" in cell

            if not is_death and not is_win:
                # Запоминаем место харакири
                self.suicide_pos = (self.agent.x, self.agent.y)
            # Сначала перерисуем поле, чтобы открыть карту (благодаря self.game_over = True)
            self.draw_grid()

            # Потом покажем сообщение
            self.show_end_message()
        else:
            self.draw_grid()

    def show_end_message(self):
        cell = self.world.get_world()[self.agent.x][self.agent.y]
        if "gold" in cell and "shine" in cell:
            messagebox.showinfo("Победа!", "Золото найдено! Вы богаты!")
        elif "pit" in cell:
            messagebox.showerror("Game Over", "Агент упал в яму.")
        elif "vantus" in cell:
            messagebox.showerror("Game Over", "Агента съел Вантус.")
        else:
            messagebox.showwarning(
                "Стоп", "Нервы сдали. Агент сделал харакири!")

    def auto_play(self):
        if self.game_over:
            return
        self.is_running = True
        self.run_loop()

    def run_loop(self):
        if self.is_running and not self.game_over:
            self.do_step()
            self.master.after(500, self.run_loop)  # Скорость 0.5 сек


def main_gui():
    root = tk.Tk()
    ROWS = 5
    COLS = 5
    PROB = 0.2
    app = WumpusGUI(root, ROWS, COLS, PROB)
    root.mainloop()


if __name__ == "__main__":
    main_gui()
