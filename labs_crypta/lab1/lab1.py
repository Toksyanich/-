# -*- coding: utf-8 -*-

# Определение алфавита согласно варианту №5
# 33 русские буквы + пробел + точка = 35 символов
ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ ."


def caesar_encrypt(text, shift):
    """
    Шифрует текст методом Цезаря.
    :param text: Исходный текст для шифрования.
    :param shift: Целочисленный ключ (сдвиг).
    :return: Зашифрованный текст.
    """
    encrypted_text = ""
    alphabet_len = len(ALPHABET)
    for char in text.upper():
        if char in ALPHABET:
            index = ALPHABET.find(char)
            new_index = (index + shift) % alphabet_len
            encrypted_text += ALPHABET[new_index]
        else:
            # Если символ не из алфавита, оставляем его без изменений
            encrypted_text += char
    return encrypted_text


def caesar_decrypt(text, shift):
    """
    Дешифрует текст, зашифрованный методом Цезаря.
    :param text: Зашифрованный текст.
    :param shift: Целочисленный ключ (сдвиг).
    :return: Расшифрованный текст.
    """
    decrypted_text = ""
    alphabet_len = len(ALPHABET)
    for char in text.upper():
        if char in ALPHABET:
            index = ALPHABET.find(char)
            # Для дешифрования выполняем обратное смещение
            new_index = (index - shift + alphabet_len) % alphabet_len
            decrypted_text += ALPHABET[new_index]
        else:
            decrypted_text += char
    return decrypted_text


def get_permutation_order(key):
    """
    Возвращает порядок перестановки столбцов/строк на основе ключа.
    Пример: ключ "КОД" -> "ДКО" -> [2, 0, 1] (индексы исходных букв)
    """
    # Создаем пары (индекс, буква) и сортируем по букве
    sorted_key = sorted([(i, char)
                        for i, char in enumerate(key)], key=lambda x: x[1])
    # Возвращаем только отсортированные индексы
    return [item[0] for item in sorted_key]


def get_inverse_permutation_order(order):
    """
    Находит обратную перестановку.
    Пример: порядок [2, 0, 1] -> обратный порядок [1, 2, 0]
    """
    inverse_order = [0] * len(order)
    for i, p in enumerate(order):
        inverse_order[p] = i
    return inverse_order


def double_permutation_encrypt(text, key_cols, key_rows):
    """
    Шифрует текст методом двойной перестановки.
    :param text: Текст для шифрования.
    :param key_cols: Ключевое слово для перестановки столбцов.
    :param key_rows: Ключевое слово для перестановки строк.
    :return: Зашифрованный текст.
    """
    num_cols = len(key_cols)
    num_rows = len(key_rows)

    # Добиваем текст пробелами до длины, кратной размеру таблицы
    while len(text) % (num_cols * num_rows) != 0:
        text += " "

    # 1. Запись в таблицу по строкам
    table = [list(text[i:i+num_cols]) for i in range(0, len(text), num_cols)]

    # 2. Перестановка столбцов
    col_order = get_permutation_order(key_cols)
    permuted_cols_table = []
    for r in range(len(table)):
        new_row = [''] * num_cols
        for c_idx, c_val in enumerate(col_order):
            new_row[c_idx] = table[r][c_val]
        permuted_cols_table.append(new_row)

    # 3. Перестановка строк
    row_order = get_permutation_order(key_rows)
    permuted_rows_table = [''] * len(table)
    for r_idx, r_val in enumerate(row_order):
        permuted_rows_table[r_idx] = permuted_cols_table[r_val]

    # 4. Считывание из итоговой таблицы по столбцам
    encrypted_text = ""
    for c in range(num_cols):
        for r in range(len(permuted_rows_table)):
            encrypted_text += permuted_rows_table[r][c]

    return encrypted_text


def double_permutation_decrypt(text, key_cols, key_rows):
    """
    Дешифрует текст, зашифрованный методом двойной перестановки.
    :param text: Зашифрованный текст.
    :param key_cols: Ключевое слово для столбцов.
    :param key_rows: Ключевое слово для строк.
    :return: Расшифрованный текст.
    """
    num_cols = len(key_cols)
    num_rows = len(key_rows)

    # 1. Запись шифртекста в таблицу по столбцам
    table = [['' for _ in range(num_cols)] for _ in range(num_rows)]
    text_idx = 0
    for c in range(num_cols):
        for r in range(num_rows):
            table[r][c] = text[text_idx]
            text_idx += 1

    # 2. Обратная перестановка строк
    row_order = get_permutation_order(key_rows)
    inverse_row_order = get_inverse_permutation_order(row_order)

    unpermuted_rows_table = [''] * num_rows
    for r_idx, r_val in enumerate(inverse_row_order):
        unpermuted_rows_table[r_idx] = table[r_val]

    # 3. Обратная перестановка столбцов
    col_order = get_permutation_order(key_cols)
    inverse_col_order = get_inverse_permutation_order(col_order)

    unpermuted_cols_table = [
        ['' for _ in range(num_cols)] for _ in range(num_rows)]
    for r in range(num_rows):
        for c_idx, c_val in enumerate(inverse_col_order):
            unpermuted_cols_table[r][c_idx] = unpermuted_rows_table[r][c_val]

    # 4. Считывание по строкам
    decrypted_text = ""
    for r in range(num_rows):
        decrypted_text += "".join(unpermuted_cols_table[r])

    return decrypted_text.strip()  # Убираем лишние пробелы в конце


def main():
    """
    Главная функция для взаимодействия с пользователем.
    """
    print("--- Лабораторная работа №1 ---")
    print("--- Вариант 5 ---")

    mode = input("Выберите режим (1 - Шифрование, 2 - Дешифрование): ")

    try:
        input_file = input(
            "Введите имя входного файла (например, input.txt): ")
        output_file = input(
            "Введите имя выходного файла (например, output.txt): ")

        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()

        if mode == '1':
            # --- Шифрование ---
            print("\n--- Режим шифрования ---")
            # Ключи для 1-й ступени (Цезарь)
            caesar_shift = int(
                input("Введите ключ для шифра Цезаря (целое число): "))

            # Ключи для 2-й ступени (Двойная перестановка)
            key_cols = input("Введите ключ-слово для столбцов: ").upper()
            key_rows = input("Введите ключ-слово для строк: ").upper()

            # Этап 1: Шифр Цезаря
            encrypted_caesar = caesar_encrypt(text, caesar_shift)
            print(f"\nТекст после шифра Цезаря:\n{encrypted_caesar}")

            # Этап 2: Двойная перестановка
            final_encrypted = double_permutation_encrypt(
                encrypted_caesar, key_cols, key_rows)
            print(f"\nИтоговый шифртекст:\n{final_encrypted}")

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_encrypted)
            print(f"\nРезультат сохранен в файл {output_file}")

        elif mode == '2':
            # --- Дешифрование ---
            print("\n--- Режим дешифрования ---")
            # Ключи для 1-й ступени (Цезарь)
            caesar_shift = int(
                input("Введите ключ для шифра Цезаря (целое число): "))

            # Ключи для 2-й ступени (Двойная перестановка)
            key_cols = input("Введите ключ-слово для столбцов: ").upper()
            key_rows = input("Введите ключ-слово для строк: ").upper()

            # Этап 1: Обратная двойная перестановка
            decrypted_permutation = double_permutation_decrypt(
                text, key_cols, key_rows)
            print(
                f"\nТекст после дешифрования перестановкой:\n{decrypted_permutation}")

            # Этап 2: Обратный шифр Цезаря
            final_decrypted = caesar_decrypt(
                decrypted_permutation, caesar_shift)
            print(f"\nИтоговый расшифрованный текст:\n{final_decrypted}")

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_decrypted)
            print(f"\nРезультат сохранен в файл {output_file}")

        else:
            print("Ошибка: выбран неверный режим.")

    except FileNotFoundError:
        print(f"Ошибка: Файл '{input_file}' не найден.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
