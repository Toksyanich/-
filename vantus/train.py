import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
import os
from collections import deque

# Импортируем генератор мира из твоего файла
from main import WampusWorld

# --- НАСТРОЙКИ ---
MAP_SIZE = 4          # Размер карты для обучения (лучше начать с 4x4)
PIT_PROB = 0.16        # Вероятность ям
BATCH_SIZE = 64       # Сколько шагов запоминаем для обучения
GAMMA = 0.99          # Важность будущих наград (дальновидность)
EPSILON_START = 1.0   # Начальный шанс случайного хода (100%)
EPSILON_END = 0.05    # Конечный шанс случайного хода (5%)
EPSILON_DECAY = 0.9995  # Скорость уменьшения случайности
LR = 0.001            # Скорость обучения (Learning Rate)
EPISODES = 5000       # Сколько игр сыграем

# --- 1. СРЕДА (Обертка над твоим миром) ---


class WumpusEnv:
    def __init__(self, size=4):
        self.size = size
        self.world_gen = None
        self.real_map = None
        self.agent_pos = [0, 0]
        self.actions = {
            0: (-1, 0),  # Вверх
            1: (1, 0),  # Вниз
            2: (0, -1),  # Влево
            3: (0, 1)   # Вправо
        }
    def reset(self):
        """Создает новый мир и возвращает вектор ощущений"""
        # Генерируем мир через твой класс
        self.world_gen = WampusWorld(self.size, self.size, PIT_PROB)
        self.real_map = self.world_gen.get_world()
        self.agent_pos = [0, 0]
        return self.get_observation()

    def get_observation(self):
        """Превращает ощущения (слова) в числа для нейросети"""
        x, y = self.agent_pos
        # Сенсоры: [Stench, Breeze, Glitter, Bump] -> 0 или 1
        # Bump (удар) мы определим в step
        obs = [0, 0, 0, 0] 
        
        percepts = self.world_gen.get_percepts(x, y)
        if 'stink' in percepts: obs[0] = 1
        if 'wind' in percepts: obs[1] = 1
        if 'shine' in percepts: obs[2] = 1
        
        return np.array(obs, dtype=np.float32)
    def step(self, action):
        """Выполняет действие. Возвращает: State, Reward, Done"""
        dx, dy = self.actions[action]
        nx, ny = self.agent_pos[0] + dx, self.agent_pos[1] + dy
        
        reward = -1 # Штраф за шаг (чтобы искал быстрее)
        done = False
        bump = 0
        
        # 1. Проверка стен (Bump)
        if not (0 <= nx < self.size and 0 <= ny < self.size):
            nx, ny = self.agent_pos # Остаемся на месте
            reward = -5 # Больно ударился
            bump = 1
        else:
            self.agent_pos = [nx, ny]

        # 2. Получаем новые ощущения
        cell = self.real_map[nx][ny]
        
        # 3. Проверка событий
        if 'pit' in cell:
            reward = -100 # Смерть в яме
            done = True
        elif 'vantus' in cell:
            reward = -100 # Смерть от монстра
            done = True
        elif 'gold' in cell:
            reward = 100 # ПОБЕДА!
            done = True
        
        # Формируем вектор состояния
        next_obs = self.get_observation()
        if bump: next_obs[3] = 1 # Записываем Bump в вектор
        
        return next_obs, reward, done