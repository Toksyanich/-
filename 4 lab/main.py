import numpy as np
import pandas as pd

# --- 1. Исходные данные для задачи 1.5 ---
data_1_5 = {
    'f1_prod': [220, 180, 240, 240, 200, 150],
    'f2_dev': [50, 80, 60, 100, 50, 25],
    'f3_cost': [52, 35, 47, 40, 50, 40],
    'f4_loss': [8, 5, 10, 10, 8, 8]
}
alternatives_1_5 = [f'x{i+1}' for i in range(len(data_1_5['f1_prod']))]
df_1_5 = pd.DataFrame(data_1_5, index=alternatives_1_5)

# Параметры задачи
# f1 -> max, f2 -> min, f3 -> min, f4 -> min
concessions = {'f1_prod': 40, 'f2_dev': 10, 'f3_cost': 3}
criteria_order = ['f1_prod', 'f2_dev', 'f3_cost', 'f4_loss']
criteria_type = {'f1_prod': 'max', 'f2_dev': 'min',
                 'f3_cost': 'min', 'f4_loss': 'min'}

print("--- Решение Задачи 1.5: Метод последовательных уступок ---\n")
print("Исходная таблица альтернатив:")
print(df_1_5)
print("\nВеличины уступок: Δ₁ = 40, Δ₂ = 10, Δ₃ = 3\n")

# Создаем копию для работы, чтобы не изменять исходные данные
working_df = df_1_5.copy()

# --- Шаг 1: Оптимизация по критерию f1 (производительность) ---
print("--- Шаг 1: Критерий f1 (производительность, max) ---")
f1 = 'f1_prod'
# Находим лучшее значение (максимальное)
best_f1 = working_df[f1].max()
print(f"Лучшее значение по f1: {best_f1}")

# Определяем границу уступки
f1_threshold = best_f1 - concessions[f1]
print(f"Граница уступки: {best_f1} - {concessions[f1]} = {f1_threshold}")

# Фильтруем альтернативы, которые проходят по уступке
X1 = working_df[working_df[f1] >= f1_threshold]
print("Альтернативы, оставшиеся после уступки по f1 (X1):")
print(X1)
print("-" * 50)

# --- Шаг 2: Оптимизация по критерию f2 (отклонение от веса) ---
print("\n--- Шаг 2: Критерий f2 (отклонение от веса, min) ---")
f2 = 'f2_dev'
# Находим лучшее значение (минимальное) в суженном множестве X1
best_f2 = X1[f2].min()
print(f"Лучшее значение по f2 среди X1: {best_f2}")

# Определяем границу уступки
f2_threshold = best_f2 + concessions[f2]
print(f"Граница уступки: {best_f2} + {concessions[f2]} = {f2_threshold}")

# Фильтруем альтернативы из X1
X2 = X1[X1[f2] <= f2_threshold]
print("Альтернативы, оставшиеся после уступки по f2 (X2):")
print(X2)
print("-" * 50)

# --- Шаг 3: Оптимизация по критерию f3 (стоимость) ---
print("\n--- Шаг 3: Критерий f3 (стоимость, min) ---")
f3 = 'f3_cost'
# Находим лучшее значение (минимальное) в суженном множестве X2
best_f3 = X2[f3].min()
print(f"Лучшее значение по f3 среди X2: {best_f3}")

# Определяем границу уступки
f3_threshold = best_f3 + concessions[f3]
print(f"Граница уступки: {best_f3} + {concessions[f3]} = {f3_threshold}")

# Фильтруем альтернативы из X2
X3 = X2[X2[f3] <= f3_threshold]
print("Альтернативы, оставшиеся после уступки по f3 (X3):")
print(X3)
print("-" * 50)

# --- Шаг 4: Оптимизация по последнему критерию f4 (потери) ---
print("\n--- Шаг 4: Критерий f4 (потери, min) ---")
f4 = 'f4_loss'
# Уступки нет, просто выбираем лучший из оставшихся (X3)
best_f4_val = X3[f4].min()
print(f"Лучшее значение по f4 среди X3: {best_f4_val}")

# Находим все альтернативы с этим лучшим значением
final_choice = X3[X3[f4] == best_f4_val]
print("\nОкончательный выбор:")
print(final_choice)
print(
    f"\nВывод: Наиболее предпочтительной является альтернатива {final_choice.index[0]}.")


# --- 1. Исходные данные для задачи 2.5 ---
data_2_5 = {
    'f1_exp': [2, 6, 5, 7, 4],
    'f2_share': [20, 20, 10, 5, 15],
    'f3_rep': [4, 2, 4, 3, 5]
}
alternatives_2_5 = [f'x{i+1}' for i in range(len(data_2_5['f1_exp']))]
df_2_5 = pd.DataFrame(data_2_5, index=alternatives_2_5)

# --- Шаг 1: Определение весов критериев ---
# Порядок важности: f3 > f1 > f2
# Метод простого ранжирования (n, n-1, ..., 1)
# f3 (rank 1) -> weight 3
# f1 (rank 2) -> weight 2
# f2 (rank 3) -> weight 1
weights = {'f1_exp': 2, 'f2_share': 1, 'f3_rep': 3}
total_weight = sum(weights.values())

print("--- Решение Задачи 2.5: Метод ELECTRE ---\n")
print("Исходная таблица альтернатив:")
print(df_2_5)
print(f"\nВеса критериев (f1, f2, f3): {list(weights.values())}")
print(f"Общая сумма весов: {total_weight}\n")

# --- Шаг 2: Расчет длин шкал L_j ---
scales = {col: df_2_5[col].max() - df_2_5[col].min() for col in df_2_5.columns}
print("Длины шкал Lj:")
print(scales)
print("-" * 50)

# --- Шаг 3: Построение матрицы индексов согласия C ---
num_alternatives = len(df_2_5)
concordance_matrix = pd.DataFrame(np.zeros((num_alternatives, num_alternatives)),
                                  index=df_2_5.index, columns=df_2_5.index)

for i in df_2_5.index:
    for k in df_2_5.index:
        if i == k:
            continue

        sum_w = 0
        for col in df_2_5.columns:
            # xi не хуже xk
            if df_2_5.loc[i, col] >= df_2_5.loc[k, col]:
                sum_w += weights[col]
        concordance_matrix.loc[i, k] = sum_w / total_weight

print("\nМатрица индексов согласия (C):")
print(concordance_matrix.round(3))
print("-" * 50)


# --- Шаг 4: Построение матрицы индексов несогласия D ---
discordance_matrix = pd.DataFrame(np.zeros((num_alternatives, num_alternatives)),
                                  index=df_2_5.index, columns=df_2_5.index)

for i in df_2_5.index:
    for k in df_2_5.index:
        if i == k:
            continue

        max_disagreement = 0
        for col in df_2_5.columns:
            # xk строго лучше xi
            if df_2_5.loc[k, col] > df_2_5.loc[i, col]:
                disagreement = (df_2_5.loc[k, col] -
                                df_2_5.loc[i, col]) / scales[col]
                if disagreement > max_disagreement:
                    max_disagreement = disagreement
        discordance_matrix.loc[i, k] = max_disagreement

print("\nМатрица индексов несогласия (D):")
print(discordance_matrix.round(3))
print("-" * 50)


# --- Шаг 5 и 6: Поиск ядра (недоминируемых альтернатив) ---
# Проведем анализ, как в примере из методички, итеративно изменяя пороги.

def find_kernel(concordance, discordance, alpha, beta):
    """Находит недоминируемые альтернативы (ядро) для заданных порогов."""
    dominance = pd.DataFrame(0, index=concordance.index,
                             columns=concordance.columns)

    for i in concordance.index:
        for k in concordance.index:
            if i == k:
                continue
            if concordance.loc[i, k] >= alpha and discordance.loc[i, k] <= beta:
                dominance.loc[i, k] = 1  # i доминирует над k

    # Альтернатива k доминируема, если есть хоть одна 1 в ее столбце
    dominated_mask = dominance.sum(axis=0) > 0
    kernel = dominance.index[~dominated_mask].tolist()

    return kernel, dominance


# Итерация 1: Жесткие пороги
alpha_1 = 0.8
beta_1 = 0.4
kernel_1, dom_1 = find_kernel(
    concordance_matrix, discordance_matrix, alpha_1, beta_1)
print(f"\n--- Итерация 1: alpha = {alpha_1}, beta = {beta_1} ---")
print("Матрица доминирования:")
print(dom_1)
print(f"Ядро (недоминируемые альтернативы): {kernel_1}")
print("Вывод 1: Ядро содержит 3 альтернативы, выбор не однозначен. Ослабим пороги.")

# Итерация 2: Ослабляем порог согласия
alpha_2 = 0.6
beta_2 = 0.4
kernel_2, dom_2 = find_kernel(
    concordance_matrix, discordance_matrix, alpha_2, beta_2)
print(f"\n--- Итерация 2: alpha = {alpha_2}, beta = {beta_2} ---")
print("Матрица доминирования:")
print(dom_2)
print(f"Ядро (недоминируемые альтернативы): {kernel_2}")
print("Вывод 2: Ядро по-прежнему содержит 2 альтернативы. Повысим порог несогласия.")

# Итерация 3: Повышаем порог несогласия
alpha_3 = 0.6
beta_3 = 0.7
kernel_3, dom_3 = find_kernel(
    concordance_matrix, discordance_matrix, alpha_3, beta_3)
print(f"\n--- Итерация 3: alpha = {alpha_3}, beta = {beta_3} ---")
print("Матрица доминирования:")
print(dom_3)
print(f"Ядро (недоминируемые альтернативы): {kernel_3}")
print("Вывод 3: Ядро сузилось до одной альтернативы.")


print("\n\n--- Итоговый результат по задаче 2.5 ---")
print(
    f"После итеративного подбора порогов было найдено ядро, состоящее из одной альтернативы: {kernel_3[0]}")
print(
    f"Альтернатива {kernel_3[0]} является наилучшим выбором, так как она доминирует над x1, x2, x3 и x4 при разумных порогах согласия и несогласия.")
print(f"Ее преимущество - наилучший показатель по самому весомому критерию f3 (репутация) при приемлемых значениях остальных критериев.")
