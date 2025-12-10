def plot_risk_loving_utility():
    """
    Строит пример функции полезности для ЛПР,
    склонного к риску (выпуклая функция полезности).
    Используется для иллюстрации в задаче 1.
    """

    import numpy as np
    import matplotlib.pyplot as plt

    # диапазон выигрышей
    y = np.linspace(0, 3000, 300)

    # выпуклая функция полезности — ЛПР склонен к риску
    u = (0.001 * y) ** 2

    plt.figure(figsize=(8, 5))
    plt.plot(y, u, linewidth=2)
    plt.xlabel("Выигрыш y, д.е.")
    plt.ylabel("Полезность u(y)")
    plt.title("Функция полезности для склонности к риску (выпуклая)")
    plt.grid(True)
    plt.show()


plot_risk_loving_utility()
