"""
Модуль bigint.py содержит реализацию класса CustomBigInt для длинной арифметики.
Все операции работают «в столбик» поверх массива цифр с фиксированным основанием.
"""

from __future__ import annotations

import math
import secrets
from typing import List, Tuple


class CustomBigInt:
    """
    Класс длинного целого числа.

    Число хранится в виде списка цифр digits (младшие разряды первыми) в основании BASE.
    sign принимает значения:
    - 1  -> положительное число
    - -1 -> отрицательное число
    - 0  -> ноль
    """

    BASE = 10**9
    BASE_DIGITS = 9

    def __init__(self, value: int | str | "CustomBigInt" = 0):
        self.digits: List[int] = [0]
        self.sign: int = 0
        if isinstance(value, CustomBigInt):
            self.digits = value.digits[:]
            self.sign = value.sign
            self._normalize()
        elif isinstance(value, str):
            self._from_string(value.strip())
        else:
            self._from_int(int(value))

    @classmethod
    def from_digits(cls, digits: List[int], sign: int) -> "CustomBigInt":
        """
        Вспомогательный конструктор из массива цифр и знака.
        """
        obj = cls(0)
        obj.digits = digits[:]
        obj.sign = 0 if all(d == 0 for d in obj.digits) else (1 if sign >= 0 else -1)
        obj._normalize()
        return obj

    @classmethod
    def random_bits(cls, bits: int) -> "CustomBigInt":
        """
        Генерация случайного числа заданной битовой длины.
        Топовый бит принудительно устанавливается в 1, чтобы длина не уменьшалась.
        """
        if bits <= 1:
            return cls(1)
        # Количество "больших" цифр в основании BASE, необходимое для bits.
        bits_per_digit = int(math.log2(cls.BASE))
        digits_count = (bits + bits_per_digit - 1) // bits_per_digit
        digits = [secrets.randbelow(cls.BASE) for _ in range(digits_count)]
        # Гарантируем ненулевой старший разряд с нужной битовой длиной.
        top_bits = bits - (digits_count - 1) * bits_per_digit
        min_top = 1 << (top_bits - 1)
        max_top = (1 << top_bits) - 1
        digits[-1] = secrets.randbelow(max_top - min_top + 1) + min_top
        # Обеспечиваем нечётность числа для последующих тестов на простоту.
        if digits[0] % 2 == 0:
            digits[0] += 1
        return cls.from_digits(digits, 1)

    def _from_int(self, value: int) -> None:
        """
        Инициализация из обычного целого (используется только для небольших значений).
        """
        if value == 0:
            self.digits = [0]
            self.sign = 0
            return
        sign = 1
        if value < 0:
            sign = -1
            value = -value
        digits = []
        while value > 0:
            digits.append(value % self.BASE)
            value //= self.BASE
        self.digits = digits
        self.sign = sign
        self._normalize()

    def _from_string(self, text: str) -> None:
        """
        Инициализация из десятичной строки.
        """
        if not text:
            self._from_int(0)
            return
        sign = 1
        if text[0] == "-":
            sign = -1
            text = text[1:]
        text = text.lstrip("0")
        if not text:
            self._from_int(0)
            return
        digits = []
        for i in range(len(text), 0, -self.BASE_DIGITS):
            start = max(0, i - self.BASE_DIGITS)
            chunk = int(text[start:i]) if start < i else 0
            digits.append(chunk)
        self.digits = digits
        self.sign = sign
        self._normalize()

    def _normalize(self) -> None:
        """
        Удаление ведущих нулей и нормализация знака.
        """
        while len(self.digits) > 1 and self.digits[-1] == 0:
            self.digits.pop()
        if len(self.digits) == 1 and self.digits[0] == 0:
            self.sign = 0
        elif self.sign == 0:
            self.sign = 1

    def copy(self) -> "CustomBigInt":
        """
        Возвращает копию числа.
        """
        return CustomBigInt.from_digits(self.digits, self.sign)

    def is_zero(self) -> bool:
        """
        Проверка на ноль.
        """
        return self.sign == 0

    def is_odd(self) -> bool:
        """
        Проверка нечётности числа по младшему разряду.
        """
        return self.digits[0] % 2 == 1

    def bit_length(self) -> int:
        """
        Оценка битовой длины числа.
        """
        if self.is_zero():
            return 0
        return (len(self.digits) - 1) * int(math.log2(self.BASE)) + self.digits[-1].bit_length()

    # ---------- Сравнения ----------
    def _compare_abs(self, other: "CustomBigInt") -> int:
        """
        Сравнение по модулю.
        Возвращает -1 если |self| < |other|, 0 если равны, 1 если |self| > |other|.
        """
        if len(self.digits) != len(other.digits):
            return -1 if len(self.digits) < len(other.digits) else 1
        for a, b in zip(reversed(self.digits), reversed(other.digits)):
            if a != b:
                return -1 if a < b else 1
        return 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CustomBigInt):
            return False
        return self.sign == other.sign and self.digits == other.digits

    def __lt__(self, other: "CustomBigInt") -> bool:
        if self.sign != other.sign:
            return self.sign < other.sign
        if self.sign == 0:
            return False
        cmp = self._compare_abs(other)
        return cmp < 0 if self.sign > 0 else cmp > 0

    def __le__(self, other: "CustomBigInt") -> bool:
        return self == other or self < other

    def __gt__(self, other: "CustomBigInt") -> bool:
        return not self <= other

    def __ge__(self, other: "CustomBigInt") -> bool:
        return not self < other

    # ---------- Арифметика ----------
    def __neg__(self) -> "CustomBigInt":
        if self.is_zero():
            return CustomBigInt(0)
        return CustomBigInt.from_digits(self.digits, -self.sign)

    def __abs__(self) -> "CustomBigInt":
        return CustomBigInt.from_digits(self.digits, 1 if not self.is_zero() else 0)

    def __add__(self, other: "CustomBigInt") -> "CustomBigInt":
        """
        Сложение двух длинных чисел с учётом знака.
        """
        if self.sign == 0:
            return other.copy()
        if other.sign == 0:
            return self.copy()
        if self.sign == other.sign:
            return self._add_abs(other, self.sign)
        cmp = self._compare_abs(other)
        if cmp == 0:
            return CustomBigInt(0)
        if cmp > 0:
            return self._sub_abs(other, self.sign)
        return other._sub_abs(self, other.sign)

    def __sub__(self, other: "CustomBigInt") -> "CustomBigInt":
        """
        Вычитание двух длинных чисел с учётом знака.
        """
        if other.sign == 0:
            return self.copy()
        if self.sign == 0:
            return -other
        if self.sign != other.sign:
            return self._add_abs(other, self.sign)
        cmp = self._compare_abs(other)
        if cmp == 0:
            return CustomBigInt(0)
        if cmp > 0:
            return self._sub_abs(other, self.sign)
        return other._sub_abs(self, -other.sign)

    def _add_abs(self, other: "CustomBigInt", sign: int) -> "CustomBigInt":
        """
        Сложение модулей чисел «в столбик».
        """
        max_len = max(len(self.digits), len(other.digits))
        result = []
        carry = 0
        for i in range(max_len):
            a = self.digits[i] if i < len(self.digits) else 0
            b = other.digits[i] if i < len(other.digits) else 0
            total = a + b + carry
            if total >= self.BASE:
                carry = 1
                total -= self.BASE
            else:
                carry = 0
            result.append(total)
        if carry:
            result.append(carry)
        return CustomBigInt.from_digits(result, sign)

    def _sub_abs(self, other: "CustomBigInt", sign: int) -> "CustomBigInt":
        """
        Вычитание модулей чисел (предполагается |self| >= |other|).
        """
        result = []
        borrow = 0
        for i in range(len(self.digits)):
            a = self.digits[i]
            b = other.digits[i] if i < len(other.digits) else 0
            diff = a - b - borrow
            if diff < 0:
                diff += self.BASE
                borrow = 1
            else:
                borrow = 0
            result.append(diff)
        return CustomBigInt.from_digits(result, sign)

    def __mul__(self, other: "CustomBigInt") -> "CustomBigInt":
        """
        Умножение двух длинных чисел методом «в столбик».
        """
        if self.is_zero() or other.is_zero():
            return CustomBigInt(0)
        result = [0] * (len(self.digits) + len(other.digits))
        for i, a in enumerate(self.digits):
            carry = 0
            for j, b in enumerate(other.digits):
                idx = i + j
                cur = result[idx] + a * b + carry
                result[idx] = cur % self.BASE
                carry = cur // self.BASE
            result[i + len(other.digits)] += carry
        return CustomBigInt.from_digits(result, self.sign * other.sign)

    def _mul_small(self, factor: int) -> "CustomBigInt":
        """
        Умножение на маленькое целое (используется внутри алгоритмов деления).
        """
        if factor == 0 or self.is_zero():
            return CustomBigInt(0)
        result = []
        carry = 0
        for d in self.digits:
            cur = d * factor + carry
            result.append(cur % self.BASE)
            carry = cur // self.BASE
        if carry:
            result.append(carry)
        return CustomBigInt.from_digits(result, self.sign)

    def _div_mod_small_abs(self, divisor: int) -> Tuple[List[int], int]:
        """
        Деление положительного числа на маленький делитель.
        Возвращает (digits частного, остаток).
        """
        remainder = 0
        quotient: List[int] = []
        for d in reversed(self.digits):
            cur = remainder * self.BASE + d
            q = cur // divisor
            remainder = cur - q * divisor
            quotient.append(q)
        quotient.reverse()
        return quotient, remainder

    def div_mod_small(self, divisor: int) -> Tuple["CustomBigInt", int]:
        """
        Деление на маленький делитель с сохранением знака.
        """
        if divisor == 0:
            raise ZeroDivisionError("Деление на ноль")
        if self.is_zero():
            return CustomBigInt(0), 0
        sign = self.sign if divisor > 0 else -self.sign
        divisor = abs(divisor)
        q_digits, rem = self._div_mod_small_abs(divisor)
        quotient = CustomBigInt.from_digits(q_digits, sign)
        if self.sign < 0 and rem != 0:
            rem = -rem
        return quotient, rem

    def _div_mod_abs(self, divisor_digits: List[int]) -> Tuple[List[int], List[int]]:
        """
        Деление положительных чисел |self| / |divisor| методом Кнута (алгоритм D).
        Возвращает пары массивов цифр (частное, остаток).
        """
        if len(divisor_digits) == 1:
            q_digits, rem = self._div_mod_small_abs(divisor_digits[0])
            return q_digits, [rem]

        m = len(divisor_digits)
        n = len(self.digits)
        # Нормализация: делитель должен иметь старший разряд не меньше BASE/2.
        d = self.BASE // (divisor_digits[-1] + 1)
        u = self._mul_small(d).digits  # нормализованный делимое
        v = CustomBigInt.from_digits(divisor_digits, 1)._mul_small(d).digits
        u.append(0)
        q = [0] * (n - m + 1)

        for j in range(n - m, -1, -1):
            # Оценка цифры частного.
            u_high = u[j + m]
            u_next = u[j + m - 1]
            u_prev = u[j + m - 2] if m >= 2 else 0
            numerator = u_high * self.BASE + u_next
            q_hat = numerator // v[m - 1]
            if q_hat >= self.BASE:
                q_hat = self.BASE - 1
            # Уточнение оценки, используя следующий разряд.
            while m >= 2 and q_hat * v[m - 2] > (numerator - q_hat * v[m - 1]) * self.BASE + u_prev:
                q_hat -= 1

            # Вычитание q_hat * v из соответствующего фрагмента u.
            borrow = 0
            for i in range(m):
                cur = u[j + i] - q_hat * v[i] - borrow
                if cur < 0:
                    borrow = (-cur + self.BASE - 1) // self.BASE
                    cur += borrow * self.BASE
                else:
                    borrow = 0
                u[j + i] = cur
            u[j + m] -= borrow

            # Если получилось отрицательно, корректируем.
            if u[j + m] < 0:
                q_hat -= 1
                carry = 0
                for i in range(m):
                    cur = u[j + i] + v[i] + carry
                    if cur >= self.BASE:
                        carry = 1
                        cur -= self.BASE
                    else:
                        carry = 0
                    u[j + i] = cur
                u[j + m] += carry
            q[j] = q_hat

        # Остаток «разнормализуем» обратно.
        remainder_digits, _ = CustomBigInt.from_digits(u[:m], 1)._div_mod_small_abs(d)
        return q, remainder_digits

    def div_mod(self, other: "CustomBigInt") -> Tuple["CustomBigInt", "CustomBigInt"]:
        """
        Деление на другое длинное число. Возвращает (частное, остаток).
        """
        if other.is_zero():
            raise ZeroDivisionError("Деление на ноль")
        if self.is_zero():
            return CustomBigInt(0), CustomBigInt(0)

        sign_q = 1 if self.sign == other.sign else -1
        abs_self = abs(self)
        abs_other = abs(other)

        if abs_self._compare_abs(abs_other) < 0:
            return CustomBigInt(0), self.copy()

        if len(abs_other.digits) == 1:
            q_digits, rem = abs_self._div_mod_small_abs(abs_other.digits[0])
            quotient = CustomBigInt.from_digits(q_digits, sign_q)
            remainder = CustomBigInt(rem)
            remainder.sign = 0 if rem == 0 else self.sign
            remainder._normalize()
            return quotient, remainder

        q_digits, r_digits = abs_self._div_mod_abs(abs_other.digits)
        quotient = CustomBigInt.from_digits(q_digits, sign_q)
        remainder = CustomBigInt.from_digits(r_digits, self.sign)
        return quotient, remainder

    def __floordiv__(self, other: "CustomBigInt") -> "CustomBigInt":
        q, _ = self.div_mod(other)
        return q

    def __mod__(self, other: "CustomBigInt") -> "CustomBigInt":
        _, r = self.div_mod(other)
        return r

    @staticmethod
    def pow_mod(base: "CustomBigInt", exponent: "CustomBigInt", modulus: "CustomBigInt") -> "CustomBigInt":
        """
        Быстрое возведение в степень по модулю (бин. возведение).
        Используются только операции длинной арифметики.
        """
        if modulus.is_zero():
            raise ZeroDivisionError("Модуль нулевой")
        result = CustomBigInt(1)
        base_mod = base % modulus
        exp = exponent.copy()
        while not exp.is_zero():
            if exp.is_odd():
                result = (result * base_mod) % modulus
            exp, _ = exp.div_mod_small(2)
            base_mod = (base_mod * base_mod) % modulus
        return result

    # ---------- Преобразования ----------
    def to_decimal(self) -> str:
        """
        Преобразование в десятичную строку.
        """
        if self.is_zero():
            return "0"
        chunks = [str(self.digits[-1])]
        for d in reversed(self.digits[:-1]):
            chunks.append(str(d).zfill(self.BASE_DIGITS))
        prefix = "-" if self.sign < 0 else ""
        return prefix + "".join(chunks)

    def __str__(self) -> str:
        return self.to_decimal()

    def to_hex(self) -> str:
        """
        Представление числа в шестнадцатеричной строке через байтовое разложение.
        """
        if self.is_zero():
            return "00"
        data = self.to_bytes()
        return data.hex()

    @classmethod
    def from_hex(cls, hex_string: str) -> "CustomBigInt":
        """
        Создание числа из шестнадцатеричной строки.
        """
        hex_string = hex_string.strip()
        if len(hex_string) % 2 == 1:
            hex_string = "0" + hex_string
        data = bytes.fromhex(hex_string)
        return cls.from_bytes(data)

    def to_bytes(self) -> bytes:
        """
        Разложение числа на массив байт (big-endian) через деление на 256.
        """
        if self.is_zero():
            return b"\x00"
        temp = self.copy()
        out = []
        while not temp.is_zero():
            temp, rem = temp.div_mod_small(256)
            out.append(rem if rem >= 0 else -rem)
        out.reverse()
        return bytes(out)

    @classmethod
    def from_bytes(cls, data: bytes) -> "CustomBigInt":
        """
        Сборка числа из массива байт (big-endian).
        """
        result = cls(0)
        for b in data:
            # result = result * 256 + b
            result = result._mul_small(256)
            result = result + cls(b)
        return result

    # ---------- Вспомогательные операции со "малыми" числами ----------
    def add_small(self, value: int) -> "CustomBigInt":
        """
        Прибавление маленького int (по модулю < BASE).
        """
        return self + CustomBigInt(value)

    def sub_small(self, value: int) -> "CustomBigInt":
        """
        Вычитание маленького int.
        """
        return self - CustomBigInt(value)
