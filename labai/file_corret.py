import os
import pandas as pd
import matplotlib.pyplot as plt

# ====== НАСТРОЙКИ ======
CSV_PATH = "results_summary.csv"
OUTPUT_DIR = "plots"
# =======================

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Загрузка данных
df = pd.read_csv(CSV_PATH)

# Список алгоритмов (порядок важен для легенды)
algorithms = df["algorithm"].unique()

# Значения d
depths = sorted(df["depth_target"].unique())


def plot_metric(y_column, y_label, title, filename, log_scale=False):
    plt.figure()

    for alg in algorithms:
        sub = df[df["algorithm"] == alg].sort_values("depth_target")
        plt.plot(
            sub["depth_target"],
            sub[y_column],
            marker="o",
            label=alg
        )

    plt.xlabel("Глубина решения d")
    plt.ylabel(y_label)
    plt.title(title)
    if log_scale:
        plt.yscale("log")
    plt.legend()
    plt.grid(True)

    plt.savefig(os.path.join(OUTPUT_DIR, filename),
                dpi=300, bbox_inches="tight")
    plt.close()


# ====== ГРАФИК 1: Итерации ======
plot_metric(
    y_column="avg_iterations",
    y_label="Среднее количество итераций",
    title="Зависимость количества итераций от глубины решения",
    filename="iterations_vs_d.png",
    log_scale=True
)

# ====== ГРАФИК 2: Макс. память (O + C) ======
plot_metric(
    y_column="avg_max_memory",
    y_label="Средний максимальный объём памяти (O + C)",
    title="Зависимость объёма памяти от глубины решения",
    filename="memory_vs_d.png",
    log_scale=True
)

# ====== ГРАФИК 3: Макс. размер списка O ======
plot_metric(
    y_column="avg_max_open",
    y_label="Средний максимальный размер списка O",
    title="Зависимость размера списка O от глубины решения",
    filename="open_list_vs_d.png",
    log_scale=True
)

# ====== ГРАФИК 4: Время выполнения (если есть) ======
if "avg_time" in df.columns:
    plot_metric(
        y_column="avg_time",
        y_label="Среднее время выполнения, с",
        title="Зависимость времени выполнения от глубины решения",
        filename="time_vs_d.png"
    )

print("Графики успешно построены и сохранены в папке:", OUTPUT_DIR)
