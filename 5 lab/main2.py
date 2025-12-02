import numpy as np


class AHP:
    def __init__(self, criteria_names):
        self.criteria_names = criteria_names
        self.n = len(criteria_names)
        self.matrix = np.ones((self.n, self.n))

    def add_comparison(self, i, j, value):
        """
        Добавляет сравнение: критерий i важнее критерия j в value раз.
        i, j - индексы (начиная с 0) или названия критериев.
        """
        idx_i = self._get_index(i)
        idx_j = self._get_index(j)

        self.matrix[idx_i, idx_j] = value
        self.matrix[idx_j, idx_i] = 1 / value

    def _get_index(self, name_or_idx):
        if isinstance(name_or_idx, int):
            return name_or_idx
        return self.criteria_names.index(name_or_idx)

    def calculate_weights(self):
        """Вычисляет весовой вектор и проверяет согласованность."""
        # Вычисляем собственные числа и векторы
        eigvals, eigvecs = np.linalg.eig(self.matrix)

        # Максимальное собственное число (должно быть вещественным)
        max_eigval = np.max(eigvals).real

        # Собственный вектор, соответствующий max_eigval
        max_eigvec = eigvecs[:, np.argmax(eigvals)].real

        # Нормализация вектора (сумма элементов = 1)
        weights = max_eigvec / np.sum(max_eigvec)

        # Индекс согласованности (CI)
        ci = (max_eigval - self.n) / (self.n - 1) if self.n > 1 else 0

        # Случайный индекс (RI) по Саати
        ri_dict = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12,
                   6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
        ri = ri_dict.get(self.n, 1.49)

        # Отношение согласованности (CR)
        cr = ci / ri if ri != 0 else 0

        return weights, cr, max_eigval

    def print_results(self, title):
        weights, cr, lam = self.calculate_weights()
        print(f"\n--- {title} ---")
        print("Матрица парных сравнений:")
        print(np.round(self.matrix, 2))
        print("\nЛокальные приоритеты (Веса):")
        for name, w in zip(self.criteria_names, weights):
            print(f"{name}: {w:.4f}")

        print(f"\nLambda_max: {lam:.4f}")
        print(
            f"Индекс согласованности (CI): {(lam - self.n)/(self.n - 1):.4f}")
        print(f"Отношение согласованности (CR): {cr:.4f}")
        if cr > 0.1:  # Порог 0.1 (или 0.2 для больших матриц)
            print("ВНИМАНИЕ: Матрица недостаточно согласована! (CR > 0.1)")
        else:
            print("Матрица согласована.")
        return weights

# ==========================================
# РЕШЕНИЕ ВАРИАНТА 5
# ==========================================


print("=== ЛАБОРАТОРНАЯ РАБОТА №5: ВАРИАНТ 5 (ХОККЕЙНЫЕ КЛУБЫ) ===")

alternatives = ["Питтсбург", "Вашингтон", "Нью-Джерси"]

# 1. МАТРИЦА ВЛИЯНИЯ СТОРОН (Уровень 1)
# Текст: Спонсор - наибольшее влияние, Тренер - немного меньшее, Игроки - еще меньшее.
# Шкала Саати: 1-равно, 3-умеренно, 5-существенно, 7-значительно, 9-абсолютно.
# Допустим: Спонсор vs Тренер = 3, Тренер vs Игроки = 2, Спонсор vs Игроки = 5.
ahp_stakeholders = AHP(["Спонсор", "Тренер", "Игроки"])
ahp_stakeholders.add_comparison("Спонсор", "Тренер", 3)
ahp_stakeholders.add_comparison("Спонсор", "Игроки", 5)
ahp_stakeholders.add_comparison("Тренер", "Игроки", 2)
w_stakeholders = ahp_stakeholders.print_results(
    "Влияние заинтересованных сторон")

# 2. МАТРИЦЫ ВАЖНОСТИ КРИТЕРИЕВ ДЛЯ КАЖДОЙ СТОРОНЫ (Уровень 2)

# А) Для Спонсора: Финансирование, Реклама, Трансферы.
# Текст: "Победа зависит в первую очередь от финансирования, в меньшей (и примерно равной) степени – от рекламы и трансферов"
ahp_sponsor_criteria = AHP(["Финансирование", "Реклама", "Трансферы"])
ahp_sponsor_criteria.add_comparison(
    "Финансирование", "Реклама", 4)  # Между 3 и 5
ahp_sponsor_criteria.add_comparison("Финансирование", "Трансферы", 4)
ahp_sponsor_criteria.add_comparison(
    "Реклама", "Трансферы", 1)  # Примерно равны
w_c_sponsor = ahp_sponsor_criteria.print_results("Критерии Спонсора")

# Б) Для Тренера: Трансферы, Опыт, Болельщики.
# Текст: "В первую очередь трансферная политика, чуть менее важен опыт, еще менее важна поддержка болельщиков"
ahp_coach_criteria = AHP(["Трансферы", "Опыт", "Болельщики"])
ahp_coach_criteria.add_comparison("Трансферы", "Опыт", 2)
ahp_coach_criteria.add_comparison("Трансферы", "Болельщики", 5)
ahp_coach_criteria.add_comparison("Опыт", "Болельщики", 3)
w_c_coach = ahp_coach_criteria.print_results("Критерии Тренера")

# В) Для Игроков: Опыт, Болельщики, Реклама.
# Текст: "Наибольшее влияние Опыт, немного меньшее Болельщики, еще меньшее Реклама"
ahp_players_criteria = AHP(["Опыт", "Болельщики", "Реклама"])
ahp_players_criteria.add_comparison("Опыт", "Болельщики", 2)
ahp_players_criteria.add_comparison("Опыт", "Реклама", 5)
ahp_players_criteria.add_comparison("Болельщики", "Реклама", 3)
w_c_players = ahp_players_criteria.print_results("Критерии Игроков")


# 3. СРАВНЕНИЕ АЛЬТЕРНАТИВ ПО КАЖДОМУ КРИТЕРИЮ (Уровень 3)

# Критерий 1: Финансирование
# Текст: Вашингтон самый богатый, Питтсбург меньше, Нью-Джерси наименьший.
ahp_funding = AHP(alternatives)
ahp_funding.add_comparison("Вашингтон", "Питтсбург", 3)
ahp_funding.add_comparison("Вашингтон", "Нью-Джерси", 6)
ahp_funding.add_comparison("Питтсбург", "Нью-Джерси", 3)
w_a_funding = ahp_funding.print_results("Альтернативы по Финансированию")

# Критерий 2: Опыт хоккеистов
# Текст: Питтсбург (наиболее опытные) > Вашингтон > Нью-Джерси (самые молодые).
ahp_experience = AHP(alternatives)
ahp_experience.add_comparison("Питтсбург", "Вашингтон", 3)
ahp_experience.add_comparison("Питтсбург", "Нью-Джерси", 6)
ahp_experience.add_comparison("Вашингтон", "Нью-Джерси", 3)
w_a_experience = ahp_experience.print_results("Альтернативы по Опыту")

# Критерий 3: Поддержка болельщиков
# Текст: Нью-Джерси (самая внушительная) > Питтсбург и Вашингтон (меньше).
ahp_fans = AHP(alternatives)
ahp_fans.add_comparison("Нью-Джерси", "Питтсбург", 5)
ahp_fans.add_comparison("Нью-Джерси", "Вашингтон", 5)
ahp_fans.add_comparison("Питтсбург", "Вашингтон", 1)  # Допустим примерно равны
w_a_fans = ahp_fans.print_results("Альтернативы по Болельщикам")

# Критерий 4: Рекламные контракты
# Текст: Нью-Джерси (самая большая сумма) > Питтсбург > Вашингтон (наименьшее).
ahp_ads = AHP(alternatives)
ahp_ads.add_comparison("Нью-Джерси", "Питтсбург", 3)
ahp_ads.add_comparison("Нью-Джерси", "Вашингтон", 6)
ahp_ads.add_comparison("Питтсбург", "Вашингтон", 3)
w_a_ads = ahp_ads.print_results("Альтернативы по Рекламе")

# Критерий 5: Трансферная политика
# Текст: Вашингтон (наиболее грамотно) > Питтсбург = Нью-Джерси (уступают).
ahp_transfer = AHP(alternatives)
ahp_transfer.add_comparison("Вашингтон", "Питтсбург", 4)
ahp_transfer.add_comparison("Вашингтон", "Нью-Джерси", 4)
ahp_transfer.add_comparison("Питтсбург", "Нью-Джерси", 1)  # Одинаково ведут
w_a_transfer = ahp_transfer.print_results("Альтернативы по Трансферам")


# 4. ИЕРАРХИЧЕСКИЙ СИНТЕЗ (Расчет глобальных приоритетов)

print("\n--- Глобальный синтез ---")

# Список всех уникальных критериев
all_criteria = ["Финансирование", "Опыт", "Болельщики", "Реклама", "Трансферы"]
# Вектора приоритетов альтернатив по этим критериям
w_alternatives_matrix = np.array(
    [w_a_funding, w_a_experience, w_a_fans, w_a_ads, w_a_transfer]).T
# Строки - альтернативы, Столбцы - критерии

# Рассчитаем глобальные веса критериев с учетом влияния сторон
# W_global(Criterion) = Sum( Weight(Stakeholder) * Weight(Criterion|Stakeholder) )
# Если критерий не важен для стейкхолдера, вес = 0.

# Инициализируем глобальные веса критериев нулями
global_criteria_weights = {c: 0.0 for c in all_criteria}

# Спонсор (index 0 in w_stakeholders)
# Критерии Спонсора: Финансирование (idx 0), Реклама (idx 1), Трансферы (idx 2)
global_criteria_weights["Финансирование"] += w_stakeholders[0] * w_c_sponsor[0]
global_criteria_weights["Реклама"] += w_stakeholders[0] * w_c_sponsor[1]
global_criteria_weights["Трансферы"] += w_stakeholders[0] * w_c_sponsor[2]

# Тренер (index 1 in w_stakeholders)
# Критерии Тренера: Трансферы (idx 0), Опыт (idx 1), Болельщики (idx 2)
global_criteria_weights["Трансферы"] += w_stakeholders[1] * w_c_coach[0]
global_criteria_weights["Опыт"] += w_stakeholders[1] * w_c_coach[1]
global_criteria_weights["Болельщики"] += w_stakeholders[1] * w_c_coach[2]

# Игроки (index 2 in w_stakeholders)
# Критерии Игроков: Опыт (idx 0), Болельщики (idx 1), Реклама (idx 2)
global_criteria_weights["Опыт"] += w_stakeholders[2] * w_c_players[0]
global_criteria_weights["Болельщики"] += w_stakeholders[2] * w_c_players[1]
global_criteria_weights["Реклама"] += w_stakeholders[2] * w_c_players[2]

# Преобразуем в массив в порядке all_criteria
w_criteria_global_vec = np.array(
    [global_criteria_weights[c] for c in all_criteria])

print("\nГлобальные веса критериев:")
for name, w in zip(all_criteria, w_criteria_global_vec):
    print(f"{name}: {w:.4f}")

# Финальный подсчет: Умножаем матрицу весов альтернатив на вектор весов критериев
final_scores = np.dot(w_alternatives_matrix, w_criteria_global_vec)

print("\n=== ИТОГОВЫЙ РЕЗУЛЬТАТ ===")
best_alt_idx = np.argmax(final_scores)
for i, name in enumerate(alternatives):
    print(f"{name}: {final_scores[i]:.4f}")

print(f"\nНаиболее вероятный победитель: {alternatives[best_alt_idx].upper()}")
