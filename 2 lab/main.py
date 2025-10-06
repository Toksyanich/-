import numpy as np
from scipy.optimize import linprog
import pandas as pd

print("="*80)
print("ЛАБОРАТОРНАЯ РАБОТА №2 - МЕТОДЫ ПРИНЯТИЯ РЕШЕНИЙ")
print("="*80)

# =============================================================================
# ЗАДАЧА 1.5 - КЛАССИЧЕСКАЯ ТРАНСПОРТНАЯ ЗАДАЧА
# =============================================================================
print("\n" + "="*80)
print("ЗАДАЧА 1.5 - КЛАССИЧЕСКАЯ ТРАНСПОРТНАЯ ЗАДАЧА")
print("="*80)

# Исходные данные
costs_1_5 = np.array([
    [1, 2, 3, 1, 4],  # S1
    [6, 3, 4, 5, 2],  # S2
    [8, 2, 1, 9, 3]   # S3
])

supply = np.array([180, 220, 100])  # Запасы на складах
demand = np.array([120, 80, 160, 90, 50])  # Потребности

print("\nМатрица затрат:")
print(pd.DataFrame(costs_1_5,
                   index=['S1', 'S2', 'S3'],
                   columns=['D1', 'D2', 'D3', 'D4', 'D5']))
print(f"\nЗапасы: {supply}, Сумма = {supply.sum()}")
print(f"Потребности: {demand}, Сумма = {demand.sum()}")


def solve_transport_problem(costs, supply, demand, constraints=None):
    """
    Решает транспортную задачу
    constraints: список кортежей (i, j, lower, upper) для ограничений x[i,j]
    """
    m, n = costs.shape

    # Формируем вектор коэффициентов целевой функции
    c = costs.flatten()

    # Ограничения-равенства (потребности)
    A_eq = []
    b_eq = []

    # Каждый потребитель должен получить свою потребность
    for j in range(n):
        row = np.zeros(m * n)
        for i in range(m):
            row[i * n + j] = 1
        A_eq.append(row)
        b_eq.append(demand[j])

    # Каждый поставщик не может отправить больше своего запаса
    for i in range(m):
        row = np.zeros(m * n)
        for j in range(n):
            row[i * n + j] = 1
        A_eq.append(row)
        b_eq.append(supply[i])

    A_eq = np.array(A_eq)
    b_eq = np.array(b_eq)

    # Границы переменных
    bounds = [(0, None) for _ in range(m * n)]

    # Дополнительные ограничения
    A_ub = []
    b_ub = []

    if constraints:
        for constraint in constraints:
            i, j, lower, upper = constraint
            idx = i * n + j

            if upper is not None:
                # x[i,j] <= upper
                row = np.zeros(m * n)
                row[idx] = 1
                A_ub.append(row)
                b_ub.append(upper)

            if lower is not None:
                # x[i,j] >= lower => -x[i,j] <= -lower
                row = np.zeros(m * n)
                row[idx] = -1
                A_ub.append(row)
                b_ub.append(-lower)

    A_ub = np.array(A_ub) if A_ub else None
    b_ub = np.array(b_ub) if b_ub else None

    # Решаем задачу
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                     bounds=bounds, method='highs')

    return result


# Задание 1
print("\n" + "-"*80)
print("ЗАДАНИЕ 1: План поставок с минимальными затратами")
print("-"*80)

result1 = solve_transport_problem(costs_1_5, supply, demand)

if result1.success:
    plan = result1.x.reshape(3, 5)
    print("\nОптимальный план перевозок:")
    df_plan = pd.DataFrame(plan,
                           index=['S1', 'S2', 'S3'],
                           columns=['D1', 'D2', 'D3', 'D4', 'D5'])
    print(df_plan.round(2))
    print(f"\nМинимальные затраты: {result1.fun:.2f} ден. ед.")
else:
    print("Решение не найдено!")

# Задание 2
print("\n" + "-"*80)
print("ЗАДАНИЕ 2: С дополнительными условиями")
print("-"*80)
print("Условия:")
print("- S1 -> D2 запрещена")
print("- S2 -> D5 запрещена")
print("- S2 -> D1 >= 60")

# Модифицируем матрицу затрат (большое число для запрещенных маршрутов)
costs_1_5_mod = costs_1_5.copy()
costs_1_5_mod[0, 1] = 1e6  # S1 -> D2 запрещена
costs_1_5_mod[1, 4] = 1e6  # S2 -> D5 запрещена

# Добавляем ограничение S2 -> D1 >= 60
constraints = [(1, 0, 60, None)]  # (i, j, lower, upper)

result2 = solve_transport_problem(costs_1_5_mod, supply, demand, constraints)

if result2.success:
    plan2 = result2.x.reshape(3, 5)
    print("\nОптимальный план перевозок с ограничениями:")
    df_plan2 = pd.DataFrame(plan2,
                            index=['S1', 'S2', 'S3'],
                            columns=['D1', 'D2', 'D3', 'D4', 'D5'])
    print(df_plan2.round(2))
    print(f"\nМинимальные затраты: {result2.fun:.2f} ден. ед.")
    print(f"Увеличение затрат: {result2.fun - result1.fun:.2f} ден. ед.")
else:
    print("Решение не найдено!")

# =============================================================================
# ЗАДАЧА 2.5 - ЗАДАЧА О НАЗНАЧЕНИЯХ
# =============================================================================
print("\n\n" + "="*80)
print("ЗАДАЧА 2.5 - ЗАДАЧА О НАЗНАЧЕНИЯХ")
print("="*80)

incompatibility = np.array([
    [13, 10, 7, 9, 9, 12, 13, 10],   # Б1
    [10, 10, 11, 12, 10, 11, 11, 11],  # Б2
    [13, 15, 15, 14, 12, 16, 16, 16],  # Б3
    [13, 18, 14, 14, 11, 9, 18, 14],  # Б4
    [8, 6, 7, 8, 12, 11, 9, 8],       # Б5
    [16, 15, 17, 17, 11, 11, 16, 13],  # Б6
    [7, 6, 12, 8, 11, 6, 9, 7],       # Б7
    [17, 15, 12, 14, 12, 17, 14, 15]  # Б8
])

print("\nМатрица индексов несовместимости:")
print(pd.DataFrame(incompatibility,
                   index=['Б1', 'Б2', 'Б3', 'Б4', 'Б5', 'Б6', 'Б7', 'Б8'],
                   columns=['И1', 'И2', 'И3', 'И4', 'И5', 'И6', 'И7', 'И8']))


def solve_assignment_problem(costs, forbidden_pairs=None):
    """
    Решает задачу о назначениях
    forbidden_pairs: список кортежей (i, j) запрещенных пар
    """
    n = costs.shape[0]

    # Модифицируем матрицу для запрещенных пар
    costs_mod = costs.copy()
    if forbidden_pairs:
        for i, j in forbidden_pairs:
            costs_mod[i, j] = 1e6

    # Формируем вектор коэффициентов целевой функции
    c = costs_mod.flatten()

    # Ограничения-равенства
    A_eq = []
    b_eq = []

    # Каждый инженер назначается ровно одному бригадиру
    for j in range(n):
        row = np.zeros(n * n)
        for i in range(n):
            row[i * n + j] = 1
        A_eq.append(row)
        b_eq.append(1)

    # Каждый бригадир получает ровно одного инженера
    for i in range(n):
        row = np.zeros(n * n)
        for j in range(n):
            row[i * n + j] = 1
        A_eq.append(row)
        b_eq.append(1)

    A_eq = np.array(A_eq)
    b_eq = np.array(b_eq)

    # Границы: переменные должны быть 0 или 1
    bounds = [(0, 1) for _ in range(n * n)]

    # Решаем задачу
    result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds,
                     method='highs')

    return result


# Задание 1
print("\n" + "-"*80)
print("ЗАДАНИЕ 1: Оптимальное распределение пар")
print("-"*80)

result_assign1 = solve_assignment_problem(incompatibility)

if result_assign1.success:
    assignment = result_assign1.x.reshape(8, 8)

    print("\nОптимальное распределение:")
    pairs = []
    max_index = 0
    for i in range(8):
        for j in range(8):
            if assignment[i, j] > 0.5:  # Учитываем погрешность
                pairs.append((i+1, j+1, incompatibility[i, j]))
                max_index = max(max_index, incompatibility[i, j])
                print(
                    f"Бригадир Б{i+1} - Инженер И{j+1}, индекс несовместимости: {incompatibility[i, j]}")

    print(f"\nСуммарный индекс несовместимости: {result_assign1.fun:.0f}")
    print(f"Наихудший индекс в отобранных парах: {max_index}")
else:
    print("Решение не найдено!")

# Задание 2
print("\n" + "-"*80)
print("ЗАДАНИЕ 2: Бригадир Б5 не работает с инженером И2")
print("-"*80)

# Б5 - это индекс 4, И2 - это индекс 1
forbidden_pairs = [(4, 1)]

result_assign2 = solve_assignment_problem(incompatibility, forbidden_pairs)

if result_assign2.success:
    assignment2 = result_assign2.x.reshape(8, 8)

    print("\nНовое распределение:")
    max_index2 = 0
    for i in range(8):
        for j in range(8):
            if assignment2[i, j] > 0.5:
                max_index2 = max(max_index2, incompatibility[i, j])
                print(
                    f"Бригадир Б{i+1} - Инженер И{j+1}, индекс несовместимости: {incompatibility[i, j]}")

    print(f"\nСуммарный индекс несовместимости: {result_assign2.fun:.0f}")
    print(
        f"Увеличение суммарного индекса: {result_assign2.fun - result_assign1.fun:.0f}")
else:
    print("Решение не найдено!")

# =============================================================================
# ЗАДАЧА 3.5 - ТРАНСПОРТНАЯ ЗАДАЧА С ПРОМЕЖУТОЧНЫМИ ПУНКТАМИ
# =============================================================================
print("\n\n" + "="*80)
print("ЗАДАЧА 3.5 - ТРАНСПОРТНАЯ ЗАДАЧА С ПРОМЕЖУТОЧНЫМИ ПУНКТАМИ")
print("="*80)

# Исходные данные
demand_consumers = np.array([135, 110, 215, 80])  # A, B, C, D

# Издержки: завод -> склад
factory_to_warehouse = np.array([
    [37, 40],  # Северный завод -> Склад1, Склад2
    [32, 38]   # Южный завод -> Склад1, Склад2
])

# Издержки: склад -> потребитель
warehouse_to_consumer = np.array([
    [12, 9, 18, 16],   # Склад1 -> A, B, C, D
    [14, 16, 7, 13]    # Склад2 -> A, B, C, D
])

# Издержки: завод -> потребитель (напрямую)
factory_to_consumer = np.array([
    [70, 58, 52, 68],  # Северный завод -> A, B, C, D
    [60, 51, 56, 57]   # Южный завод -> A, B, C, D
])

print("\nИздержки завод -> склад:")
print(pd.DataFrame(factory_to_warehouse,
                   index=['Северный', 'Южный'],
                   columns=['Склад1', 'Склад2']))

print("\nИздержки склад -> потребитель:")
print(pd.DataFrame(warehouse_to_consumer,
                   index=['Склад1', 'Склад2'],
                   columns=['A', 'B', 'C', 'D']))

print("\nИздержки завод -> потребитель (прямые):")
print(pd.DataFrame(factory_to_consumer,
                   index=['Северный', 'Южный'],
                   columns=['A', 'B', 'C', 'D']))


def solve_transshipment_problem(factory_supply, demand_consumers,
                                factory_to_warehouse, warehouse_to_consumer,
                                factory_to_consumer):
    """
    Решает транспортную задачу с промежуточными пунктами
    """
    n_factories = 2
    n_warehouses = 2
    n_consumers = 4

    # Переменные:
    # x[0:4] - завод i -> склад j (2*2 = 4)
    # x[4:12] - склад i -> потребитель j (2*4 = 8)
    # x[12:20] - завод i -> потребитель j напрямую (2*4 = 8)
    # x[20:22] - остаток на складе (2)

    n_vars = 4 + 8 + 8 + 2

    # Целевая функция
    c = np.zeros(n_vars)

    # Затраты завод -> склад
    idx = 0
    for i in range(n_factories):
        for j in range(n_warehouses):
            c[idx] = factory_to_warehouse[i, j]
            idx += 1

    # Затраты склад -> потребитель
    for i in range(n_warehouses):
        for j in range(n_consumers):
            c[idx] = warehouse_to_consumer[i, j]
            idx += 1

    # Затраты завод -> потребитель напрямую
    for i in range(n_factories):
        for j in range(n_consumers):
            c[idx] = factory_to_consumer[i, j]
            idx += 1

    # Остатки на складах - нулевая стоимость
    c[20:22] = 0

    # Ограничения-равенства
    A_eq = []
    b_eq = []

    # Баланс заводов
    for i in range(n_factories):
        row = np.zeros(n_vars)
        # Отправка на склады
        for j in range(n_warehouses):
            row[i * n_warehouses + j] = 1
        # Прямая отправка потребителям
        for j in range(n_consumers):
            row[12 + i * n_consumers + j] = 1
        A_eq.append(row)
        b_eq.append(factory_supply[i])

    # Баланс складов
    for j in range(n_warehouses):
        row = np.zeros(n_vars)
        # Приход с заводов
        for i in range(n_factories):
            row[i * n_warehouses + j] = 1
        # Отправка потребителям
        for k in range(n_consumers):
            row[4 + j * n_consumers + k] = -1
        # Остаток
        row[20 + j] = -1
        A_eq.append(row)
        b_eq.append(0)

    # Спрос потребителей
    for k in range(n_consumers):
        row = np.zeros(n_vars)
        # Приход со складов
        for j in range(n_warehouses):
            row[4 + j * n_consumers + k] = 1
        # Прямая поставка с заводов
        for i in range(n_factories):
            row[12 + i * n_consumers + k] = 1
        A_eq.append(row)
        b_eq.append(demand_consumers[k])

    A_eq = np.array(A_eq)
    b_eq = np.array(b_eq)

    bounds = [(0, None) for _ in range(n_vars)]

    result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

    return result


# Задание 1
print("\n" + "-"*80)
print("ЗАДАНИЕ 1: План перевозок с минимальными издержками")
print("-"*80)

factory_supply1 = np.array([300, 240])
print(
    f"\nЗапасы заводов: Северный = {factory_supply1[0]}, Южный = {factory_supply1[1]}")
print(f"Потребности: {demand_consumers}, Сумма = {demand_consumers.sum()}")

result_trans1 = solve_transshipment_problem(
    factory_supply1, demand_consumers,
    factory_to_warehouse, warehouse_to_consumer,
    factory_to_consumer
)

if result_trans1.success:
    x = result_trans1.x

    print("\nЗавод -> Склад:")
    for i, factory in enumerate(['Северный', 'Южный']):
        for j in range(2):
            val = x[i * 2 + j]
            if val > 0.01:
                print(f"  {factory} -> Склад{j+1}: {val:.2f}")

    print("\nСклад -> Потребитель:")
    for j in range(2):
        for k, consumer in enumerate(['A', 'B', 'C', 'D']):
            val = x[4 + j * 4 + k]
            if val > 0.01:
                print(f"  Склад{j+1} -> {consumer}: {val:.2f}")

    print("\nЗавод -> Потребитель (напрямую):")
    for i, factory in enumerate(['Северный', 'Южный']):
        for k, consumer in enumerate(['A', 'B', 'C', 'D']):
            val = x[12 + i * 4 + k]
            if val > 0.01:
                print(f"  {factory} -> {consumer}: {val:.2f}")

    print("\nОстатки на складах:")
    print(f"  Склад1: {x[20]:.2f}")
    print(f"  Склад2: {x[21]:.2f}")

    print(f"\nМинимальные издержки: {result_trans1.fun:.2f} ден. ед.")
else:
    print("Решение не найдено!")

# Задание 2
print("\n" + "-"*80)
print("ЗАДАНИЕ 2: Северный завод выпускает дополнительно 50 единиц")
print("-"*80)

factory_supply2 = np.array([350, 240])
print(
    f"\nНовые запасы заводов: Северный = {factory_supply2[0]}, Южный = {factory_supply2[1]}")

result_trans2 = solve_transshipment_problem(
    factory_supply2, demand_consumers,
    factory_to_warehouse, warehouse_to_consumer,
    factory_to_consumer
)

if result_trans2.success:
    x2 = result_trans2.x

    print("\nЗавод -> Склад:")
    for i, factory in enumerate(['Северный', 'Южный']):
        for j in range(2):
            val = x2[i * 2 + j]
            if val > 0.01:
                print(f"  {factory} -> Склад{j+1}: {val:.2f}")

    print("\nСклад -> Потребитель:")
    for j in range(2):
        for k, consumer in enumerate(['A', 'B', 'C', 'D']):
            val = x2[4 + j * 4 + k]
            if val > 0.01:
                print(f"  Склад{j+1} -> {consumer}: {val:.2f}")

    print("\nЗавод -> Потребитель (напрямую):")
    for i, factory in enumerate(['Северный', 'Южный']):
        for k, consumer in enumerate(['A', 'B', 'C', 'D']):
            val = x2[12 + i * 4 + k]
            if val > 0.01:
                print(f"  {factory} -> {consumer}: {val:.2f}")

    print("\nОстатки на складах после выполнения плана поставок:")
    print(f"  Склад1: {x2[20]:.2f}")
    print(f"  Склад2: {x2[21]:.2f}")
    print(f"  Общий остаток: {x2[20] + x2[21]:.2f}")

    print(f"\nМинимальные издержки: {result_trans2.fun:.2f} ден. ед.")
    print(
        f"Изменение издержек: {result_trans2.fun - result_trans1.fun:.2f} ден. ед.")
else:
    print("Решение не найдено!")

print("\n" + "="*80)
print("РАБОТА ЗАВЕРШЕНА")
print("="*80)
