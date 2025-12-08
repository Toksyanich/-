from sympy import symbols, Not

# -----------------------------
# 1. Обозначения (про Иванова)
# -----------------------------
# N_i  – Иванов не сдал хотя бы один экзамен
# D_i  – у Иванова есть отсрочка
# Pr_i – Иванов допущен к летней практике
# P_i  – Иванов пропустил более половины лекций по физике
# Sp_i – Иванов участвовал в спортивных соревнованиях

N_i, D_i, Pr_i, P_i, Sp_i = symbols('N_i D_i Pr_i P_i Sp_i')

# -----------------------------
# 2. Представление дизъюнктов
# -----------------------------
# Дизъюнкт — это множество литералов (sympy-выражений),
# формула в КНФ — множество таких дизъюнктов.
#
# A1: (¬N_i ∨ D_i ∨ ¬Pr_i)
# A2: (¬P_i ∨ N_i)
# A3: Sp_i и P_i  → два дизъюнкта: {Sp_i}, {P_i}
# A4: Pr_i        → {Pr_i}
# ¬B: ¬(Sp_i ∧ D_i) экв. (¬Sp_i ∨ ¬D_i)

clauses = set()

# A1
clauses.add(frozenset({Not(N_i), D_i, Not(Pr_i)}))

# A2
clauses.add(frozenset({Not(P_i), N_i}))

# A3
clauses.add(frozenset({Sp_i}))
clauses.add(frozenset({P_i}))

# A4
clauses.add(frozenset({Pr_i}))

# ¬B
clauses.add(frozenset({Not(Sp_i), Not(D_i)}))


# -----------------------------
# 3. Вспомогательные функции
# -----------------------------
def is_complementary(l1, l2):
    """
    Проверка, являются ли два литерала дополнениями:
    l1 = p, l2 = ¬p   или наоборот.
    """
    return l1 == Not(l2) or l2 == Not(l1)


def resolve(c1, c2):
    """
    Правило резолюции для двух дизъюнктов c1 и c2.
    Возвращает множество возможных резольвент (frozenset).
    """
    resolvents = set()
    for l1 in c1:
        for l2 in c2:
            if is_complementary(l1, l2):
                new_clause = (c1 - {l1}) | (c2 - {l2})
                resolvents.add(frozenset(new_clause))
    return resolvents


def print_clause(clause):
    """
    Красивый вывод одного дизъюнкта.
    """
    if not clause:
        return "[]"
    return " ∨ ".join(str(l) for l in clause)


# -----------------------------
# 4. Общий алгоритм резолюций
# -----------------------------
def resolution(clauses, trace=True):
    """
    Классический (неупорядоченный) резолютивный вывод.
    Возвращает:
        True  – если получен пустой дизъюнкт (противоречие),
        False – если противоречия вывести не удалось.
    """
    clauses = set(clauses)  # скопировать множество
    step = 1

    if trace:
        print("Исходные дизъюнкты:")
        for c in clauses:
            print("  ", print_clause(c))
        print("-" * 50)

    while True:
        new = set()
        # все пары дизъюнктов
        clauses_list = list(clauses)
        n = len(clauses_list)

        for i in range(n):
            for j in range(i + 1, n):
                c1, c2 = clauses_list[i], clauses_list[j]
                resolvents = resolve(c1, c2)
                for r in resolvents:
                    if trace:
                        print(f"Шаг {step}: резолюция")
                        print("   ", print_clause(c1))
                        print("   ", print_clause(c2))
                        print("   =>", print_clause(r))
                        print()
                        step += 1
                    if not r:
                        # пустой дизъюнкт – найдено противоречие
                        if trace:
                            print(
                                "Получен пустой дизъюнкт []. Множество дизъюнктов противоречиво.")
                        return True
                    new.add(r)

        # если новых дизъюнктов нет – дальше вывод не продвинется
        if new.issubset(clauses):
            if trace:
                print("Новые дизъюнкты не появились, противоречие не выведено.")
            return False

        clauses |= new


# -----------------------------
# 5. Запуск и интерпретация
# -----------------------------
if __name__ == "__main__":
    is_contradictory = resolution(clauses, trace=True)

    print("\nИТОГ:")
    if is_contradictory:
        print("Множество {A1, A2, A3, A4, ¬B} противоречиво.")
        print("Значит, из A1–A4 логически следует B:")
        print("  «Существует студент, участвовавший в спортивных соревнованиях и получивший отсрочку».")
        print("Конкретный пример – Иванов (у него должна быть отсрочка).")
    else:
        print("Противоречие не удалось получить — вывод не доказан.")
