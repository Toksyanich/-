import numpy as np

# Таблица случайных индексов (RI) для расчета CR
RI_TABLE = {
    1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49
}


def analyze_matrix(matrix, labels):
    """
    Анализирует матрицу парных сравнений методом анализа иерархий.

    Args:
        matrix (np.array): Квадратная обратно-симметричная матрица.
        labels (list): Список названий для строк/столбцов.

    Returns:
        dict: Словарь с результатами анализа.
    """
    n = matrix.shape[0]

    # 1. Вычисление вектора приоритетов (локальных весов)
    # Нормализуем столбцы
    norm_matrix = matrix / matrix.sum(axis=0)
    # Усредняем строки для получения вектора приоритетов
    priorities = norm_matrix.mean(axis=1)

    # 2. Вычисление λ_max
    weighted_sum_vector = matrix @ priorities
    lambda_max = np.mean(weighted_sum_vector / priorities)

    # 3. Проверка согласованности
    if n > 2:
        ci = (lambda_max - n) / (n - 1)
        ri = RI_TABLE.get(n)
        cr = ci / ri
    else:  # для матриц 2х2 согласованность всегда идеальна
        ci = 0
        cr = 0

    # Форматирование для вывода
    print("-" * 50)
    print("Матрица парных сравнений:")
    # Печать заголовка
    print(f"{'':<15}", end="")
    for label in labels:
        print(f"{label:<15}", end="")
    print()
    # Печать строк
    for i, label in enumerate(labels):
        print(f"{label:<15}", end="")
        for val in matrix[i]:
            print(f"{val:<15.3f}", end="")
        print()
    print("-" * 50)

    print("\nРезультаты анализа:")
    print(f"Максимальное собственное число (λ_max): {lambda_max:.4f}")
    print(f"Индекс согласованности (CI): {ci:.4f}")
    if n > 2:
        print(f"Отношение согласованности (CR): {cr:.4f}")
        if cr < 0.1:
            print("--> Согласованность суждений приемлема (CR < 0.1)")
        else:
            print("--> ВНИМАНИЕ: Согласованность суждений нарушена (CR >= 0.1)")

    print("\nНормализованный вектор приоритетов (W):")
    for i, label in enumerate(labels):
        print(f"- {label}: {priorities[i]:.4f}")

    return {
        "priorities": priorities,
        "lambda_max": lambda_max,
        "ci": ci,
        "cr": cr
    }


# --- Данные для варианта 5 ---
stakeholders = ["Спонсор", "Тренер", "Хоккеисты"]
teams = ["Питтсбург", "Вашингтон", "Нью-Джерси"]

# Матрица сравнения критериев (стейкхолдеров)
stakeholder_matrix = np.array([
    [1, 3, 5],
    [1/3, 1, 3],
    [1/5, 1/3, 1]
])

# Матрицы сравнения альтернатив по каждому критерию
alt_sponsor_matrix = np.array([
    [1, 1/3, 2],
    [3, 1, 4],
    [1/2, 1/4, 1]
])

alt_coach_matrix = np.array([
    [1, 1/2, 3],
    [2, 1, 5],
    [1/3, 1/5, 1]
])

alt_player_matrix = np.array([
    [1, 4, 2],
    [1/4, 1, 1/2],
    [1/2, 2, 1]
])


# --- Выполнение расчетов ---

print("="*60)
print("ЭТАП 1: ОПРЕДЕЛЕНИЕ ВЕСОВ КРИТЕРИЕВ (МНЕНИЙ СТОРОН)")
print("="*60)
stakeholder_results = analyze_matrix(stakeholder_matrix, stakeholders)
criteria_weights = stakeholder_results["priorities"]

print("\n\n" + "="*60)
print("ЭТАП 2: ОЦЕНКА АЛЬТЕРНАТИВ ОТНОСИТЕЛЬНО КАЖДОГО КРИТЕРИЯ")
print("="*60)

print("\n\n--- 2.1. По критерию 'Мнение спонсора' ---")
sponsor_alt_results = analyze_matrix(alt_sponsor_matrix, teams)
sponsor_priorities = sponsor_alt_results["priorities"]

print("\n\n--- 2.2. По критерию 'Мнение тренера' ---")
coach_alt_results = analyze_matrix(alt_coach_matrix, teams)
coach_priorities = coach_alt_results["priorities"]

print("\n\n--- 2.3. По критерию 'Мнение хоккеистов' ---")
player_alt_results = analyze_matrix(alt_player_matrix, teams)
player_priorities = player_alt_results["priorities"]

# --- Иерархический синтез ---
print("\n\n" + "="*60)
print("ЭТАП 3: ИЕРАРХИЧЕСКИЙ СИНТЕЗ И ИТОГОВОЕ РАНЖИРОВАНИЕ")
print("="*60)

# Собираем матрицу локальных приоритетов
local_priorities_matrix = np.column_stack([
    sponsor_priorities,
    coach_priorities,
    player_priorities
])

print("\nМатрица локальных приоритетов:")
print(
    f"{'':<15}{stakeholders[0]:<15}{stakeholders[1]:<15}{stakeholders[2]:<15}")
for i, team in enumerate(teams):
    print(f"{team:<15}", end="")
    for p in local_priorities_matrix[i]:
        print(f"{p:<15.4f}", end="")
    print()

# Вычисляем глобальные приоритеты
global_scores = local_priorities_matrix @ criteria_weights

print("\nВектор весов критериев:")
print(criteria_weights)

print("\nИтоговые глобальные приоритеты (оценки):")
results = sorted(zip(teams, global_scores), key=lambda x: x[1], reverse=True)
for i, (team, score) in enumerate(results):
    print(f"{i+1}. {team}: {score:.4f}")

print("\n--- Вывод ---")
print(f"Наиболее предпочтительной альтернативой является '{results[0][0]}'.")
print("Эта команда имеет самые высокие шансы на выигрыш трофея согласно построенной модели,")
print("поскольку она получила наилучшие оценки с точки зрения самых влиятельных сторон - спонсора и тренерского штаба.")
