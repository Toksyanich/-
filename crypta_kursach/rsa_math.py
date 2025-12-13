"""
Модуль rsa_math.py: реализация математики RSA поверх класса CustomBigInt.
Содержит генерацию простых чисел, тест Миллера-Рабина, построение ключей,
а также функции шифрования и дешифрования.
"""

from __future__ import annotations

import os
from typing import Dict, Tuple

from bigint import CustomBigInt


DEFAULT_E = CustomBigInt(65537)


# ---------- Вспомогательные функции ----------
def text_to_bigint(text: str) -> CustomBigInt:
    """
    Кодирует текст в UTF-8 и превращает байты в CustomBigInt через основание 256.
    """
    data = text.encode("utf-8")
    return CustomBigInt.from_bytes(data)


def bigint_to_text(value: CustomBigInt) -> str:
    """
    Превращает CustomBigInt обратно в строку UTF-8.
    Ведущие нулевые байты отбрасываются.
    """
    data = value.to_bytes()
    data = data.lstrip(b"\x00")
    return data.decode("utf-8", errors="ignore")


# ---------- Тест простоты ----------
def is_probable_prime(n: CustomBigInt, rounds: int = 8) -> bool:
    """
    Вероятностный тест Миллера-Рабина.
    Для учебных размеров (64-128 бит) количества раундов достаточно.
    """
    if n.sign <= 0:
        return False
    if n == CustomBigInt(2) or n == CustomBigInt(3):
        return True
    if n == CustomBigInt(1) or not n.is_odd():
        return False

    # n - 1 = 2^s * d
    d = n.sub_small(1)
    s = 0
    while not d.is_zero():
        _, rem = d.div_mod_small(2)
        if rem != 0:
            break
        d, _ = d.div_mod_small(2)
        s += 1

    n_minus_one = n.sub_small(1)
    n_minus_two = n.sub_small(2)
    bits = n.bit_length()

    for _ in range(rounds):
        # Случайная база a в диапазоне [2, n-2]
        while True:
            a = CustomBigInt.random_bits(bits)
            if a._compare_abs(n_minus_two) > 0:
                a = a % n_minus_two
            a = a.add_small(2)
            if a._compare_abs(n_minus_two) <= 0:
                break

        x = CustomBigInt.pow_mod(a, d, n)
        if x == CustomBigInt(1) or x == n_minus_one:
            continue
        witness = True
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n_minus_one:
                witness = False
                break
        if witness:
            return False
    return True


def generate_prime(bits: int, rounds: int = 8) -> CustomBigInt:
    """
    Генерация вероятно простого числа нужной битовой длины.
    """
    if bits < 8:
        bits = 8
    while True:
        candidate = CustomBigInt.random_bits(bits)
        # Гарантируем нечётность.
        if candidate.is_odd() is False:
            candidate = candidate.add_small(1)
        if is_probable_prime(candidate, rounds):
            return candidate


# ---------- Расширенный алгоритм Евклида ----------
def extended_gcd(a: CustomBigInt, b: CustomBigInt) -> Tuple[CustomBigInt, CustomBigInt, CustomBigInt]:
    """
    Расширенный алгоритм Евклида.
    Возвращает кортеж (g, x, y), такой что ax + by = g = gcd(a, b).
    """
    if b.is_zero():
        return a, CustomBigInt(1), CustomBigInt(0)
    q, r = a.div_mod(b)
    g, x1, y1 = extended_gcd(b, r)
    x = y1
    y = x1 - q * y1
    return g, x, y


def mod_inverse(value: CustomBigInt, modulus: CustomBigInt) -> CustomBigInt:
    """
    Находит мультипликативную обратную величину value^-1 mod modulus.
    """
    g, x, _ = extended_gcd(value, modulus)
    if g != CustomBigInt(1):
        raise ValueError("Обратный элемент не существует")
    # Приводим результат к положительному остатку.
    _, rem = x.div_mod(modulus)
    if rem.sign < 0:
        rem = rem + modulus
    return rem


# ---------- Генерация ключей ----------
def generate_keypair(bits: int = 128) -> Dict[str, CustomBigInt]:
    """
    Генерирует пару ключей RSA указанной битовой длины модуля.
    Для учебных целей подходит диапазон 64-128 бит.
    """
    half = max(32, bits // 2)
    while True:
        p = generate_prime(half)
        q = generate_prime(bits - half)
        if p == q:
            continue
        n = p * q
        phi = (p.sub_small(1)) * (q.sub_small(1))
        g, _, _ = extended_gcd(DEFAULT_E, phi)
        if g != CustomBigInt(1):
            continue
        d = mod_inverse(DEFAULT_E, phi)
        return {"p": p, "q": q, "n": n, "phi": phi, "e": DEFAULT_E, "d": d}


# ---------- Шифрование / дешифрование ----------
def encrypt_text(plaintext: str, public_key: Dict[str, CustomBigInt]) -> str:
    """
    Шифрует строку plaintext с помощью открытого ключа.
    Возвращает шифртекст в hex-представлении.
    """
    m = text_to_bigint(plaintext)
    n = public_key["n"]
    e = public_key["e"]
    if m._compare_abs(n) >= 0:
        raise ValueError("Сообщение слишком длинное для выбранного модуля")
    c = CustomBigInt.pow_mod(m, e, n)
    return c.to_hex()


def decrypt_text(cipher_hex: str, private_key: Dict[str, CustomBigInt]) -> str:
    """
    Дешифрует hex-строку шифртекста с помощью закрытого ключа.
    """
    c = CustomBigInt.from_hex(cipher_hex)
    n = private_key["n"]
    d = private_key["d"]
    m = CustomBigInt.pow_mod(c, d, n)
    return bigint_to_text(m)


# ---------- Работа с файлами ключей ----------
def _parse_key_file(path: str) -> Dict[str, str]:
    """
    Разбирает файл формата key=value построчно.
    """
    data: Dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            if "=" not in line:
                continue
            key, val = line.strip().split("=", maxsplit=1)
            data[key.lower()] = val
    return data


def save_public_key(path: str, n: CustomBigInt, e: CustomBigInt) -> None:
    """
    Сохраняет открытый ключ (N, E) в текстовый файл.
    """
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f"N={n.to_decimal()}\n")
        fh.write(f"E={e.to_decimal()}\n")


def save_private_key(path: str, n: CustomBigInt, d: CustomBigInt, p: CustomBigInt, q: CustomBigInt) -> None:
    """
    Сохраняет закрытый ключ в файл.
    """
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f"N={n.to_decimal()}\n")
        fh.write(f"D={d.to_decimal()}\n")
        fh.write(f"P={p.to_decimal()}\n")
        fh.write(f"Q={q.to_decimal()}\n")


def load_public_key(path: str) -> Dict[str, CustomBigInt]:
    """
    Загружает открытый ключ из файла.
    """
    data = _parse_key_file(path)
    if "n" not in data or "e" not in data:
        raise ValueError("Файл открытого ключа поврежден или неполон")
    return {"n": CustomBigInt(data["n"]), "e": CustomBigInt(data["e"])}


def load_private_key(path: str) -> Dict[str, CustomBigInt]:
    """
    Загружает закрытый ключ из файла.
    """
    data = _parse_key_file(path)
    required = {"n", "d"}
    if not required.issubset(data.keys()):
        raise ValueError("Файл закрытого ключа поврежден или неполон")
    key = {
        "n": CustomBigInt(data["n"]),
        "d": CustomBigInt(data["d"]),
    }
    if "p" in data:
        key["p"] = CustomBigInt(data["p"])
    if "q" in data:
        key["q"] = CustomBigInt(data["q"])
    return key


def load_cipher_file(path: str) -> str:
    """
    Читает шифртекст из файла.
    """
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read().strip()


def save_cipher_file(path: str, cipher_hex: str) -> None:
    """
    Сохраняет шифртекст в файл.
    """
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(cipher_hex)
