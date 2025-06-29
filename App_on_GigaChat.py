import tkinter as tk
import tkinter.ttk as ttk
import re
import json

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from datetime import datetime

DATA_FILE = "todo_data(GigaChat).json"


# Базовая структура осталась прежней
class App(tk.Tk):
    def __init__(self):

        super().__init__()

        self.minsize(800, 600)
        # self.geometry("400x300")

        self.title("To-Do Journal")

        # Меню сверху
        top_frame = tk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        # Кнопки для переключения страниц
        btn_tasks = tk.Button(top_frame, text="Задачи", command=lambda: self.show_page(TasksPage))
        btn_tasks.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.X)

        btn_notes = tk.Button(top_frame, text="Заметки", command=lambda: self.show_page(NotesPage))
        btn_notes.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.X)

        btn_stats = tk.Button(top_frame, text="Статистика", command=lambda: self.show_page(StatsPage))
        btn_stats.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.X)

        # Главный контейнер для хранения различных страниц
        container = tk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)

        # Словарь для хранения созданных страниц
        self.pages = {}

        # Список классов страниц
        pages = [TasksPage, NotesPage, StatsPage]

        self.current = None

        # Создание и размещение всех страниц
        for PageClass in pages:
            page = PageClass(container, self)
            self.pages[PageClass] = page

        # По умолчанию показываем страницу "Задачи"
        self.show_page(TasksPage)

        self.load_data()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_data(self):

        tasks_data = None
        notes_data = None

        with open(DATA_FILE, "r", encoding="utf-8") as file:
            loaded_data = json.load(file)

            tasks_data = loaded_data.get("tasks", [])
            notes_data = loaded_data.get("notes", [])

        self.pages[TasksPage].tasks_data = tasks_data
        self.pages[TasksPage].update()
        self.pages[NotesPage].notes_data = notes_data
        self.pages[NotesPage].update()

    def save_data(self):

        data_to_save = {

            "tasks": self.pages[TasksPage].tasks_data,
            "notes": self.pages[NotesPage].notes_data

        }

        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data_to_save, file, ensure_ascii=False, indent=4)

    def on_closing(self):

        self.save_data()

        self.destroy()

    def show_page(self, page_class):
        """Поднимаем указанную страницу вверх"""
        if self.current:
            self.current.pack_forget()

        page = self.pages.get(page_class)

        if page is not None:

            page.pack(expand=True, fill=tk.BOTH)

            if page_class is StatsPage:
                page.update()

            self.current = page


class TasksPage(tk.Frame):

    def update(self):

        for child in self.treeview.get_children():
            self.treeview.delete(child)

        for i, task in enumerate(self.tasks_data):
            completed_text = "Да" if task["completed"] else "Нет"
            self.treeview.insert("", "end", text=str(i + 1),
                                 values=(task['task'], task['category'], task['due_date'], completed_text))

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Поисковая панель
        search_frame = tk.Frame(self)
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        # Надпись "Поиск:"
        lbl_search = tk.Label(search_frame, text="Поиск:")
        lbl_search.pack(side=tk.LEFT)

        # Поле для ввода текста поиска
        entry_search = tk.Entry(search_frame)
        entry_search.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry_search.bind("<KeyRelease>", lambda event: self.filter_table(entry_search.get(), category_var.get()))

        # Выбор категории
        categories = ["Все", "Работа", "Учеба", "Дом", "Здоровье", "Другое"]
        category_var = tk.StringVar(value="Все")
        self.combo_category = ttk.Combobox(search_frame, textvariable=category_var, state="readonly", values=categories)
        self.combo_category.pack(side=tk.RIGHT)
        self.combo_category.bind("<<ComboboxSelected>>", lambda event: self.filter_table(entry_search.get(),
                                                                                         category_var.get()))  # Привязываем событие смены категории

        # Основная таблица задач
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.treeview = ttk.Treeview(main_frame, columns=("task", "category", "due_date", "completed"))
        self.treeview.heading("#0", text="№")
        self.treeview.column("#0", width=50)
        self.treeview.heading("task", text="Задача")
        self.treeview.column("task", width=200)
        self.treeview.heading("category", text="Категория")
        self.treeview.column("category", width=100)
        self.treeview.heading("due_date", text="Срок выполнения")
        self.treeview.column("due_date", width=120)
        self.treeview.heading("completed", text="Выполнено")
        self.treeview.column("completed", width=70)

        # Исходные данные
        self.tasks_data = []

        # Наполняем таблицу исходными данными
        for i, task in enumerate(self.tasks_data):
            completed_text = "Да" if task["completed"] else "Нет"
            self.treeview.insert("", "end", text=str(i + 1),
                                 values=(task['task'], task['category'], task['due_date'], completed_text))

        # Привязываем событие для фильтра по полю ввода
        self.treeview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Нижняя панель с кнопками
        buttons_frame = tk.Frame(self)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        # Кнопки действий
        btn_add = tk.Button(buttons_frame, text="Добавить")
        btn_edit = tk.Button(buttons_frame, text="Редактировать")
        btn_delete = tk.Button(buttons_frame, text="Удалить")
        btn_mark_done = tk.Button(buttons_frame, text="Отметить выполненной")

        # Размещение кнопок слева направо
        btn_add.pack(side=tk.LEFT, padx=5)
        btn_edit.pack(side=tk.LEFT, padx=5)
        btn_delete.pack(side=tk.LEFT, padx=5)
        btn_mark_done.pack(side=tk.LEFT, padx=5)

        btn_add.config(command=lambda: self.add_task())
        btn_edit.config(command=lambda: self.edit_task())
        btn_delete.config(command=lambda: self.delete_task())
        btn_mark_done.config(command=lambda: self.mark_as_completed())

        # Форму для новых задач ниже кнопок
        form_frame = tk.Frame(self)
        form_frame.pack(fill=tk.X, padx=10, pady=10)

        # Название задачи
        lbl_task = tk.Label(form_frame, text="Задача:")
        lbl_task.pack(side=tk.LEFT)
        self.entry_task = tk.Entry(form_frame)
        self.entry_task.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Категория
        lbl_category = tk.Label(form_frame, text="Категория:")
        lbl_category.pack(side=tk.LEFT, padx=(10, 0))  # Немного отступ справа
        categories = ["Работа", "Учеба", "Дом", "Здоровье", "Другое"]
        self.combo_category = ttk.Combobox(form_frame, values=categories, state="readonly")
        self.combo_category.pack(side=tk.LEFT)

        # Срок выполнения
        lbl_due_date = tk.Label(form_frame, text="Срок выполнения:")
        lbl_due_date.pack(side=tk.LEFT, padx=(10, 0))
        self.entry_due_date = tk.Entry(form_frame)
        self.entry_due_date.pack(side=tk.LEFT)

    def validate_and_format_date(self, date_str):
        pattern = r'^(\d{4})-(\d{2})-(\d{2})$'
        match = re.match(pattern, date_str)
        if match:
            year, month, day = map(int, match.groups())
            try:
                datetime(year, month, day)  # Проверьте, является ли данная дата действительной датой
                return f"{year}-{month:02d}-{day:02d}"  # Возвращаем дату в правильном формате
            except ValueError:
                pass
        return None

    def add_task(self):
        # Получаем введённые данные
        new_task = {
            "task": self.entry_task.get(),
            "category": self.combo_category.get(),
            "due_date": self.validate_and_format_date(self.entry_due_date.get().strip()),
            "completed": False
        }

        # Проверяем наличие необходимых данных
        if not all([new_task['task'], new_task['category'], new_task['due_date']]):
            return

        # Добавляем задачу в глобальную переменную задач
        self.tasks_data.append(new_task)

        # Добавляем задачу в таблицу
        completed_text = "Да" if new_task["completed"] else "Нет"
        self.treeview.insert("", "end",
                             values=(new_task['task'], new_task['category'], new_task['due_date'], completed_text))

        # Очищаем поля формы
        self.entry_task.delete(0, tk.END)
        self.entry_due_date.delete(0, tk.END)
        self.combo_category.set("")

        self.reorder()

    def edit_task(self):
        # Получаем выбранную задачу
        selection = self.treeview.selection()
        if not selection: return

        # Получаем ID выбранной задачи
        item_id = self.treeview.item(selection)['text']  # Индекс начинается с нуля

        # Сохраняем данные выбранной задачи
        current_task = None

        for i, child in enumerate(self.treeview.get_children()):

            if item_id == self.treeview.item(child)["text"]:
                current_task = self.tasks_data.pop(i)
                break

        # Заполняем поля формой существующими данными
        self.entry_task.delete(0, tk.END)
        self.entry_task.insert(0, current_task['task'])

        self.combo_category.set(current_task['category'])

        self.entry_due_date.delete(0, tk.END)
        self.entry_due_date.insert(0, current_task['due_date'])

        # Удаляем старую задачу из таблицы
        self.treeview.delete(selection)

    def delete_task(self):
        # Получаем выбранную задачу
        selection = self.treeview.selection()
        if not selection:
            return

        # Получаем ID выбранной задачи
        item_id = self.treeview.item(selection)['text']

        # Удаляем задачу из глобальной переменной
        for i, child in enumerate(self.treeview.get_children()):

            if item_id == self.treeview.item(child)["text"]:
                self.tasks_data.pop(i)
                break

        self.treeview.delete(selection)

        self.reorder()

    def reorder(self):

        for i, child_id in enumerate(self.treeview.get_children()):
            self.treeview.item(child_id, text=str(i + 1))

    def mark_as_completed(self):
        # Получаем выбранную задачу
        selection = self.treeview.selection()
        if not selection:
            return

        # Получаем индекс выбранной задачи
        item_id = int(self.treeview.item(selection)["text"]) - 1  # Индексация начинается с 0

        # Обновляем статус задачи в глобальном массиве
        self.tasks_data[item_id]["completed"] = True

        # Обновляем представление в таблице
        self.treeview.item(selection, values=(self.tasks_data[item_id]["task"],
                                              self.tasks_data[item_id]["category"],
                                              self.tasks_data[item_id]["due_date"], "Да"))

    def filter_table(self, search_term, selected_category):
        """
        Фильтрует таблицу задач в зависимости от условий поиска и выбранной категории.
        :param search_term: Текущий текст поиска
        :param selected_category: Категория выбора
        """
        treeview = self.winfo_children()[1].children['!treeview']
        items = treeview.get_children()

        # Сначала удаляем все существующие записи
        for item in items:
            treeview.delete(item)

        # Перезагружаем данные с учётом фильтра
        filtered_data = []
        for data in self.tasks_data:
            # Проверка совпадений по тексту задачи и категории
            match_task = search_term.lower() in data['task'].lower()
            match_category = (selected_category == "Все" or data['category'] == selected_category)

            if match_task and match_category:
                filtered_data.append(data)

        # Повторно загружаем данные в таблицу
        for idx, task in enumerate(filtered_data):
            completed_text = "Да" if task["completed"] else "Нет"
            treeview.insert("", "end", text=str(idx + 1),
                            values=(task['task'], task['category'], task['due_date'], completed_text))


# Класс страницы "Заметки"
class NotesPage(tk.Frame):

    def update(self):

        for child in self.treeview.get_children():
            self.treeview.delete(child)

        for i, note in enumerate(self.notes_data):
            self.treeview.insert("", "end", text=str(i + 1), values=(note['note'], note['category']))

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Верхняя панель для поиска и фильтра
        search_frame = tk.Frame(self)
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        # Поиск
        lbl_search = tk.Label(search_frame, text="Поиск:")
        lbl_search.pack(side=tk.LEFT)

        entry_search = tk.Entry(search_frame)
        entry_search.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry_search.bind("<KeyRelease>", lambda event: self.filter_notes(entry_search.get(), category_var.get()))

        # Фильтр по категориям
        categories = ["Все", "Работа", "Учеба", "Дом", "Здоровье", "Другое"]
        category_var = tk.StringVar(value="Все")
        combo_category = ttk.Combobox(search_frame, textvariable=category_var, state="readonly", values=categories)
        combo_category.pack(side=tk.RIGHT)
        combo_category.bind("<<ComboboxSelected>>",
                            lambda event: self.filter_notes(entry_search.get(), category_var.get()))

        # Основная таблица заметок
        notes_frame = tk.Frame(self)
        notes_frame.pack(fill=tk.BOTH, expand=True)

        # Дерево заметок
        treeview = ttk.Treeview(notes_frame, columns=("note", "category"))
        treeview.heading("#0", text="№")
        treeview.column("#0", width=50)
        treeview.heading("note", text="Заметка")
        treeview.column("note", width=200)
        treeview.heading("category", text="Категория")
        treeview.column("category", width=100)

        # Загрузка начальных данных

        self.notes_data = [
            {"note": "Планирую отдых", "category": "Дом"},
            {"note": "Переговоры с клиентом", "category": "Работа"}
        ]

        # Отображение данных
        for i, note in enumerate(self.notes_data):
            treeview.insert("", "end", text=str(i + 1), values=(note['note'], note['category']))

        treeview.pack(fill=tk.BOTH, expand=True)

        # Панель с кнопками
        buttons_frame = tk.Frame(self)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        # Кнопки
        btn_add = tk.Button(buttons_frame, text="Добавить", command=self.add_note)
        btn_edit = tk.Button(buttons_frame, text="Редактировать", command=self.edit_note)
        btn_delete = tk.Button(buttons_frame, text="Удалить", command=self.delete_note)

        # Упаковка кнопок
        btn_add.pack(side=tk.LEFT, padx=5)
        btn_edit.pack(side=tk.LEFT, padx=5)
        btn_delete.pack(side=tk.LEFT, padx=5)

        # Нижний блок для ввода заметки и выбора категории
        input_frame = tk.Frame(self)
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        # Ввод заметки
        lbl_note = tk.Label(input_frame, text="Заметка:")
        lbl_note.pack(side=tk.LEFT)
        entry_note = tk.Entry(input_frame)
        entry_note.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Выбор категории
        lbl_category = tk.Label(input_frame, text="Категория:")
        lbl_category.pack(side=tk.LEFT, padx=(10, 0))
        combo_input_category = ttk.Combobox(input_frame, values=["Работа", "Учеба", "Дом", "Здоровье", "Другое"],
                                            state="readonly")
        combo_input_category.pack(side=tk.LEFT)

        self.treeview = treeview
        self.entry_note = entry_note
        self.combo_input_category = combo_input_category

    def reorder(self):

        for i, child in enumerate(self.treeview.get_children()):
            self.treeview.item(child, text=str(i + 1))

    def add_note(self):

        treeview = self.treeview
        notes_data = self.notes_data
        entry_note = self.entry_note
        combo_input_category = self.combo_input_category

        # Получаем введённые данные
        new_note = {
            "note": entry_note.get().strip(),
            "category": combo_input_category.get().strip()
        }

        # Проверяем, что все поля заполнены
        if not new_note['note'] or not new_note['category']:
            return

        # Генерация уникального индекса
        index = len(notes_data) + 1

        # Добавляем заметку в глобальную переменную
        notes_data.append(new_note)

        # Добавляем заметку в таблицу
        treeview.insert("", "end", text=str(index), values=(new_note['note'], new_note['category']))

        # Очищаем поля формы
        entry_note.delete(0, tk.END)
        combo_input_category.set("")

        self.reorder()

    def edit_note(self):

        treeview = self.treeview
        notes_data = self.notes_data
        entry_note = self.entry_note
        combo_input_category = self.combo_input_category

        # Получаем выбранную заметку
        selection = treeview.selection()
        if not selection:
            return

        # Получаем индекс выбранной заметки
        item_id = int(treeview.item(selection)['text']) - 1  # Нумерация начинается с 1

        # Заполняем поля формы данными
        current_note = notes_data[item_id]
        entry_note.delete(0, tk.END)
        entry_note.insert(0, current_note['note'])
        combo_input_category.set(current_note['category'])

        # Удаляем старую заметку из таблицы
        treeview.delete(selection)

        # Удаляем из глобальных данных
        del notes_data[item_id]

        self.reorder()

    def delete_note(self):

        treeview = self.treeview
        notes_data = self.notes_data

        # Получаем выбранную заметку
        selection = treeview.selection()
        if not selection:
            return

        # Получаем индекс заметки
        item_id = int(treeview.item(selection)['text']) - 1

        if item_id >= len(notes_data):
            return

        # Удаляем заметку из таблицы
        treeview.delete(selection)

        # Удаляем из глобальных данных
        del self.notes_data[item_id]

        self.reorder()

    def filter_notes(self, search_term, selected_category):
        # Получаем ссылку на таблицу
        treeview = self.treeview
        notes_data = self.notes_data

        # Получаем все имеющиеся записи в таблице
        items = treeview.get_children()

        # Начинаем очистку таблицы
        for item in items:
            treeview.delete(item)

        # Фильтруем заметки согласно поиску и выбранной категории
        filtered_data = []
        for note in notes_data:
            # Проверка соответствия по строке поиска
            match_note = search_term.lower() in note['note'].lower()

            # Проверка соответствия по категории
            match_category = (selected_category == "Все" or note['category'] == selected_category)

            if match_note and match_category:
                filtered_data.append(note)

        # Вставляем отфильтрованные заметки назад в таблицу
        for idx, note in enumerate(filtered_data):
            treeview.insert("", "end", text=str(idx + 1), values=(note['note'], note['category']))


# Класс страницы "Статистика"
class StatsPage(tk.Frame):

    def update(self):

        for child in self.stats_frame.winfo_children():
            child.destroy()

        # Рисование диаграмм
        fig, axes = plt.subplots(2, 2, figsize=(10, 8))

        pages = self.controller.pages

        tasks_data = pages[TasksPage].tasks_data
        notes_data = pages[NotesPage].notes_data

        if len(tasks_data) != 0:

            # Первая диаграмма: Выполненные vs Невыполненные задачи
            tasks_status = {'Выполнено': sum(task['completed'] for task in tasks_data),
                            'Невыполнено': len(tasks_data) - sum(task['completed'] for task in tasks_data)}
            axes[0, 0].pie(list(tasks_status.values()), labels=list(tasks_status.keys()), autopct='%1.1f%%',
                           startangle=90)
            axes[0, 0].set_title("Выполнение задач")

            categories = {}
            for item in tasks_data:
                cat = item["category"]
                categories[cat] = categories.get(cat, 0) + 1

            # Вторая диаграмма: Распределение задач по категориям
            counts = [count for _, count in categories.items()]
            axes[0, 1].pie(counts, labels=categories, autopct='%1.1f%%', startangle=90)
            axes[0, 1].set_title("Категории задач")

            # Третья диаграмма: Распределение задач по срокам выполнения
            due_dates = sorted(set(task['due_date'] for task in tasks_data))
            dates_count = [sum(1 for task in tasks_data if task['due_date'] == date) for date in due_dates]
            axes[1, 0].pie(dates_count, labels=due_dates, autopct='%1.1f%%', startangle=90)
            axes[1, 0].set_title("Сроки выполнения")

        if len(notes_data) != 0:

            # Четвёртая диаграмма: Распределение заметок по категориям
            categories = {}
            for item in notes_data:
                cat = item["category"]
                categories[cat] = categories.get(cat, 0) + 1

            counts = [count for _, count in categories.items()]
            axes[1, 1].pie(counts, labels=categories, autopct='%1.1f%%', startangle=90)
            axes[1, 1].set_title("Категории заметок")

        # Добавляем фигуры на страницу
        canvas = FigureCanvasTkAgg(fig, master=self.stats_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        # Главное рабочее пространство
        self.stats_frame = tk.Frame(self)
        self.stats_frame.pack(fill=tk.BOTH, expand=True)

        self.controller = controller

        self.update()


# Запуск приложения
if __name__ == "__main__":
    app = App()
    app.mainloop()