#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog
from collections import deque
import threading
import time
from dataclasses import dataclass
from typing import Tuple, List, Optional

# Импортируем A* алгоритмы
from astar_search import astar_h1, astar_h2, State


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


@dataclass
class Stats:
    iterations: int        # число итераций / развёртываний
    max_open: int
    open_end: int
    max_memory: int
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
            return Stats(it, mo, len(Q), max(mm, len(Q)+len(closed)), float(it), s.path())
        closed.add(s.tiles)
        for n in s.expand():
            if n.tiles not in seen and n.tiles not in closed:
                Q.append(n)
                seen.add(n.tiles)
        mo = max(mo, len(Q))
        mm = max(mm, len(Q)+len(closed))
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
            return Stats(it, mo, len(S), max(mm, len(S)+len(closed)), float(it), s.path())
        closed.add(s.tiles)
        for n in reversed(s.expand()):
            if n.tiles not in closed and n.tiles not in seen:
                S.append(n)
                seen.add(n.tiles)
        mo = max(mo, len(S))
        mm = max(mm, len(S)+len(closed))
    return Stats(it, mo, len(S), mm, float(it), None)


def iddfs(start: State, goal: Tuple[int, ...], limit=20) -> Stats:
    total = 0
    mo = 0
    mm = 0
    found = None

    def dls(node, d, lim, pathset):
        nonlocal total, mo, mm, found
        total += 1
        if node.tiles == goal:
            found = node
            return True
        if d == lim:
            return False
        for n in node.expand():
            if n.tiles in pathset:
                continue
            pathset.add(n.tiles)
            if dls(n, d+1, lim, pathset):
                return True
            pathset.remove(n.tiles)
        mo = max(mo, len(pathset))
        mm = max(mm, len(pathset))
        return False

    for l in range(limit+1):
        if dls(start, 0, l, {start.tiles}):
            return Stats(total, mo, 0, mm, float(total), found.path())
    return Stats(total, mo, 0, mm, float(total), None)


class App:
    def __init__(self, root):
        self.root = root
        self.start = None
        self.goal = None
        self.solution = None
        self.search_thread = None
        self.anim_thread = None

        f = ttk.Frame(root)
        f.pack(side='left', fill='y', padx=5, pady=5)

        ttk.Button(f, text="Загрузить файл", command=self.load_file).grid(
            row=0, column=0, columnspan=2, pady=5)

        # Слепой поиск
        ttk.Label(f, text="Слепой поиск:", font=('Arial', 9, 'bold')).grid(
            row=1, column=0, columnspan=2, sticky='w')
        ttk.Button(f, text="BFS", command=lambda: self.run_search(
            'BFS')).grid(row=2, column=0, columnspan=2)
        ttk.Button(f, text="DFS", command=lambda: self.run_search(
            'DFS')).grid(row=3, column=0, columnspan=2)
        ttk.Button(f, text="IDDFS", command=lambda: self.run_search(
            'IDDFS')).grid(row=4, column=0, columnspan=2)

        # Информированный поиск (A*)
        ttk.Label(f, text="Информированный поиск (A*):", font=('Arial', 9, 'bold')).grid(
            row=5, column=0, columnspan=2, sticky='w', pady=(10, 0))
        ttk.Button(f, text="A* (h1)", command=lambda: self.run_search(
            'A*_H1')).grid(row=6, column=0)
        ttk.Button(f, text="A* (h2)", command=lambda: self.run_search(
            'A*_H2')).grid(row=6, column=1)

        ttk.Button(f, text="Показать анимацию", command=self.show_animation).grid(
            row=7, column=0, columnspan=2, pady=5)

        self.log = tk.Text(f, width=50, height=22)
        self.log.grid(row=8, column=0, columnspan=2)

        self.canvas_cur = tk.Canvas(root, width=300, height=300, bg="#b22222")
        self.canvas_cur.pack(side='left', padx=5)

        self.canvas_goal = tk.Canvas(root, width=300, height=300, bg="#333")
        self.canvas_goal.pack(side='left', padx=5)

    def write(self, *a):
        self.log.insert('end', ' '.join(map(str, a))+'\n')
        self.log.see('end')

    def draw(self, cv, state):
        cv.delete('all')
        if not state:
            return
        r, c = state.rows, state.cols
        w, h = cv.winfo_width(), cv.winfo_height()
        if w <= 1 or h <= 1:
            w, h = 300, 300
        cw, ch = w/c, h/r
        rad = min(cw, ch)*0.4
        for i in range(r):
            for j in range(c):
                idx = i*c+j
                if state.tiles[idx] == 1:
                    x = j*cw+cw/2
                    y = i*ch+ch/2
                    cv.create_oval(x-rad, y-rad, x+rad, y+rad,
                                   fill="white", outline='black', width=2)

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[('Text', '*.txt')])
        if not path:
            return
        with open(path) as f:
            lines = [line.strip() for line in f if line.strip() != '']
        r, c = map(int, lines[0].split())
        start_rows = lines[1:1+r]
        goal_rows = lines[1+r:1+2*r]

        def parse(rows):
            vals = []
            for ln in rows:
                vals.extend([1 if x in ('1', '*') else 0 for x in ln.split()])
            return tuple(vals)

        self.start = State(parse(start_rows), r, c)
        self.goal = State(parse(goal_rows), r, c)
        self.draw(self.canvas_cur, self.start)
        self.draw(self.canvas_goal, self.goal)
        self.write("Начальное и целевое состояния загружены.")

    def run_search(self, alg):
        if not self.start or not self.goal:
            self.write("Сначала загрузите файл.")
            return
        if self.search_thread and self.search_thread.is_alive():
            self.write("Поиск уже идёт.")
            return

        def work():
            if alg == 'BFS':
                st = bfs(self.start, self.goal.tiles)
            elif alg == 'DFS':
                st = dfs(self.start, self.goal.tiles)
            elif alg == 'IDDFS':
                st = iddfs(self.start, self.goal.tiles)
            elif alg == 'A*_H1':
                st = astar_h1(self.start, self.goal.tiles)
            elif alg == 'A*_H2':
                st = astar_h2(self.start, self.goal.tiles)

            self.solution = st.path
            self.root.after(0, lambda: self.show_stats(alg, st))

        self.search_thread = threading.Thread(target=work, daemon=True)
        self.search_thread.start()

    def show_stats(self, alg, st: Stats):
        self.write("\n" + "="*45)
        if st.heuristic_name:
            self.write(f"{st.heuristic_name} завершён")
        else:
            self.write(f"{alg} завершён")
        self.write(f"Итераций / развёртываний: {st.iterations}")
        self.write(f"Макс. узлов в O: {st.max_open}")
        self.write(f"Узлов в O при завершении: {st.open_end}")
        self.write(f"Макс. (O+C): {st.max_memory}")
        self.write(f"Время (условные единицы): {st.time_s:.0f}")
        if st.path:
            self.write(f"Длина пути: {len(st.path)-1}")
        else:
            self.write("Решение не найдено")
        self.write("="*45)

    def show_animation(self):
        if not self.solution:
            self.write("Сначала выполните поиск.")
            return
        if self.anim_thread and self.anim_thread.is_alive():
            self.write("Анимация уже идёт.")
            return

        def anim():
            for s in self.solution:
                self.root.after(0, lambda st=s: self.draw(self.canvas_cur, st))
                time.sleep(0.5)

        self.anim_thread = threading.Thread(target=anim, daemon=True)
        self.anim_thread.start()


if __name__ == "__main__":
    tk_root = tk.Tk()
    tk_root.title("Повороты одинаковых шариков - ЛР №1,2,3")
    App(tk_root)
    tk_root.mainloop()
