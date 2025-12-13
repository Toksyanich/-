"""
Графический интерфейс RSA на Tkinter.
Три вкладки: генерация ключей, шифрование, дешифрование.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from rsa_math import (
    DEFAULT_E,
    decrypt_text,
    encrypt_text,
    generate_keypair,
    load_cipher_file,
    load_private_key,
    load_public_key,
    save_cipher_file,
    save_private_key,
    save_public_key,
)


class RSAApp(tk.Tk):
    """
    Основное окно приложения с вкладками.
    """

    def __init__(self) -> None:
        super().__init__()
        self.title("RSA (учебная реализация на CustomBigInt)")
        self.geometry("820x640")

        self.public_key = None
        self.private_key = None
        self.cipher_cache = ""

        self._build_layout()

    # ---------- Построение интерфейса ----------
    def _build_layout(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.tab_keys = ttk.Frame(notebook)
        self.tab_encrypt = ttk.Frame(notebook)
        self.tab_decrypt = ttk.Frame(notebook)

        notebook.add(self.tab_keys, text="Генерация ключей")
        notebook.add(self.tab_encrypt, text="Шифрование")
        notebook.add(self.tab_decrypt, text="Дешифрование")

        self._build_keys_tab()
        self._build_encrypt_tab()
        self._build_decrypt_tab()

    def _build_keys_tab(self) -> None:
        padding = {"padx": 8, "pady": 4}
        row = 0

        ttk.Label(self.tab_keys, text="Длина модуля (бит):").grid(row=row, column=0, sticky="w", **padding)
        self.bits_var = tk.StringVar(value="128")
        ttk.Entry(self.tab_keys, textvariable=self.bits_var, width=10).grid(row=row, column=1, sticky="w", **padding)
        ttk.Button(self.tab_keys, text="Сгенерировать ключи", command=self.on_generate_keys).grid(
            row=row, column=2, sticky="w", **padding
        )
        row += 1

        self._p_text = self._create_multiline(self.tab_keys, "P:", row)
        row += 1
        self._q_text = self._create_multiline(self.tab_keys, "Q:", row)
        row += 1
        self._n_text = self._create_multiline(self.tab_keys, "N:", row)
        row += 1
        self._e_text = self._create_multiline(self.tab_keys, "E:", row, default_value=str(DEFAULT_E))
        row += 1
        self._d_text = self._create_multiline(self.tab_keys, "D:", row)
        row += 1

        ttk.Button(self.tab_keys, text="Сохранить открытый ключ", command=self.on_save_public).grid(
            row=row, column=0, sticky="w", **padding
        )
        ttk.Button(self.tab_keys, text="Сохранить закрытый ключ", command=self.on_save_private).grid(
            row=row, column=1, sticky="w", **padding
        )

    def _build_encrypt_tab(self) -> None:
        padding = {"padx": 8, "pady": 4}
        row = 0

        ttk.Button(self.tab_encrypt, text="Загрузить открытый ключ", command=self.on_load_public).grid(
            row=row, column=0, sticky="w", **padding
        )
        self.pub_status = tk.StringVar(value="Ключ не загружен")
        ttk.Label(self.tab_encrypt, textvariable=self.pub_status).grid(row=row, column=1, sticky="w", **padding)
        row += 1

        ttk.Label(self.tab_encrypt, text="Исходный текст:").grid(row=row, column=0, sticky="w", **padding)
        self.plain_text = tk.Text(self.tab_encrypt, width=80, height=8)
        self.plain_text.grid(row=row + 1, column=0, columnspan=3, sticky="nsew", **padding)
        row += 2

        ttk.Button(self.tab_encrypt, text="Зашифровать", command=self.on_encrypt).grid(
            row=row, column=0, sticky="w", **padding
        )
        row += 1

        ttk.Label(self.tab_encrypt, text="Шифртекст (HEX):").grid(row=row, column=0, sticky="w", **padding)
        self.cipher_text = tk.Text(self.tab_encrypt, width=80, height=8)
        self.cipher_text.grid(row=row + 1, column=0, columnspan=3, sticky="nsew", **padding)
        row += 2

        ttk.Button(self.tab_encrypt, text="Сохранить шифр в файл", command=self.on_save_cipher).grid(
            row=row, column=0, sticky="w", **padding
        )

    def _build_decrypt_tab(self) -> None:
        padding = {"padx": 8, "pady": 4}
        row = 0

        ttk.Button(self.tab_decrypt, text="Загрузить шифртекст из файла", command=self.on_load_cipher).grid(
            row=row, column=0, sticky="w", **padding
        )
        ttk.Button(self.tab_decrypt, text="Загрузить закрытый ключ", command=self.on_load_private).grid(
            row=row, column=1, sticky="w", **padding
        )
        self.priv_status = tk.StringVar(value="Ключ не загружен")
        ttk.Label(self.tab_decrypt, textvariable=self.priv_status).grid(row=row, column=2, sticky="w", **padding)
        row += 1

        ttk.Label(self.tab_decrypt, text="Шифртекст (HEX):").grid(row=row, column=0, sticky="w", **padding)
        self.cipher_input = tk.Text(self.tab_decrypt, width=80, height=8)
        self.cipher_input.grid(row=row + 1, column=0, columnspan=3, sticky="nsew", **padding)
        row += 2

        ttk.Button(self.tab_decrypt, text="Расшифровать", command=self.on_decrypt).grid(
            row=row, column=0, sticky="w", **padding
        )
        row += 1

        ttk.Label(self.tab_decrypt, text="Расшифрованный текст:").grid(row=row, column=0, sticky="w", **padding)
        self.plain_output = tk.Text(self.tab_decrypt, width=80, height=8)
        self.plain_output.grid(row=row + 1, column=0, columnspan=3, sticky="nsew", **padding)

    def _create_multiline(self, parent, label: str, row: int, default_value: str = "") -> tk.Text:
        """
        Утилита для пары метка+многострочное поле только для чтения.
        """
        padding = {"padx": 8, "pady": 4}
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="nw", **padding)
        txt = tk.Text(parent, width=80, height=4, state="normal")
        txt.insert("1.0", default_value)
        txt.configure(state="disabled")
        txt.grid(row=row, column=1, columnspan=2, sticky="nsew", **padding)
        return txt

    def _set_text(self, widget: tk.Text, value: str) -> None:
        """
        Обновляет содержимое text-widget в режиме только для чтения.
        """
        widget.configure(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, value)
        widget.configure(state="disabled")

    # ---------- Обработчики ----------
    def on_generate_keys(self) -> None:
        """
        Генерирует новую пару ключей и выводит параметры на экран.
        """
        try:
            bits = int(self.bits_var.get())
            if bits < 32:
                raise ValueError("Минимальная длина - 32 бита")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Ошибка", f"Некорректная длина: {exc}")
            return

        self.pub_status.set("Генерация...")
        self.update_idletasks()
        try:
            keys = generate_keypair(bits)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Ошибка", f"Не удалось сгенерировать ключ: {exc}")
            return

        self.public_key = {"n": keys["n"], "e": keys["e"]}
        self.private_key = {"n": keys["n"], "d": keys["d"], "p": keys["p"], "q": keys["q"]}
        self._set_text(self._p_text, str(keys["p"]))
        self._set_text(self._q_text, str(keys["q"]))
        self._set_text(self._n_text, str(keys["n"]))
        self._set_text(self._e_text, str(keys["e"]))
        self._set_text(self._d_text, str(keys["d"]))
        self.pub_status.set("Открытый ключ готов")
        self.priv_status.set("Закрытый ключ готов")
        messagebox.showinfo("Готово", "Ключи успешно сгенерированы")

    def on_save_public(self) -> None:
        """
        Сохраняет открытый ключ в файл.
        """
        if not self.public_key:
            messagebox.showwarning("Внимание", "Сначала сгенерируйте или загрузите ключ")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".pub",
            filetypes=[("Key files", "*.pub"), ("All files", "*.*")],
            title="Сохранить открытый ключ",
        )
        if not path:
            return
        save_public_key(path, self.public_key["n"], self.public_key["e"])
        messagebox.showinfo("Готово", f"Открытый ключ сохранён: {path}")

    def on_save_private(self) -> None:
        """
        Сохраняет закрытый ключ в файл.
        """
        if not self.private_key:
            messagebox.showwarning("Внимание", "Сначала сгенерируйте ключ")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".key",
            filetypes=[("Key files", "*.key"), ("All files", "*.*")],
            title="Сохранить закрытый ключ",
        )
        if not path:
            return
        save_private_key(path, self.private_key["n"], self.private_key["d"], self.private_key["p"], self.private_key["q"])
        messagebox.showinfo("Готово", f"Закрытый ключ сохранён: {path}")

    def on_load_public(self) -> None:
        """
        Загружает открытый ключ из файла.
        """
        path = filedialog.askopenfilename(
            filetypes=[("Key files", "*.pub;*.key;*.txt"), ("All files", "*.*")],
            title="Выберите файл открытого ключа",
        )
        if not path:
            return
        try:
            self.public_key = load_public_key(path)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Ошибка", f"Не удалось загрузить ключ: {exc}")
            return
        self.pub_status.set(f"Открытый ключ: {path}")
        messagebox.showinfo("Готово", "Открытый ключ загружен")

    def on_load_private(self) -> None:
        """
        Загружает закрытый ключ из файла.
        """
        path = filedialog.askopenfilename(
            filetypes=[("Key files", "*.key;*.txt"), ("All files", "*.*")],
            title="Выберите файл закрытого ключа",
        )
        if not path:
            return
        try:
            self.private_key = load_private_key(path)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Ошибка", f"Не удалось загрузить ключ: {exc}")
            return
        self.priv_status.set(f"Закрытый ключ: {path}")
        messagebox.showinfo("Готово", "Закрытый ключ загружен")

    def on_encrypt(self) -> None:
        """
        Шифрует текст из поля ввода, выводит HEX-шифртекст.
        """
        if not self.public_key:
            messagebox.showwarning("Внимание", "Загрузите или сгенерируйте открытый ключ")
            return
        plaintext = self.plain_text.get("1.0", tk.END).strip()
        if not plaintext:
            messagebox.showwarning("Внимание", "Введите текст для шифрования")
            return
        try:
            cipher_hex = encrypt_text(plaintext, self.public_key)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Ошибка", f"Не удалось зашифровать: {exc}")
            return
        self.cipher_cache = cipher_hex
        self.cipher_text.configure(state="normal")
        self.cipher_text.delete("1.0", tk.END)
        self.cipher_text.insert(tk.END, cipher_hex)
        self.cipher_text.configure(state="disabled")
        messagebox.showinfo("Готово", "Сообщение зашифровано")

    def on_save_cipher(self) -> None:
        """
        Сохраняет последний шифртекст в файл.
        """
        cipher_hex = self.cipher_text.get("1.0", tk.END).strip()
        if not cipher_hex:
            messagebox.showwarning("Внимание", "Нет данных для сохранения")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".enc",
            filetypes=[("Encrypted files", "*.enc"), ("All files", "*.*")],
            title="Сохранить шифртекст",
        )
        if not path:
            return
        save_cipher_file(path, cipher_hex)
        messagebox.showinfo("Готово", f"Шифртекст сохранён: {path}")

    def on_load_cipher(self) -> None:
        """
        Загружает шифртекст из файла во вкладку расшифровки.
        """
        path = filedialog.askopenfilename(
            filetypes=[("Encrypted files", "*.enc;*.txt"), ("All files", "*.*")],
            title="Выберите файл шифртекста",
        )
        if not path:
            return
        try:
            cipher_hex = load_cipher_file(path)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл: {exc}")
            return
        self.cipher_input.delete("1.0", tk.END)
        self.cipher_input.insert(tk.END, cipher_hex)
        messagebox.showinfo("Готово", "Шифртекст загружен")

    def on_decrypt(self) -> None:
        """
        Дешифрует шифртекст из поля ввода при наличии закрытого ключа.
        """
        if not self.private_key:
            messagebox.showwarning("Внимание", "Загрузите закрытый ключ")
            return
        cipher_hex = self.cipher_input.get("1.0", tk.END).strip()
        if not cipher_hex:
            messagebox.showwarning("Внимание", "Введите или загрузите шифртекст")
            return
        try:
            plaintext = decrypt_text(cipher_hex, self.private_key)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Ошибка", f"Не удалось расшифровать: {exc}")
            return
        self.plain_output.delete("1.0", tk.END)
        self.plain_output.insert(tk.END, plaintext)
        messagebox.showinfo("Готово", "Сообщение расшифровано")


def run_app() -> None:
    """
    Запускает окно приложения.
    """
    app = RSAApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
