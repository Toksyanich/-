# -*- coding: utf-8 -*-
import random
import math
from collections import Counter

# --- КОНСТАНТЫ И ЭТАЛОННЫЕ ДАННЫЕ ---

# Алфавит согласно варианту 5 (30 символов)
ALPHABET = "abcdefghijklmnopqrstuvwxyz,.: "

# Эталонные частоты для английского языка (из Таблицы 2, стр. 5)
# Добавлены примерные частоты для пробела и знаков препинания
# Пробел - самый частый "символ" в тексте.
ENGLISH_FREQUENCIES = {
    'a': 0.081, 'b': 0.016, 'c': 0.032, 'd': 0.036, 'e': 0.123,
    'f': 0.023, 'g': 0.016, 'h': 0.051, 'i': 0.071, 'j': 0.001,
    'k': 0.005, 'l': 0.040, 'm': 0.022, 'n': 0.072, 'o': 0.079,
    'p': 0.023, 'q': 0.002, 'r': 0.060, 's': 0.066, 't': 0.096,
    'u': 0.031, 'v': 0.009, 'w': 0.020, 'x': 0.002, 'y': 0.019,
    'z': 0.001, ' ': 0.180, ',': 0.010, '.': 0.010, ':': 0.001
}

# Нормализуем частоты, чтобы их сумма была равна 1
total_freq = sum(ENGLISH_FREQUENCIES.values())
for char in ENGLISH_FREQUENCIES:
    ENGLISH_FREQUENCIES[char] /= total_freq

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---


def find_char_in_square(char, square):
    """Находит координаты символа в квадрате Полибия."""
    for r, row in enumerate(square):
        for c, symbol in enumerate(row):
            if symbol == char:
                return r, c
    return None, None


def generate_square_from_first_row(first_row, rows=5, cols=6):
    """Генерирует полный квадрат Полибия на основе заданной первой строки."""
    square = [first_row]
    remaining_chars = [char for char in ALPHABET if char not in first_row]

    for i in range(1, rows):
        row = remaining_chars[(i-1)*cols: i*cols]
        square.append(row)
    return square

# --- ФУНКЦИИ ШИФРОВАНИЯ И ДЕШИФРОВАНИЯ ---


def polybius_encrypt(text, square):
    """Шифрует текст, заменяя символ на тот, что находится ПОД ним."""
    encrypted_text = ""
    rows, cols = len(square), len(square[0])
    for char in text.lower():
        if char in ALPHABET:
            r, c = find_char_in_square(char, square)
            if r is not None:
                # Циклический сдвиг вниз
                encrypted_char = square[(r + 1) % rows][c]
                encrypted_text += encrypted_char
        else:
            encrypted_text += char  # Сохраняем символы не из алфавита
    return encrypted_text


def polybius_decrypt(text, square):
    """Дешифрует текст, заменяя символ на тот, что находится НАД ним."""
    decrypted_text = ""
    rows, cols = len(square), len(square[0])
    for char in text:
        if char in ALPHABET:
            r, c = find_char_in_square(char, square)
            if r is not None:
                # Циклический сдвиг вверх
                decrypted_char = square[(r - 1 + rows) % rows][c]
                decrypted_text += decrypted_char
        else:
            decrypted_text += char
    return decrypted_text

# --- ФУНКЦИИ КРИПТОАНАЛИЗА ---


def calculate_divergence(text):
    """Вычисляет степень расхождения статистики текста от эталонной."""
    text_len = len(text)
    if text_len == 0:
        return float('inf')

    counts = Counter(text)
    observed_freqs = {char: counts[char] / text_len for char in ALPHABET}

    # Формула W из методички
    divergence = 0
    for char in ALPHABET:
        w = (observed_freqs.get(char, 0) - ENGLISH_FREQUENCIES[char]) ** 2
        divergence += w

    return divergence


def cryptanalyze(ciphertext, num_variants=50000, cols=6):
    """
    Выполняет криптоанализ шифртекста для поиска первой строки квадрата Полибия.
    :param ciphertext: Зашифрованный текст.
    :param num_variants: Количество вариантов первой строки для перебора.
    :param cols: Количество столбцов в квадрате.
    :return: (Найденная первая строка, Расшифрованный текст)
    """
    best_row = None
    min_divergence = float('inf')

    print(
        f"Начинаем криптоанализ. Перебор {num_variants} вариантов первой строки...")

    # Генерируем 30 случайных уникальных вариантов первой строки
    alphabet_list = list(ALPHABET)
    candidate_rows = set()
    while len(candidate_rows) < num_variants:
        random.shuffle(alphabet_list)
        candidate_rows.add(tuple(alphabet_list[:cols]))

    for i, row_tuple in enumerate(candidate_rows):
        candidate_row = list(row_tuple)

        # 1. Генерируем полный квадрат на основе кандидата
        square = generate_square_from_first_row(candidate_row)

        # 2. Расшифровываем текст
        decrypted_text = polybius_decrypt(ciphertext, square)

        # 3. Вычисляем расхождение
        divergence = calculate_divergence(decrypted_text)

        print(
            f"  Вариант {i+1}/{num_variants}: строка {''.join(candidate_row)}, расхождение = {divergence:.6f}")

        # 4. Если результат лучше, сохраняем его
        if divergence < min_divergence:
            min_divergence = divergence
            best_row = candidate_row
            best_decrypted_text = decrypted_text

    return best_row, best_decrypted_text

# --- ГЛАВНАЯ ФУНКЦИЯ ---


def main():
    print("--- Лабораторная работа №3: Криптоанализ ---")
    print("--- Вариант 5: Полибианский квадрат ---")

    mode = input("Выберите режим (1 - Шифрование, 2 - Криптоанализ): ")

    try:
        if mode == '1':
            input_file = input("Введите имя файла с исходным текстом: ")
            output_file = input(
                "Введите имя файла для сохранения шифртекста: ")

            # Для шифрования создадим ключ - первую строку
            secret_first_row_str = input(
                "Введите секретную первую строку (6 уникальных символов из алфавита): ")
            secret_first_row = list(secret_first_row_str)

            if len(secret_first_row) != 6 or len(set(secret_first_row)) != 6:
                print("Ошибка: строка должна содержать 6 уникальных символов.")
                return

            square = generate_square_from_first_row(secret_first_row)

            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()

            encrypted = polybius_encrypt(text, square)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(encrypted)
            print(f"Текст успешно зашифрован и сохранен в {output_file}")

        elif mode == '2':
            input_file = input("Введите имя файла с шифртекстом: ")
            output_file = input(
                "Введите имя файла для сохранения результата: ")

            with open(input_file, 'r', encoding='utf-8') as f:
                ciphertext = f.read()

            found_row, decrypted_text = cryptanalyze(ciphertext)

            print("\n--- Результаты криптоанализа ---")
            print(f"Наиболее вероятная первая строка: {''.join(found_row)}")
            print("\nНачало расшифрованного текста:")
            print(decrypted_text[:500])  # Выводим первые 500 символов

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(decrypted_text)
            print(f"\nПолный расшифрованный текст сохранен в {output_file}")

        else:
            print("Ошибка: выбран неверный режим.")

    except FileNotFoundError:
        print(f"Ошибка: Файл не найден.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
