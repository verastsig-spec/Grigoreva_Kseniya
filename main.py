import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

# Константы
HISTORY_FILE = "history.json"
MIN_LEN = 4
MAX_LEN = 64

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор случайных паролей")
        self.root.geometry("500x600")
        self.root.resizable(False, False)

        self.history = self.load_history()
        self.setup_ui()
        self.update_history_view()

    def setup_ui(self):
        # === Параметры длины ===
        ttk.Label(self.root, text="Длина пароля:", font=("Arial", 11)).pack(pady=(10, 0))
        self.len_var = tk.IntVar(value=12)
        self.slider = ttk.Scale(self.root, from_=MIN_LEN, to=MAX_LEN, variable=self.len_var, orient="horizontal")
        self.slider.pack(fill="x", padx=30)
        self.len_label = ttk.Label(self.root, textvariable=self.len_var, font=("Arial", 10))
        self.len_label.pack()

        # === Чекбоксы символов ===
        self.use_letters = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_special = tk.BooleanVar(value=False)

        chk_frame = ttk.Frame(self.root)
        chk_frame.pack(pady=10)
        ttk.Checkbutton(chk_frame, text="Буквы (A-Z, a-z)", variable=self.use_letters).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(chk_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=0, column=1, sticky="w", padx=20)
        ttk.Checkbutton(chk_frame, text="Спецсимволы (!@#...)", variable=self.use_special).grid(row=0, column=2, sticky="w")

        # === Кнопка генерации ===
        self.gen_btn = ttk.Button(self.root, text="Сгенерировать пароль", command=self.generate_password)
        self.gen_btn.pack(pady=15)

        # === Поле вывода ===
        self.password_var = tk.StringVar()
        self.out_entry = ttk.Entry(self.root, textvariable=self.password_var, font=("Courier", 14), state="readonly")
        self.out_entry.pack(fill="x", padx=30, pady=5)

        # === Таблица истории ===
        ttk.Label(self.root, text="История генераций:").pack(pady=(10, 0))
        cols = ("Дата", "Длина", "Пароль")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings", height=12)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120 if col != "Пароль" else 280, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=15, pady=10)

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                messagebox.showwarning("Внимание", "Файл истории повреждён. Создан новый.")
                return []
        return []

    def save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def update_history_view(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Отображаем последние 30 записей (самые новые сверху)
        for item in reversed(self.history[-30:]):
            self.tree.insert("", "end", values=(item["timestamp"], item["length"], item["password"]))

    def generate_password(self):
        length = self.len_var.get()

        # 4. Проверка корректности ввода длины
        if not (MIN_LEN <= length <= MAX_LEN):
            messagebox.showerror("Ошибка", f"Длина должна быть от {MIN_LEN} до {MAX_LEN}")
            return

        # Формирование набора символов
        charset = ""
        if self.use_letters.get(): charset += string.ascii_letters
        if self.use_digits.get(): charset += string.digits
        if self.use_special.get(): charset += "!@#$%^&*()-_=+[]{}|;:,.<>?/~`"

        if not charset:
            messagebox.showerror("Ошибка", "Выберите хотя бы один набор символов!")
            return

        # 2. Генерация через библиотеку random
        pwd_list = [random.choice(charset) for _ in range(length)]
        random.shuffle(pwd_list)
        final_pwd = "".join(pwd_list)

        self.password_var.set(final_pwd)

        # Сохранение в историю
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "length": length,
            "password": final_pwd,
            "settings": {
                "letters": self.use_letters.get(),
                "digits": self.use_digits.get(),
                "special": self.use_special.get()
            }
        }
        self.history.append(record)
        self.save_history()
        self.update_history_view()

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()
