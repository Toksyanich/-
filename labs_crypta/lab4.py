
import collections

# --- Часть 1: Линейный сдвиговый регистр (ЛСОР/LFSR) ---
# Источник начальных значений для генератора Фибоначчи


def lfsr_17_generator(seed: int):
    """
    Генератор 17-битного ЛСОР.
    Использует примитивный полином x^17 + x^3 + 1 для максимального периода.
    Отводы (taps) находятся на позициях 17 и 3 (индексация с 1).
    В 0-индексированной системе сдвига вправо это биты 16 и 2.
    """
    # Убедимся, что начальное состояние не нулевое и 17-битное
    if not 0 < seed < 2**17:
        raise ValueError(
            "Начальное состояние (seed) должно быть 17-битным и не нулевым.")

    state = seed
    # Маска для ограничения числа 17 битами
    mask = (1 << 17) - 1

    while True:
        yield state
        # 1. Вычисляем новый бит (XOR битов 16 и 2)
        new_bit = ((state >> 16) ^ (state >> 2)) & 1
        # 2. Сдвигаем регистр влево на 1
        state = (state << 1) & mask
        # 3. Устанавливаем новый младший бит
        state |= new_bit

# --- Часть 2: Генератор Фибоначчи с запаздываниями ---
# Основной генератор псевдослучайной последовательности


class FibonacciGenerator:
    """
    Реализует генератор Фибоначчи с запаздываниями (Subtract-with-borrow).
    Формула: Y_k = (Y_{k-a} - Y_{k-b}) mod 1.0
    """

    def __init__(self, seed_values: list, a: int, b: int):
        if len(seed_values) != max(a, b):
            raise ValueError(f"Требуется {max(a, b)} начальных значений.")

        self.a = a
        self.b = b
        # Используем deque как кольцевой буфер для хранения состояния
        self.state = collections.deque(seed_values, maxlen=max(a, b))

    def _generate_next(self) -> float:
        """Генерирует следующее вещественное число."""
        # Индексы в deque: 0 - самый "старый", maxlen-1 - самый "новый"
        # Y_{k-a} - самый старый элемент, Y_{k-b} - элемент с индексом maxlen-b
        y_k_a = self.state[len(self.state) - self.a]
        y_k_b = self.state[len(self.state) - self.b]

        diff = y_k_a - y_k_b

        # Эквивалент операции по модулю 1.0 для вещественных чисел
        if diff < 0:
            new_val = diff + 1.0
        else:
            new_val = diff

        self.state.append(new_val)
        return new_val

    def stream(self):
        """Бесконечный генератор вещественных чисел."""
        while True:
            yield self._generate_next()

# --- Часть 3: Шифратор, использующий гаммирование ---


class GammingCipher:
    def __init__(self, lfsr_seed: int, a: int, b: int):
        self.lfsr_seed = lfsr_seed
        self.a = a
        self.b = b
        self.gamma_generator = self._initialize_gamma_generator()

    def _initialize_gamma_generator(self):
        """Инициализирует генератор гаммы, используя ЛСОР."""
        print(
            f"1. Инициализация ЛСОР с начальным значением: {hex(self.lfsr_seed)}")
        lfsr_gen = lfsr_17_generator(self.lfsr_seed)

        # Генерируем max(a,b) стартовых значений из ЛСОР
        num_seeds = max(self.a, self.b)
        lfsr_seeds_int = [next(lfsr_gen) for _ in range(num_seeds)]
        print(
            f"\n2. Сгенерировано {num_seeds} целых чисел из ЛСОР для инициализации:")
        print(lfsr_seeds_int)

        # Преобразуем в вещественные числа по условию
        fib_seeds_float = [val / 10**9 for val in lfsr_seeds_int]
        print("\n3. Преобразование в вещественные числа (деление на 10^9):")
        print([f"{v:.9f}" for v in fib_seeds_float])

        # Инициализируем генератор Фибоначчи
        fib_gen = FibonacciGenerator(fib_seeds_float, self.a, self.b)

        # Возвращаем бесконечный поток вещественных чисел
        return fib_gen.stream()

    def _get_gamma_bits(self, num_bits: int) -> str:
        """Генерирует гамму указанной длины в битах."""
        gamma_bits = []
        while len(gamma_bits) < num_bits:
            # Получаем следующее вещественное число
            f_val = next(self.gamma_generator)
            # Преобразуем его в целое по условию
            i_val = int(f_val * 10**9)
            # Переводим в двоичную строку без префикса "0b"
            bin_str = format(i_val, 'b')
            gamma_bits.extend(list(bin_str))

        return "".join(gamma_bits)[:num_bits]

    @staticmethod
    def _xor_binary_strings(str1: str, str2: str) -> str:
        """Выполняет операцию XOR для двух бинарных строк."""
        return "".join('1' if b1 != b2 else '0' for b1, b2 in zip(str1, str2))

    @staticmethod
    def text_to_binary(text: str) -> str:
        """Преобразует ASCII текст в бинарную строку (8 бит на символ)."""
        return "".join(format(ord(c), '08b') for c in text)

    @staticmethod
    def binary_to_text(binary_str: str) -> str:
        """Преобразует бинарную строку обратно в ASCII текст."""
        text = ""
        for i in range(0, len(binary_str), 8):
            byte = binary_str[i:i+8]
            if len(byte) < 8:
                continue  # Игнорируем неполные байты
            try:
                text += chr(int(byte, 2))
            except (ValueError, TypeError):
                text += '?'  # Если байт не представляет печатный символ
        return text

    def encrypt(self, plaintext: str):
        """Шифрует текст и возвращает все промежуточные результаты."""
        print("\n--- Процесс шифрования ---")

        # 1. Конвертируем исходный текст в двоичный вид
        plaintext_binary = self.text_to_binary(plaintext)
        print(f"Длина исходного сообщения в битах: {len(plaintext_binary)}")

        # 2. Генерируем гамму такой же длины
        print("Генерация гаммы...")
        gamma_binary = self._get_gamma_bits(len(plaintext_binary))

        # 3. Шифруем (XOR)
        ciphertext_binary = self._xor_binary_strings(
            plaintext_binary, gamma_binary)

        return plaintext_binary, gamma_binary, ciphertext_binary

# --- Часть 4: Основная программа и демонстрация ---


if __name__ == "__main__":
    # Параметры для варианта 15
    A_LAG = 17
    B_LAG = 5
    # Начальное состояние для ЛСОР (любое 17-битное не-ноль)
    LFSR_SEED = 0x1A2B3  # Пример: 107187 в десятичной

    PLAINTEXT = "Hello, world! This is a test message for the Fibonacci gammimg cipher."

    # 1. Создание и инициализация шифратора
    # Инициализация происходит один раз при создании объекта
    cipher = GammingCipher(lfsr_seed=LFSR_SEED, a=A_LAG, b=B_LAG)

    # 2. Шифрование
    plaintext_bin, gamma_bin, ciphertext_bin = cipher.encrypt(PLAINTEXT)

    # 3. Преобразование шифротекста в читаемый вид
    ciphertext_text = cipher.binary_to_text(ciphertext_bin)

    # 4. Вывод результатов на экран
    print("\n--- Результаты ---")
    print(f"Исходный текст:      {PLAINTEXT}")
    print(f"Исходный текст (bin): {plaintext_bin[:64]}...")
    print(f"Гамма (bin):          {gamma_bin[:64]}...")
    print(f"Шифротекст (bin):     {ciphertext_bin[:64]}...")
    print(f"Шифротекст (текст):   {ciphertext_text}")

    # 5. Сохранение результатов в файлы
    try:
        with open("plaintext.txt", "w", encoding="utf-8") as f:
            f.write(f"Текст: {PLAINTEXT}\n")
            f.write(f"Бинарный вид: {plaintext_bin}\n")

        with open("gamma.txt", "w", encoding="utf-8") as f:
            f.write(f"Гамма (бинарный вид): {gamma_bin}\n")

        with open("ciphertext.txt", "w", encoding="utf-8") as f:
            f.write(f"Текст: {ciphertext_text}\n")
            f.write(f"Бинарный вид: {ciphertext_bin}\n")

        print("\nРезультаты сохранены в файлы: plaintext.txt, gamma.txt, ciphertext.txt")
    except Exception as e:
        print(f"\nОшибка при сохранении файлов: {e}")

    # 6. Демонстрация расшифрования
    print("\n--- Процесс расшифрования ---")

    # Для расшифрования нужен новый объект с ТЕМ ЖЕ ключом (LFSR_SEED)
    # чтобы сгенерировать ту же самую гамму с самого начала
    decipher = GammingCipher(lfsr_seed=LFSR_SEED, a=A_LAG, b=B_LAG)

    print("Генерация той же гаммы для расшифрования...")
    decryption_gamma_bin = decipher._get_gamma_bits(len(ciphertext_bin))

    # Проверка, что гамма идентична
    if decryption_gamma_bin == gamma_bin:
        print("Гаммы для шифрования и расшифрования совпадают. Продолжаем.")
    else:
        print("ОШИБКА: Гаммы не совпадают! Расшифрование будет некорректным.")

    decrypted_bin = decipher._xor_binary_strings(
        ciphertext_bin, decryption_gamma_bin)
    decrypted_text = decipher.binary_to_text(decrypted_bin)

    print(f"\nРасшифрованный текст: {decrypted_text}")
    print(f"Расшифровка успешна: {decrypted_text == PLAINTEXT}")
