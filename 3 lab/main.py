import numpy as np
import pandas as pd
from itertools import combinations

print("="*80)
print("ЛАБОРАТОРНАЯ РАБОТА №3: МЕТОДЫ ПРИНЯТИЯ РЕШЕНИЙ")
print("Вариант 1.5 (Метод опорных множеств) и Вариант 2.5 (Метод взвешенной свертки)")
print("="*80)

# ============================================================================
# ЗАДАНИЕ 1.5: МЕТОД ОПОРНЫХ МНОЖЕСТВ
# ============================================================================
print("\n" + "="*80)
print("ЗАДАНИЕ 1.5: МЕТОД ОПОРНЫХ МНОЖЕСТВ")
print("="*80)

# Исходные данные
alternatives_15 = ['x1', 'x2', 'x3', 'x4']
criteria_15 = ['f1', 'f2', 'f3', 'f4', 'f5']
data_15 = np.array([
    [8, 5, 4, 6, 3],  # x1
    [2, 7, 1, 4, 5],  # x2
    [7, 5, 4, 2, 2],  # x3
    [2, 3, 1, 4, 3]   # x4
])

# Omega информация: {f1 ≻ f2, f4 ≻ f5, f2 ~ f5}
omega_info = "Ω = {f1 ≻ f2, f4 ≻ f5, f2 ~ f5}"
print(f"\nΩ-информация: {omega_info}")

# Создаем DataFrame для удобства
df_15 = pd.DataFrame(data_15, index=alternatives_15, columns=criteria_15)
print("\nИсходные данные:")
print(df_15)

# Функция для проверки доминирования по Парето


def pareto_dominates(x1, x2):
    """Проверяет, доминирует ли x1 над x2 по Парето"""
    return np.all(x1 >= x2) and np.any(x1 > x2)

# Выделение множества Парето


def find_pareto_set(data):
    """Находит множество Парето"""
    n = len(data)
    pareto_mask = np.ones(n, dtype=bool)

    for i in range(n):
        if not pareto_mask[i]:
            continue
        for j in range(n):
            if i == j:
                continue
            if pareto_dominates(data[j], data[i]):
                pareto_mask[i] = False
                break

    return pareto_mask


print("\n" + "-"*80)
print("ШАГ 1: ВЫДЕЛЕНИЕ МНОЖЕСТВА ПАРЕТО")
print("-"*80)

pareto_mask_15 = find_pareto_set(data_15)
pareto_alternatives_15 = [alternatives_15[i]
                          for i in range(len(alternatives_15)) if pareto_mask_15[i]]

print("\nСравнения по Парето:")
for i in range(len(alternatives_15)):
    for j in range(i+1, len(alternatives_15)):
        x_i = alternatives_15[i]
        x_j = alternatives_15[j]
        if pareto_dominates(data_15[i], data_15[j]):
            print(f"  {x_i} ≻_P {x_j}")
        elif pareto_dominates(data_15[j], data_15[i]):
            print(f"  {x_j} ≻_P {x_i}")
        else:
            print(f"  {x_i} и {x_j} несравнимы по Парето")

print(f"\nМножество Парето P(X) = {{{', '.join(pareto_alternatives_15)}}}")

# Функция для генерации опорных множеств


def generate_support_sets(y, omega_relations):
    """
    Генерирует опорные множества для оценки y
    omega_relations: список кортежей (i, j, relation_type)
    где relation_type: '>' для ≻, '~' для ~
    """
    equivalent_set = [y.copy()]
    improved_set = []

    # Обрабатываем соотношения из Ω
    # f1 ≻ f2: индексы 0 ≻ 1
    # f4 ≻ f5: индексы 3 ≻ 4
    # f2 ~ f5: индексы 1 ~ 4

    # Для эквивалентных оценок: меняем местами равнозначные критерии
    # f2 ~ f5 (индексы 1 и 4)
    y_equiv = y.copy()
    y_equiv[1], y_equiv[4] = y_equiv[4], y_equiv[1]
    if not np.array_equal(y_equiv, y):
        equivalent_set.append(y_equiv)

    # Для улучшенных оценок: используем информацию о превосходстве
    # f1 ≻ f2: переносим значение f2 в f1
    y_imp1 = y.copy()
    y_imp1[0] = y[1]
    improved_set.append(y_imp1)

    # f4 ≻ f5: переносим значение f5 в f4
    y_imp2 = y.copy()
    y_imp2[3] = y[4]
    improved_set.append(y_imp2)

    # Комбинации: f1 ≻ f2 и f4 ≻ f5
    y_imp3 = y.copy()
    y_imp3[0] = y[1]
    y_imp3[3] = y[4]
    improved_set.append(y_imp3)

    # Учитываем f2 ~ f5: можем сначала поменять, потом улучшить
    # Меняем f2 и f5, затем применяем f1 ≻ f2
    y_imp4 = y_equiv.copy()
    y_imp4[0] = y_equiv[1]
    improved_set.append(y_imp4)

    return equivalent_set, improved_set


print("\n" + "-"*80)
print("ШАГ 2: СРАВНЕНИЕ АЛЬТЕРНАТИВ МЕТОДОМ ОПОРНЫХ МНОЖЕСТВ")
print("-"*80)

# Сравниваем все пары из множества Парето
pareto_data = data_15[pareto_mask_15]
pareto_alts = [alternatives_15[i]
               for i, mask in enumerate(pareto_mask_15) if mask]

print(f"\nСравниваем альтернативы из P(X): {pareto_alts}")

for idx1 in range(len(pareto_alts)):
    for idx2 in range(idx1+1, len(pareto_alts)):
        alt1 = pareto_alts[idx1]
        alt2 = pareto_alts[idx2]
        y = pareto_data[idx1]
        z = pareto_data[idx2]

        print(f"\n{'='*60}")
        print(f"Сравнение {alt1} и {alt2}")
        print(f"{'='*60}")
        print(f"y = {alt1}: {y}")
        print(f"z = {alt2}: {z}")

        # Строим опорные множества для y относительно z
        print(f"\n--- Строим опорные множества для {alt1} ---")
        equiv_set_y, impr_set_y = generate_support_sets(y, None)

        print("\nY≈ (эквивалентные оценки):")
        for i, vec in enumerate(equiv_set_y, 1):
            print(f"  {i}. {vec}")

        print("\nY≻ (улучшенные оценки):")
        for i, vec in enumerate(impr_set_y, 1):
            print(f"  {i}. {vec}")

        # Проверяем доминирование
        y_dominates_z = False
        for vec in impr_set_y:
            if pareto_dominates(vec, z):
                print(
                    f"\n✓ Найдена улучшенная оценка {vec}, которая доминирует z по Парето")
                y_dominates_z = True
                break

        if not y_dominates_z:
            for vec in equiv_set_y:
                if pareto_dominates(vec, z):
                    print(
                        f"\n✓ Найдена эквивалентная оценка {vec}, которая доминирует z по Парето")
                    y_dominates_z = True
                    break

        # Строим опорные множества для z относительно y
        print(f"\n--- Строим опорные множества для {alt2} ---")
        equiv_set_z, impr_set_z = generate_support_sets(z, None)

        print("\nZ≈ (эквивалентные оценки):")
        for i, vec in enumerate(equiv_set_z, 1):
            print(f"  {i}. {vec}")

        print("\nZ≻ (улучшенные оценки):")
        for i, vec in enumerate(impr_set_z, 1):
            print(f"  {i}. {vec}")

        z_dominates_y = False
        for vec in impr_set_z:
            if pareto_dominates(vec, y):
                print(
                    f"\n✓ Найдена улучшенная оценка {vec}, которая доминирует y по Парето")
                z_dominates_y = True
                break

        if not z_dominates_y:
            for vec in equiv_set_z:
                if pareto_dominates(vec, y):
                    print(
                        f"\n✓ Найдена эквивалентная оценка {vec}, которая доминирует y по Парето")
                    z_dominates_y = True
                    break

        print("\n" + "="*60)
        if y_dominates_z:
            print(f"ВЫВОД: {alt1} ≻_Ω {alt2}")
        elif z_dominates_y:
            print(f"ВЫВОД: {alt2} ≻_Ω {alt1}")
        else:
            print(f"ВЫВОД: {alt1} и {alt2} несравнимы с учетом Ω-информации")
        print("="*60)

# ============================================================================
# ЗАДАНИЕ 2.5: МЕТОД ВЗВЕШЕННОЙ СВЕРТКИ КРИТЕРИЕВ
# ============================================================================
print("\n\n" + "="*80)
print("ЗАДАНИЕ 2.5: МЕТОД ВЗВЕШЕННОЙ СВЕРТКИ КРИТЕРИЕВ")
print("="*80)

# Исходные данные
alternatives_25 = ['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7']
criteria_25 = ['f1', 'f2', 'f3', 'f4']
data_25 = np.array([
    [40, 8, 3, 3],  # x1
    [30, 8, 5, 3],  # x2
    [40, 6, 2, 4],  # x3
    [60, 6, 5, 5],  # x4
    [45, 7, 1, 3],  # x5
    [25, 8, 4, 3],  # x6
    [55, 6, 3, 4]   # x7
])

# Направления оптимизации (True = max, False = min)
maximize = [False, False, True, True]  # f1→min, f2→min, f3→max, f4→max

print("\nКритерии:")
print("  f1 → min (затраты на внедрение, тыс. ден.ед)")
print("  f2 → min (срок ввода в эксплуатацию, месяцев)")
print("  f3 → max (удобство в эксплуатации, баллы)")
print("  f4 → max (срок гарантийного обслуживания, лет)")

print("\nПорядок важности критериев: f1 ≻ f2 ≻ f4 ≻ f3")

df_25 = pd.DataFrame(data_25, index=alternatives_25, columns=criteria_25)
print("\nИсходные данные:")
print(df_25)

# ШАГ 1: Определение весов критериев
print("\n" + "-"*80)
print("ШАГ 1: ОПРЕДЕЛЕНИЕ ВЕСОВ КРИТЕРИЕВ (пропорциональный метод)")
print("-"*80)

# Порядок: f1 ≻ f2 ≻ f4 ≻ f3
# Предположим: f1 в 4 раза важнее f3 (наименее важный)
# f2 в 3 раза важнее f3
# f4 в 2 раза важнее f3
# f3 = w, f4 = 2w, f2 = 3w, f1 = 4w
# Сумма = 10w = 1, w = 0.1

weights = np.array([0.4, 0.3, 0.1, 0.2])  # f1, f2, f3, f4

print("\nКоэффициенты важности:")
for i, (crit, w) in enumerate(zip(criteria_25, weights)):
    print(f"  {crit}: λ = {w:.3f}")
print(f"  Сумма: {weights.sum():.3f}")

# ШАГ 2: Нормировка критериев
print("\n" + "-"*80)
print("ШАГ 2: НОРМИРОВКА КРИТЕРИЕВ")
print("-"*80)

# Преобразуем минимизируемые критерии в максимизируемые
data_transformed = data_25.copy().astype(float)
for j in range(len(criteria_25)):
    if not maximize[j]:
        # Инвертируем критерий (берем обратное значение или отрицание)
        data_transformed[:, j] = -data_transformed[:, j]

# Нормировка: (x - min) / (max - min)
data_normalized = np.zeros_like(data_transformed)
for j in range(len(criteria_25)):
    min_val = data_transformed[:, j].min()
    max_val = data_transformed[:, j].max()
    if max_val - min_val > 0:
        data_normalized[:, j] = (
            data_transformed[:, j] - min_val) / (max_val - min_val)
    else:
        data_normalized[:, j] = 1.0

df_normalized = pd.DataFrame(data_normalized, index=alternatives_25,
                             columns=[f"{c}'" for c in criteria_25])
print("\nНормированные критериальные оценки:")
print(df_normalized.round(3))

# ШАГ 3: Применение сверток
print("\n" + "-"*80)
print("ШАГ 3: ПРИМЕНЕНИЕ МЕТОДОВ СВЕРТКИ")
print("-"*80)

# 3.1 Аддитивная свертка
print("\n--- 3.1. Аддитивная свертка ---")
W_add = np.sum(weights * data_normalized, axis=1)
print("\nW_add(x_i):")
for alt, val in zip(alternatives_25, W_add):
    print(f"  {alt}: {val:.4f}")

best_add = alternatives_25[np.argmax(W_add)]
print(
    f"\nЛучшая альтернатива (аддитивная свертка): {best_add} = {W_add.max():.4f}")

# 3.2 Мультипликативная свертка
print("\n--- 3.2. Мультипликативная свертка ---")
# Избегаем нулей, добавляя малое число
data_mult = data_normalized + 1e-10
W_mult = np.prod(data_mult ** weights, axis=1)
print("\nW_mult(x_i):")
for alt, val in zip(alternatives_25, W_mult):
    print(f"  {alt}: {val:.4f}")

best_mult = alternatives_25[np.argmax(W_mult)]
print(
    f"\nЛучшая альтернатива (мультипликативная свертка): {best_mult} = {W_mult.max():.4f}")

# 3.3 Расстояние до идеала
print("\n--- 3.3. Расстояние до идеала ---")
# Идеальная точка - лучшие значения по каждому критерию
ideal = data_normalized.max(axis=0)
print(f"\nИдеальная точка: {ideal}")

# Вспомогательные критерии (отклонения от идеала)
data_deviation = ideal - data_normalized
df_deviation = pd.DataFrame(data_deviation, index=alternatives_25,
                            columns=[f"f̃{i+1}" for i in range(len(criteria_25))])
print("\nОтклонения от идеала:")
print(df_deviation.round(3))

# Взвешенное расстояние
W_ideal = np.sqrt(np.sum(weights * (data_deviation ** 2), axis=1))
print("\nW_ideal(x_i) (минимизируется):")
for alt, val in zip(alternatives_25, W_ideal):
    print(f"  {alt}: {val:.4f}")

best_ideal = alternatives_25[np.argmin(W_ideal)]
print(
    f"\nЛучшая альтернатива (расстояние до идеала): {best_ideal} = {W_ideal.min():.4f}")

# Проверка Парето-оптимальности
print("\n" + "-"*80)
print("ПРОВЕРКА ПАРЕТО-ОПТИМАЛЬНОСТИ РЕШЕНИЙ")
print("-"*80)

pareto_mask_25 = find_pareto_set(data_normalized)
pareto_alternatives_25 = [alternatives_25[i]
                          for i in range(len(alternatives_25)) if pareto_mask_25[i]]

print(f"\nМножество Парето P(X) = {{{', '.join(pareto_alternatives_25)}}}")

solutions = {
    'Аддитивная свертка': best_add,
    'Мультипликативная свертка': best_mult,
    'Расстояние до идеала': best_ideal
}

print("\nПроверка решений:")
for method, solution in solutions.items():
    is_pareto = solution in pareto_alternatives_25
    status = "✓ Парето-оптимально" if is_pareto else "✗ НЕ Парето-оптимально"
    print(f"  {method}: {solution} - {status}")

# Итоговая таблица
print("\n" + "="*80)
print("ИТОГОВАЯ СВОДКА")
print("="*80)

results_df = pd.DataFrame({
    'Альтернатива': alternatives_25,
    'W_add': W_add.round(4),
    'W_mult': W_mult.round(4),
    'W_ideal': W_ideal.round(4),
    'Парето': ['Да' if m else 'Нет' for m in pareto_mask_25]
})
print("\n", results_df.to_string(index=False))

print("\n" + "="*80)
print("КОНЕЦ РЕШЕНИЯ")
print("="*80)
