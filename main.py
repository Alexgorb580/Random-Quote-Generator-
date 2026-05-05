# main.py
#!/usr/bin/env python3
# Random Quote Generator - GUI с использованием Tkinter
# Автор: [Ваше Имя Фамилия] (заменить перед публикацией)

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import random
from datetime import datetime

# Импорт предопределённых цитат
from quotes_data import quotes

HISTORY_FILE = "quotes_history.json"

class QuoteGeneratorApp:
    def __init__(self, root):
        self.root = root
        root.title("Random Quote Generator")

        # История
        self.history = self.load_history()

        # Фильтры
        self.author_list = ["Все"] + sorted({q["author"] for q in quotes})
        self.theme_list = ["Все"] + sorted({q["theme"] for q in quotes})

        self.author_var = tk.StringVar(value="Все")
        self.theme_var = tk.StringVar(value="Все")

        # Текущая цитата
        self.current_text = tk.StringVar(value="Нажмите 'Сгенерировать цитату'")
        self.current_meta = tk.StringVar(value="")

        # UI Раздел 1: Цитата и кнопка
        quote_frame = ttk.LabelFrame(root, text="Цитата")
        quote_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.quote_label = ttk.Label(quote_frame, textvariable=self.current_text,
                                     wraplength=600, justify="center",
                                     font=("Arial", 14))
        self.quote_label.grid(row=0, column=0, padx=10, pady=(12,6), sticky="ew")

        self.meta_label = ttk.Label(quote_frame, textvariable=self.current_meta,
                                    font=("Arial", 10, "italic"))
        self.meta_label.grid(row=1, column=0, padx=10, pady=(0,12), sticky="ew")

        self.generate_btn = ttk.Button(quote_frame, text="Сгенерировать цитату", command=self.generate_quote)
        self.generate_btn.grid(row=2, column=0, pady=6)

        # UI Раздел 2: Фильтры
        filter_frame = ttk.LabelFrame(root, text="Фильтры")
        filter_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Автор
        author_label = ttk.Label(filter_frame, text="Автор:")
        author_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.author_cb = ttk.Combobox(filter_frame, values=self.author_list, state="readonly",
                                      textvariable=self.author_var)
        self.author_cb.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.author_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_history_table())

        # Тема
        theme_label = ttk.Label(filter_frame, text="Тема:")
        theme_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.theme_cb = ttk.Combobox(filter_frame, values=self.theme_list, state="readonly",
                                     textvariable=self.theme_var)
        self.theme_cb.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.theme_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_history_table())

        # UI Раздел 3: История
        history_frame = ttk.LabelFrame(root, text="История цитат")
        history_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        columns = ("text", "author", "theme", "time")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            if col == "text":
                self.tree.column(col, width=320, anchor="w")
            else:
                self.tree.column(col, width=120, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)

        history_frame.rowconfigure(0, weight=1)
        history_frame.columnconfigure(0, weight=1)

        # Настройка сетки главного окна
        root.grid_rowconfigure(2, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # Инициализация таблицы истории
        self.refresh_history_table()

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
            except Exception:
                pass
        return []

    def save_history(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Ошибка сохранения истории:", e)

    def generate_quote(self):
        # Фильтры применяются к pool цитат
        pool = quotes
        author_filter = self.author_var.get()
        theme_filter = self.theme_var.get()

        if author_filter != "Все":
            pool = [q for q in pool if q["author"] == author_filter]
        if theme_filter != "Все":
            pool = [q for q in pool if q["theme"] == theme_filter]

        if not pool:
            messagebox.showinfo("Нет цитат", "Нет цитат под выбранными фильтрами.")
            return

        q = random.choice(pool)

        self.current_text.set(q["text"])
        self.current_meta.set(f"Автор: {q['author']} | Тема: {q['theme']}")

        entry = {
            "text": q["text"],
            "author": q["author"],
            "theme": q["theme"],
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(entry)
        self.save_history()
        self.refresh_history_table()

    def refresh_history_table(self):
        # Очистить
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Фильтры History по текущим значениям
        f_author = self.author_var.get()
        f_theme = self.theme_var.get()

        for entry in self.history:
            if (f_author == "Все" or entry["author"] == f_author) and \
               (f_theme == "Все" or entry["theme"] == f_theme):
                text_display = entry["text"]
                if len(text_display) > 320:
                    text_display = text_display[:317] + "..."
                self.tree.insert('', 'end', values=(
                    text_display,
                    entry["author"],
                    entry["theme"],
                    entry["time"]
                ))

def main():
    root = tk.Tk()
    app = QuoteGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()