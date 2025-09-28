# -*- coding: utf-8 -*-

# Определение алфавита согласно варианту №5
# 26 английских букв + пробел = 27 символов
PLAINTEXT_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "


def generate_cipher_alphabet(keyword, base_alphabet):
    """
    Генерирует алфавит замены на основе ключевого слова.
    Сначала идут уникальные символы из ключа, затем остальные символы из базового алфавита.
    :param keyword: Ключевое слово (например, "SECURITY").
    :param base_alphabet: Базовый алфавит (в нашем случае PLAINTEXT_ALPHABET).
    :return: Сформированный алфавит замены.
    """
    keyword = keyword.upper()
    cipher_alphabet = ""
    # Добавляем уникальные символы из ключа
    for char in keyword:
        if char in base_alphabet and char not in cipher_alphabet:
            cipher_alphabet += char
    # Добавляем оставшиеся символы из базового алфавита
    for char in base_alphabet:
        if char not in cipher_alphabet:
            cipher_alphabet += char
    return cipher_alphabet


def alberti_encrypt(text, keyword, initial_shift, step_shift):
    """
    Шифрует текст методом Альберти согласно варианту 5.
    :param text: Исходный текст для шифрования.
    :param keyword: Ключевое слово для генерации алфавита замены.
    :param initial_shift: Начальный сдвиг алфавита замены.
    :param step_shift: Шаг сдвига после каждого слова (пробела).
    :return: Зашифрованный текст.
    """
    text = text.upper()
    cipher_alphabet = generate_cipher_alphabet(keyword, PLAINTEXT_ALPHABET)
    alphabet_len = len(PLAINTEXT_ALPHABET)

    encrypted_text = ""
    current_shift = initial_shift

    for char in text:
        if char in PLAINTEXT_ALPHABET:
            # Находим индекс исходного символа
            p_index = PLAINTEXT_ALPHABET.find(char)

            # Вычисляем индекс в алфавите замены с учетом текущего сдвига
            c_index = (p_index + current_shift) % alphabet_len

            encrypted_text += cipher_alphabet[c_index]

            # Если зашифровали пробел, увеличиваем сдвиг на величину шага
            if char == ' ':
                current_shift = (current_shift + step_shift) % alphabet_len
        else:
            # Символы, не входящие в алфавит, оставляем без изменений
            encrypted_text += char

    return encrypted_text


def alberti_decrypt(text, keyword, initial_shift, step_shift):
    """
    Дешифрует текст, зашифрованный методом Альберти.
    :param text: Зашифрованный текст.
    :param keyword: Ключевое слово.
    :param initial_shift: Начальный сдвиг.
    :param step_shift: Шаг сдвига.
    :return: Расшифрованный текст.
    """
    text = text.upper()
    cipher_alphabet = generate_cipher_alphabet(keyword, PLAINTEXT_ALPHABET)
    alphabet_len = len(PLAINTEXT_ALPHABET)

    decrypted_text = ""
    current_shift = initial_shift

    for char in text:
        if char in cipher_alphabet:
            # Находим индекс зашифрованного символа в алфавите замены
            c_index = cipher_alphabet.find(char)

            # Вычисляем индекс исходного символа (обратная операция)
            p_index = (c_index - current_shift + alphabet_len) % alphabet_len

            decrypted_char = PLAINTEXT_ALPHABET[p_index]
            decrypted_text += decrypted_char

            # Если расшифрованный символ - пробел, увеличиваем сдвиг
            if decrypted_char == ' ':
                current_shift = (current_shift + step_shift) % alphabet_len
        else:
            decrypted_text += char

    return decrypted_text


def main():
    """
    Главная функция для взаимодействия с пользователем.
    """
    print("--- Лабораторная работа №2 ---")
    print("--- Шифр Альберти (Вариант 5) ---")

    mode = input("Выберите режим (1 - Шифрование, 2 - Дешифрование): ")

    try:
        input_file = input(
            "Введите имя входного файла (например, input.txt): ")
        output_file = input(
            "Введите имя выходного файла (например, output.txt): ")

        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()

        keyword = input("Введите ключевое слово (на английском): ")
        initial_shift = int(
            input("Введите величину начального сдвига (целое число): "))
        step_shift = 2  # Шаг сдвига фиксирован и равен 2 по заданию

        if mode == '1':
            print("\n--- Режим шифрования ---")
            result = alberti_encrypt(text, keyword, initial_shift, step_shift)
            print(f"\nИтоговый шифртекст:\n{result}")

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"\nРезультат сохранен в файл {output_file}")

        elif mode == '2':
            print("\n--- Режим дешифрования ---")
            result = alberti_decrypt(text, keyword, initial_shift, step_shift)
            print(f"\nИтоговый расшифрованный текст:\n{result}")

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"\nРезультат сохранен в файл {output_file}")

        else:
            print("Ошибка: выбран неверный режим.")

    except FileNotFoundError:
        print(f"Ошибка: Файл '{input_file}' не найден.")
    except ValueError:
        print("Ошибка: Начальный сдвиг должен быть целым числом.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
