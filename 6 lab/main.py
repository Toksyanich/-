import numpy as np
import pandas as pd

# ==========================
# Общие вспомогательные функции
# ==========================

# ---- Задачи блока 1 (со стохастическим риском) ----


def probabilistic_guarantee(Y, p, t_values):
    """
    Критерий вероятностной гарантии:
    H(x, t0) = P{ y(x,z) >= t0 }.
    Возвращает словарь t0 -> вектор значений H(x, t0) для всех альтернатив.
    """
    results = {}
    for t in t_values:
        results[t] = ((Y >= t) * p).sum(axis=1)
    return results


def probabilistic_guaranteed_result(Y, p, P_values):
    """
    Критерий наибольшего вероятностно-гарантированного результата.
    Для каждой альтернативы x:
      t_P0(x) = max{ t из множества значений выигрыша | H(x, t) >= P0 }.
    Возвращает словарь P0 -> вектор t_P0(x).
    """
    res = {}
    m, n = Y.shape
    for P0 in P_values:
        tP = np.full(m, np.nan)
        for i in range(m):
            payoffs = np.unique(np.sort(Y[i]))
            best = -np.inf
            for t in payoffs:
                H = ((Y[i] >= t) * p).sum()
                if H >= P0 and t > best:
                    best = t
            tP[i] = np.nan if best == -np.inf else best
        res[P0] = tP
    return res


def mean_and_std(Y, p):
    """
    Критерий «среднее – разброс».
    Возвращает векторы M[y(x)] и σ[y(x)].
    """
    EY = (Y * p).sum(axis=1)
    EY2 = (Y ** 2 * p).sum(axis=1)
    var = EY2 - EY ** 2
    var[var < 0] = 0.0
    return EY, np.sqrt(var)


def expected_utility(Y, p, u):
    """
    Критерий ожидаемой полезности:
    U(x) = Σ p_j * u(y(x, z_j))
    """
    return (u(Y) * p).sum(axis=1)


# ---- Задачи блока 2 (полная неопределённость) ----

def wald(Y):
    """Критерий Вальда (максимин): W_D(x) = min_j y(x, z_j)."""
    return Y.min(axis=1)


def hurwicz(Y, gamma):
    """
    Критерий Гурвица:
    W_H(x) = γ * min_j y + (1 - γ) * max_j y
    """
    mins = Y.min(axis=1)
    maxs = Y.max(axis=1)
    return gamma * mins + (1 - gamma) * maxs


def laplace(Y):
    """
    Принцип недостаточного обоснования (Бернулли–Лаплас):
    W_L(x) = средний выигрыш по всем состояниям.
    """
    return Y.mean(axis=1)


def hurwicz_laplace_combined(Y, gamma):
    """
    Комбинация Гурвица и принципа недостаточного обоснования.
    Делим исходы на «неблагоприятные» и «благоприятные» относительно порога y_γ
    и усредняем их с весами γ и (1-γ).
    """
    ymin = Y.min()
    ymax = Y.max()
    y_gamma = gamma * ymin + (1 - gamma) * ymax

    m, n = Y.shape
    res = np.zeros(m)

    for i in range(m):
        vals = Y[i]
        unfavorable = vals[vals < y_gamma]
        favorable = vals[vals >= y_gamma]

        if len(unfavorable) == 0 or len(favorable) == 0:
            # если все исходы только благоприятные или только неблагоприятные –
            # используем критерий Лапласа
            res[i] = vals.mean()
        else:
            q_avg = unfavorable.mean()
            r_avg = favorable.mean()
            res[i] = gamma * q_avg + (1 - gamma) * r_avg

    return res


def savage(Y):
    """
    Критерий Сэвиджа:
    1) считаем матрицу сожалений r_ij = max_i y_ij - y_ij;
    2) W_S(x) = max_j r_ij (минимизировать!).
    Возвращает вектор W_S и матрицу сожалений.
    """
    max_by_state = Y.max(axis=0, keepdims=True)
    regrets = max_by_state - Y
    W = regrets.max(axis=1)
    return W, regrets


def khomenyuk(Y):
    """
    Критерий Хоменюка:
    1) считаем матрицу сожалений;
    2) оцениваем псевдо-вероятности состояний как пропорциональные суммарным сожалениям;
    3) W_K(x) = Σ p̂(z_j) * y(x, z_j).
    Возвращает оценки W_K(x), вектор p̂(z_j) и матрицу сожалений.
    """
    max_by_state = Y.max(axis=0, keepdims=True)
    regrets = max_by_state - Y
    sum_by_state = regrets.sum(axis=0)
    total = sum_by_state.sum()
    p_hat = sum_by_state / total
    W = (Y * p_hat).sum(axis=1)
    return W, p_hat, regrets


# ==========================
# Задача 1.5
# ==========================

def solve_task_1_5():
    print("===== Задача 1.5 (вероятностная модель) =====\n")

    # Состояния внешней среды – реальные проценты брака
    q_values = np.array([0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4])  # %
    p = np.array([0.16, 0.30, 0.19, 0.13, 0.11, 0.07, 0.04])  # вероятности

    # Альтернативы – выбор потребителя
    consumers = np.array(["A", "B", "C", "D"])
    prices = np.array([3500, 3100, 2700, 2300])  # цена поставки партии, д.е.
    qmax = np.array([0.8, 1.0, 1.2, 1.4])        # допущенный процент брака, %
    # затраты на выпуск партии, д.е.
    production_cost = 1000

    m, n = len(consumers), len(q_values)

    # Матрица выигрышей Y: прибыль = цена - себестоимость - штраф
    Y = np.zeros((m, n))
    for i in range(m):
        for j in range(n):
            # превышение брака, % (в абсолютных пунктах)
            excess = max(0.0, q_values[j] - qmax[i])
            points = int(round(excess / 0.1))            # число пунктов (0.1%)
            penalty = 400 * points                       # штраф
            Y[i, j] = prices[i] - production_cost - penalty

    payoff_table = pd.DataFrame(
        Y,
        index=consumers,
        columns=[f"{q:.1f}%" for q in q_values]
    )
    print("Таблица выигрышей (прибыль, д.е.):")
    print(payoff_table, "\n")

    # ----- а) Критерий вероятностной гарантии -----
    t_values = [1300, 1500, 1800]
    H = probabilistic_guarantee(Y, p, t_values)

    print("Критерий вероятностной гарантии H(x, t0):")
    for t0 in t_values:
        print(f"t0 = {t0} д.е.:")
        for i, cons in enumerate(consumers):
            print(f"  {cons}: H = {H[t0][i]:.2f}")
        best_idx = np.argmax(H[t0])
        print(
            f"  -> Наибольшая вероятность у потребителя {consumers[best_idx]}\n")

    # ----- б) Критерий наибольшего вероятностно-гарантированного результата -----
    P_values = [0.8, 0.9]
    tP = probabilistic_guaranteed_result(Y, p, P_values)

    print("Критерий наибольшего вероятностно-гарантированного результата t_P0(x):")
    for P0 in P_values:
        print(f"P0 = {P0}:")
        for i, cons in enumerate(consumers):
            val = tP[P0][i]
            print(f"  {cons}: t_P0 = {val:.0f} д.е.")
        best_idx = np.nanargmax(tP[P0])
        print(f"  -> Максимальный t_P0 у потребителя {consumers[best_idx]}\n")

    # ----- в) Критерий «среднее – разброс» -----
    EY, SD = mean_and_std(Y, p)
    print("Критерий «среднее – разброс»:")
    for i, cons in enumerate(consumers):
        print(f"{cons}: M[y] = {EY[i]:.2f} д.е., σ[y] = {SD[i]:.2f} д.е.")
    print("  (Выбор зависит от отношения ЛПР к риску; по среднему выигрышу лидер – потребитель",
          consumers[np.argmax(EY)], ".)\n")

    # ----- г) Критерий ожидаемой полезности -----
    def u(y):
        # Функция полезности из условия задачи
        return 0.3 * np.log(0.01 * y + 1.0)

    EU = expected_utility(Y, p, u)
    print("Критерий ожидаемой полезности U(x):")
    for i, cons in enumerate(consumers):
        print(f"{cons}: U = {EU[i]:.4f}")
    best_idx = np.argmax(EU)
    print(
        f"\nС точки зрения ожидаемой полезности наибольший приоритет имеет потребитель {consumers[best_idx]}.\n")


# ==========================
# Задача 2.5
# ==========================

def solve_task_2_5():
    print("===== Задача 2.5 (полная неопределённость) =====\n")

    # Допущение: урожайность дискретизируем шагом 10 ц
    yields = np.arange(200, 251, 10)   # 200, 210, ..., 250 центнеров
    # Решаем, сколько рабочих нанять
    workers = np.arange(10, 26)        # от 10 до 25 человек

    price_per_c = 5 * 100   # 5 д.е./кг * 100 кг = 500 д.е. за 1 ц
    wage_per_c = 2 * 100    # 2 д.е./кг * 100 кг = 200 д.е. за 1 ц
    housing_cost = 5000     # общие затраты на жильё, не зависят от N

    def profit(N, Y):
        """
        Прибыль для данного числа рабочих N и урожайности Y.
        Каждый рабочий может убрать до 10 ц.
        Оплата: 2 д.е./кг за фактически убранный урожай + 600 д.е. за проезд.
        В данной модели предполагаем, что оплата 2 д.е./кг идёт только за фактически убранный урожай,
        а 600 д.е. за проезд платится каждому нанятому рабочему.
        Тогда суммарная прибыль можно записать через H = min(Y, 10N):
            выручка по цене 5 д.е./кг = 500 * H
            сдельная оплата = 200 * H
            проезд = 600 * N
            жильё = 5000
            прибыль = 300 * H - 600 * N - 5000
        """
        H = min(Y, 10 * N)
        return 300 * H - 600 * N - housing_cost

    # Матрица выигрышей: строки – N, столбцы – урожай Y
    Y = np.zeros((len(workers), len(yields)))
    for i, N in enumerate(workers):
        for j, Yld in enumerate(yields):
            Y[i, j] = profit(N, Yld)

    payoff_table = pd.DataFrame(
        Y,
        index=[f"N={N}" for N in workers],
        columns=[f"{y} ц" for y in yields]
    )
    print("Таблица выигрышей (прибыль, д.е.):")
    print(payoff_table, "\n")

    # ----- а) Критерий Вальда -----
    W_wald = wald(Y)
    print("Критерий Вальда (максимин):")
    for i, N in enumerate(workers):
        print(f"N = {N}: W_D = min прибыль = {W_wald[i]:.0f} д.е.")
    best_wald = workers[np.argmax(W_wald)]
    print(
        f"-> По критерию Вальда оптимально нанять N = {best_wald} рабочих.\n")

    # ----- б) Критерий Гурвица (γ > 0.5 и γ < 0.5) -----
    gammas = [0.7, 0.3]  # пример коэффициентов
    for gamma in gammas:
        W_h = hurwicz(Y, gamma)
        print(f"Критерий Гурвица, γ = {gamma}:")
        for i, N in enumerate(workers):
            print(f"  N = {N}: W_H = {W_h[i]:.2f}")
        best_h = workers[np.argmax(W_h)]
        print(
            f"  -> Оптимальное N по критерию Гурвица (γ={gamma}) = {best_h}\n")

    # ----- в) Принцип недостаточного обоснования (Бернулли–Лаплас) -----
    W_lap = laplace(Y)
    print("Принцип недостаточного обоснования (Бернулли–Лаплас):")
    for i, N in enumerate(workers):
        print(f"N = {N}: W_L = средняя прибыль = {W_lap[i]:.2f} д.е.")
    best_lap = workers[np.argmax(W_lap)]
    print(
        f"-> По критерию Лапласа оптимально нанять N = {best_lap} рабочих.\n")

    # ----- г) Комбинация критерия Гурвица и принципа недостаточного обоснования -----
    for gamma in gammas:
        W_c = hurwicz_laplace_combined(Y, gamma)
        print(f"Комбинированный критерий (Гурвиц + Лаплас), γ = {gamma}:")
        for i, N in enumerate(workers):
            print(f"  N = {N}: W_C = {W_c[i]:.2f}")
        best_c = workers[np.argmax(W_c)]
        print(
            f"  -> Оптимальное N по комбинированному критерию (γ={gamma}) = {best_c}\n")

    # ----- д) Критерий Сэвиджа -----
    W_sav, regrets = savage(Y)
    print("Критерий Сэвиджа (минимакс сожалений):")
    for i, N in enumerate(workers):
        print(f"N = {N}: W_S = max сожаление = {W_sav[i]:.0f} д.е.")
    best_sav = workers[np.argmin(W_sav)]
    print(
        f"-> По критерию Сэвиджа оптимально нанять N = {best_sav} рабочих.\n")

    # ----- е) Критерий Хоменюка -----
    W_kh, p_hat, regrets_kh = khomenyuk(Y)
    print("Критерий Хоменюка:")
    print("Оценённые псевдо-вероятности состояний (урожайностей):")
    for j, y in enumerate(yields):
        print(f"  Y = {y} ц: p̂ = {p_hat[j]:.4f}")
    print()
    for i, N in enumerate(workers):
        print(f"N = {N}: W_K = {W_kh[i]:.2f}")
    best_kh = workers[np.argmax(W_kh)]
    print(
        f"-> По критерию Хоменюка оптимально нанять N = {best_kh} рабочих.\n")


# ==========================
# Запуск обоих заданий
# ==========================

if __name__ == "__main__":
    solve_task_1_5()
    solve_task_2_5()
