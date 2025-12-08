import tkinter as tk
from tkinter import messagebox
import hashlib
import math
import random
import secrets


# ============================
#   ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================

def is_probable_prime(n: int, k: int = 16) -> bool:
    """
    Тест Миллера–Рабина на простоту.
    n - тестируемое число
    k - количество раундов (чем больше, тем надёжнее)
    """
    if n <= 1:
        return False

    # Небольшая таблица малых простых чисел
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    if n in small_primes:
        return True
    for p in small_primes:
        if n % p == 0:
            return False

    # Представляем n-1 в виде 2^r * d
    r = 0
    d = n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    # Повторяем тест k раз
    for _ in range(k):
        a = random.randrange(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue

        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            # составное
            return False

    return True


def generate_large_prime(bits: int = 512) -> int:
    """
    Генерация большого вероятно простого числа заданной разрядности.
    """
    while True:
        # случайное нечётное число с установленным старшим битом
        candidate = secrets.randbits(bits)
        candidate |= (1 << (bits - 1)) | 1
        if is_probable_prime(candidate):
            return candidate


def egcd(a: int, b: int):
    """
    Расширенный алгоритм Евклида.
    Возвращает (g, x, y) такие, что a*x + b*y = g = gcd(a, b)
    """
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def modinv(a: int, m: int) -> int:
    """
    Обратный элемент по модулю m: a * x ≡ 1 (mod m)
    """
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("Обратного элемента не существует")
    return x % m


# ============================
#   РЕАЛИЗАЦИЯ RSA-ЭЦП
# ============================

def generate_rsa_keys(bits: int = 512):
    """
    Генерация пары ключей RSA для ЭЦП.
    Возвращает (public_key, private_key), где:
      public_key  = (e, n)
      private_key = (d, n)
    """
    # Генерация двух больших простых p и q
    p = generate_large_prime(bits // 2)
    q = generate_large_prime(bits // 2)
    while q == p:
        q = generate_large_prime(bits // 2)

    n = p * q
    phi = (p - 1) * (q - 1)

    # Типичное значение e
    e = 65537
    if math.gcd(e, phi) != 1:
        # В редких случаях подбираем другое нечётное e
        e = 3
        while math.gcd(e, phi) != 1:
            e += 2

    d = modinv(e, phi)

    public_key = (e, n)
    private_key = (d, n)
    return public_key, private_key


def hash_message(message: str) -> int:
    """
    Хэширование сообщения с помощью SHA-256.
    Возвращает целое число, полученное из хэша.
    """
    digest = hashlib.sha256(message.encode("utf-8")).digest()
    return int.from_bytes(digest, byteorder="big")


def sign_message(message: str, private_key) -> int:
    """
    Формирование подписи RSA:
    S = (H(m) mod n)^d mod n
    """
    d, n = private_key
    h = hash_message(message) % n
    signature = pow(h, d, n)
    return signature


def verify_signature(message: str, signature: int, public_key) -> bool:
    """
    Проверка подписи RSA:
    H(m) mod n ?= S^e mod n
    """
    e, n = public_key
    expected = hash_message(message) % n
    h_from_signature = pow(signature, e, n)
    return h_from_signature == expected


# ============================
#   ГРАФИЧЕСКИЙ ИНТЕРФЕЙС
# ============================

class RSADigitalSignatureApp(tk.Tk):
    """
    Простое приложение "Отправитель–Получатель"
    для демонстрации ЭЦП на основе RSA.
    """

    def __init__(self):
        super().__init__()

        self.title("Демонстрация электронной цифровой подписи (RSA)")
        self.geometry("1000x600")

        # Текущие ключи и подпись
        self.public_key = None
        self.private_key = None
        self.current_signature = None

        self.create_widgets()

    def create_widgets(self):
        # --- Блок ключей отправителя ---
        keys_frame = tk.LabelFrame(
            self, text="Ключи отправителя (RSA)", padx=10, pady=10)
        keys_frame.pack(fill="x", padx=10, pady=10)

        self.keys_info_label = tk.Label(
            keys_frame,
            text="Ключи ещё не сгенерированы.",
            justify="left"
        )
        self.keys_info_label.pack(side="left", padx=5)

        gen_keys_button = tk.Button(
            keys_frame,
            text="Сгенерировать ключи",
            command=self.on_generate_keys
        )
        gen_keys_button.pack(side="right", padx=5)

        # --- Основная область: слева отправитель, справа получатель ---
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ----- Отправитель -----
        sender_frame = tk.LabelFrame(
            main_frame, text="Отправитель", padx=10, pady=10)
        sender_frame.pack(side="left", fill="both",
                          expand=True, padx=5, pady=5)

        sender_label = tk.Label(sender_frame, text="Сообщение для подписания:")
        sender_label.pack(anchor="w")

        self.sender_message_text = tk.Text(sender_frame, height=10)
        self.sender_message_text.pack(fill="both", expand=True, pady=5)

        sign_button = tk.Button(
            sender_frame,
            text="Подписать сообщение",
            command=self.on_sign_message
        )
        sign_button.pack(pady=5)

        signature_label = tk.Label(
            sender_frame, text="Сформированная подпись (число):")
        signature_label.pack(anchor="w")

        self.signature_text = tk.Text(sender_frame, height=6)
        self.signature_text.pack(fill="both", expand=True, pady=5)

        # ----- Получатель -----
        receiver_frame = tk.LabelFrame(
            main_frame, text="Получатель", padx=10, pady=10)
        receiver_frame.pack(side="right", fill="both",
                            expand=True, padx=5, pady=5)

        recv_msg_label = tk.Label(receiver_frame, text="Полученное сообщение:")
        recv_msg_label.pack(anchor="w")

        self.receiver_message_text = tk.Text(receiver_frame, height=10)
        self.receiver_message_text.pack(fill="both", expand=True, pady=5)

        recv_sig_label = tk.Label(
            receiver_frame, text="Полученная подпись (число):")
        recv_sig_label.pack(anchor="w")

        self.receiver_signature_text = tk.Text(receiver_frame, height=6)
        self.receiver_signature_text.pack(fill="both", expand=True, pady=5)

        verify_button = tk.Button(
            receiver_frame,
            text="Проверить подпись",
            command=self.on_verify_signature
        )
        verify_button.pack(pady=5)

        self.verify_result_label = tk.Label(
            receiver_frame, text="Результат проверки: —")
        self.verify_result_label.pack(anchor="w", pady=5)

    # ============================
    #   ОБРАБОТЧИКИ СОБЫТИЙ
    # ============================

    def on_generate_keys(self):
        """
        Генерация новой пары ключей RSA отправителя.
        """
        try:
            public_key, private_key = generate_rsa_keys(bits=512)
        except Exception as exc:
            messagebox.showerror(
                "Ошибка", f"Не удалось сгенерировать ключи:\n{exc}")
            return

        self.public_key = public_key
        self.private_key = private_key

        e, n = public_key
        d, _ = private_key

        n_bits = n.bit_length()

        self.keys_info_label.config(
            text=(
                "Ключи сгенерированы.\n"
                f"Открытый ключ: e = {e}, n (длина {n_bits} бит)\n"
                f"Закрытый ключ: d = {d}\n"
                "Закрытый ключ должен храниться в секрете.\n"
            )
        )

        # Очищаем старые данные
        self.signature_text.delete("1.0", tk.END)
        self.receiver_message_text.delete("1.0", tk.END)
        self.receiver_signature_text.delete("1.0", tk.END)
        self.verify_result_label.config(text="Результат проверки: —")

    def on_sign_message(self):
        """
        Формирование подписи отправителем.
        """
        if self.private_key is None:
            messagebox.showwarning(
                "Нет ключей", "Сначала сгенерируйте ключи отправителя.")
            return

        message = self.sender_message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning(
                "Нет сообщения", "Введите сообщение для подписания.")
            return

        try:
            signature = sign_message(message, self.private_key)
        except Exception as exc:
            messagebox.showerror(
                "Ошибка", f"Не удалось сформировать подпись:\n{exc}")
            return

        self.current_signature = signature

        # Показываем подпись у отправителя
        self.signature_text.delete("1.0", tk.END)
        self.signature_text.insert(tk.END, str(signature))

        # "Передаём" сообщение и подпись получателю
        self.receiver_message_text.delete("1.0", tk.END)
        self.receiver_message_text.insert(tk.END, message)

        self.receiver_signature_text.delete("1.0", tk.END)
        self.receiver_signature_text.insert(tk.END, str(signature))

        self.verify_result_label.config(text="Результат проверки: —")

    def on_verify_signature(self):
        """
        Проверка подписи получателем.
        """
        if self.public_key is None:
            messagebox.showwarning("Нет открытого ключа",
                                   "Сначала сгенерируйте ключи отправителя.")
            return

        message = self.receiver_message_text.get("1.0", tk.END).strip()
        sig_text = self.receiver_signature_text.get("1.0", tk.END).strip()

        if not message:
            messagebox.showwarning(
                "Нет сообщения", "Нет текста сообщения для проверки.")
            return
        if not sig_text:
            messagebox.showwarning("Нет подписи", "Нет подписи для проверки.")
            return

        try:
            signature = int(sig_text)
        except ValueError:
            messagebox.showerror("Ошибка", "Подпись должна быть целым числом.")
            return

        try:
            ok = verify_signature(message, signature, self.public_key)
        except Exception as exc:
            messagebox.showerror(
                "Ошибка", f"Не удалось проверить подпись:\n{exc}")
            return

        if ok:
            self.verify_result_label.config(
                text="Результат проверки: подпись корректна (сообщение подлинно и не изменено).",
                fg="green"
            )
        else:
            self.verify_result_label.config(
                text="Результат проверки: подпись НЕ корректна (сообщение подделано или ключ неверен).",
                fg="red"
            )


if __name__ == "__main__":
    app = RSADigitalSignatureApp()
    app.mainloop()
