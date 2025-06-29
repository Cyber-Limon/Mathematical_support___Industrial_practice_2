import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



DATA_FILE = "todo_data.json"



class ToDoJournalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("To-Do Journal")
        self.geometry("800x600")
        self.minsize(800, 600)



        # Верхняя панель с кнопками
        top_frame = ttk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10)

        ttk.Style().configure("Big.TButton", font=("Arial", 20, 'bold'))

        self.btn_tasks = ttk.Button(top_frame, text="Задачи", command=self.show_tasks, style='Big.TButton')
        self.btn_tasks.pack(side=tk.LEFT, fill='x', expand=True)

        self.btn_notes = ttk.Button(top_frame, text="Заметки", command=self.show_notes, style='Big.TButton')
        self.btn_notes.pack(side=tk.LEFT, fill='x', expand=True)

        self.btn_stats = ttk.Button(top_frame, text="Статистика", command=self.show_stats, style='Big.TButton')
        self.btn_stats.pack(side=tk.LEFT, fill='x', expand=True)



        # Контейнер для страниц
        self.container = ttk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)



        # Страницы
        self.pages = {}
        for PageClass in (TasksPage, NotesPage, StatsPage):
            page = PageClass(self.container)
            self.pages[PageClass] = page
            page.pack(fill=tk.BOTH, expand=True)
            page.pack_forget()

        self.tasks_page = self.pages[TasksPage]
        self.notes_page = self.pages[NotesPage]



        # Загрузка данных из файла (после создания страниц)
        self.load_data()

        # Установка обработчика закрытия окна
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Отображение стартовой страницы
        self.show_page(TasksPage)



    # Функции перехода между страницами
    def show_tasks(self):
        self.show_page(TasksPage)

    def show_notes(self):
        self.show_page(NotesPage)

    def show_stats(self):
        self.pages[StatsPage].update_stats()
        self.show_page(StatsPage)

    def show_page(self, page_class):
        for page in self.pages.values():
            page.pack_forget()
        self.pages[page_class].pack(fill=tk.BOTH, expand=True)



    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.tasks_page.all_tasks = data.get("tasks", [])
                    self.notes_page.all_notes = data.get("notes", [])
                    self.tasks_page.populate_tasks()
                    self.notes_page.populate_notes()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")

    def save_data(self):
        data = {
            "tasks": self.tasks_page.all_tasks,
            "notes": self.notes_page.all_notes
        }
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def on_close(self):
        self.save_data()
        self.destroy()



# Страница "Задач"
class TasksPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Страница задач", font=('Arial', 40, 'bold')).pack(pady=10)



        # Верхняя панель поиска и фильтрации
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        # Метка "Поиск:"
        search_label = ttk.Label(search_frame, text="Поиск:")
        search_label.pack(side=tk.LEFT)

        # Поле ввода для поиска
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.update_filter)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5, expand=True, fill='x')

        # Выпадающий список с категориями
        self.category_var = tk.StringVar()
        categories = ["Все", "Работа", "Учёба", "Дом", "Здоровье", "Другое"]
        category_combo = ttk.Combobox(search_frame, textvariable=self.category_var, values=categories, state="readonly")
        category_combo.pack(side=tk.LEFT)
        category_combo.set(categories[0])
        category_combo.bind("<<ComboboxSelected>>", self.update_filter)



        # Основное поле (фрейм) для таблицы
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Создаем таблицу с 4 колонками
        columns = ("task", "category", "deadline", "completed")
        self.task_tree = ttk.Treeview(main_frame, columns=columns, show="headings")

        # Заголовки колонок
        self.task_tree.heading("task", text="Задача")
        self.task_tree.heading("category", text="Категория")
        self.task_tree.heading("deadline", text="Срок выполнения")
        self.task_tree.heading("completed", text="Выполнено")

        # Устанавливаем ширину колонок (можно настроить)
        self.task_tree.column("task", width=200)
        self.task_tree.column("category", width=100)
        self.task_tree.column("deadline", width=120)
        self.task_tree.column("completed", width=80)

        # Размещение таблицы
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)



        # Нижняя панель с кнопками
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)

        # Кнопки
        buttons_frame = ttk.Frame(bottom_frame)
        buttons_frame.pack(fill=tk.X)

        btn_add = ttk.Button(buttons_frame, text="Добавить", command=self.add_task)
        btn_add.pack(side=tk.LEFT, padx=5)

        btn_edit = ttk.Button(buttons_frame, text="Редактировать", command=self.edit_task)
        btn_edit.pack(side=tk.LEFT, padx=5)

        btn_delete = ttk.Button(buttons_frame, text="Удалить", command=self.delete_task)
        btn_delete.pack(side=tk.LEFT, padx=5)

        btn_mark_done = ttk.Button(buttons_frame, text="Отметить выполненной", command=self.done_task)
        btn_mark_done.pack(side=tk.LEFT, padx=5)



        # Нижняя панель с полями ввода
        fields_frame = ttk.Frame(bottom_frame)
        fields_frame.pack(fill=tk.X, pady=5)

        # Задача:
        task_frame = ttk.Frame(fields_frame)
        task_frame.pack(fill=tk.X)
        task_label = ttk.Label(task_frame, text="Задача:")
        task_label.pack(side=tk.LEFT, padx=5)
        self.task_entry = ttk.Entry(task_frame)
        self.task_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Категория:
        category_frame = ttk.Frame(fields_frame)
        category_frame.pack(fill=tk.X, pady=5)
        category_label = ttk.Label(category_frame, text="Категория:")
        category_label.pack(side=tk.LEFT, padx=5)
        self.input_category_var = tk.StringVar()
        input_categories = ["Работа", "Учёба", "Дом", "Здоровье", "Другое"]
        category_input_combo = ttk.Combobox(category_frame, textvariable=self.input_category_var,
                                            values=input_categories, state="readonly")
        category_input_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        category_input_combo.set(input_categories[0])

        # Срок выполнения:
        deadline_frame = ttk.Frame(fields_frame)
        deadline_frame.pack(fill=tk.X)
        deadline_label = ttk.Label(deadline_frame, text="Срок выполнения:")
        deadline_label.pack(side=tk.LEFT, padx=5)
        self.deadline_entry = ttk.Entry(deadline_frame)
        self.deadline_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)



        # Пример данных для демонстрации фильтрации
        self.all_tasks = []

        self.populate_tasks()



    # Обновление таблицы
    def populate_tasks(self):
        # Очистить таблицу
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        # Добавить задачи, отфильтрованные по поиску и категории
        search_text = self.search_var.get().lower()
        selected_category = self.category_var.get()
        for task, category, deadline, completed in self.all_tasks:
            if search_text in task.lower() and (selected_category == "Все" or category == selected_category):
                self.task_tree.insert("", tk.END, values=(task, category, deadline, completed))

    def update_filter(self, *args):
        self.populate_tasks()



    # Добавить задачу
    def add_task(self):
        task = self.task_entry.get().strip()
        category = self.input_category_var.get()
        deadline = self.deadline_entry.get().strip()

        # Проверка заполненности полей
        if not task or not category or not deadline:
            messagebox.showwarning("Внимание", "Пожалуйста, заполните все поля.")
            return

        # Проверка формата даты
        try:
            datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Внимание", "Дата должна быть в формате ГГГГ-ММ-ДД.")
            return

        # Добавляем новую задачу в список
        self.all_tasks.append((task, category, deadline, "Нет"))

        # Обновляем таблицу с учетом текущих фильтров
        self.populate_tasks()

        # Очищаем поля ввода
        self.task_entry.delete(0, tk.END)
        self.deadline_entry.delete(0, tk.END)
        self.input_category_var.set("Работа")

    # Редактировать задачу
    def edit_task(self):
        selected_items = self.task_tree.selection()
        if not selected_items:
            messagebox.showwarning("Внимание", "Пожалуйста, выберете задачу.")
            return

        # Берем первую выбранную задачу (если несколько выбрано)
        item = selected_items[0]
        values = self.task_tree.item(item, "values")

        # Заполняем поля ввода данными выбранной задачи
        self.task_entry.delete(0, tk.END)
        self.task_entry.insert(0, values[0])

        self.input_category_var.set(values[1])

        self.deadline_entry.delete(0, tk.END)
        self.deadline_entry.insert(0, values[2])

        # Удаляем выбранную задачу из таблицы и из списка all_tasks
        self.task_tree.delete(item)

        task_name = values[0]
        for i, (task, category, deadline, completed) in enumerate(self.all_tasks):
            if task == task_name:
                del self.all_tasks[i]
                break

    # Отметить задачу выполненной
    def done_task(self):
        selected_items = self.task_tree.selection()
        if not selected_items:
            messagebox.showwarning("Внимание", "Пожалуйста, выберете задачу.")
            return

        for item in selected_items:
            values = list(self.task_tree.item(item, "values"))
            values[3] = "Да"
            self.task_tree.item(item, values=values)

            # Обновим данные в self.all_tasks, чтобы сохранить состояние
            task_name = values[0]
            for i, (task, category, deadline, completed) in enumerate(self.all_tasks):
                if task == task_name:
                    self.all_tasks[i] = (task, category, deadline, "Да")
                    break

    # Удалить задачу
    def delete_task(self):
        selected_items = self.task_tree.selection()
        if not selected_items:
            messagebox.showwarning("Внимание", "Пожалуйста, выберете задачу.")
            return

        for item in selected_items:
            values = self.task_tree.item(item, "values")
            task_name = values[0]

            # Удаляем из внутреннего списка
            self.all_tasks = [t for t in self.all_tasks if t[0] != task_name]

            # Удаляем из таблицы
            self.task_tree.delete(item)



# Страница "Заметок"
class NotesPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Страница заметок", font=('Arial', 40, 'bold')).pack(pady=10)

        # Верхняя панель поиска и фильтрации
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        # Метка "Поиск:"
        search_label = ttk.Label(search_frame, text="Поиск:")
        search_label.pack(side=tk.LEFT)

        # Поле ввода для поиска
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.update_filter)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, padx=5, expand=True, fill='x')

        # Выпадающий список с категориями, добавлена категория "Все"
        self.category_var = tk.StringVar()
        categories = ["Все", "Работа", "Учёба", "Дом", "Здоровье", "Другое"]
        category_combo = ttk.Combobox(search_frame, textvariable=self.category_var, values=categories, state="readonly")
        category_combo.pack(side=tk.LEFT)
        category_combo.set(categories[0])  # По умолчанию "Все"
        category_combo.bind("<<ComboboxSelected>>", self.update_filter)



        # Основное поле (фрейм) для таблицы
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Создаем таблицу с 2 колонками
        columns = ("note", "category")
        self.note_tree = ttk.Treeview(main_frame, columns=columns, show="headings")

        # Заголовки колонок
        self.note_tree.heading("note", text="Заметка")
        self.note_tree.heading("category", text="Категория")

        # Устанавливаем ширину колонок
        self.note_tree.column("note", width=300)
        self.note_tree.column("category", width=150)

        # Размещение таблицы
        self.note_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)



        # Нижняя панель с кнопками и полями ввода
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)

        # Кнопки (без "Отметить выполненной")
        buttons_frame = ttk.Frame(bottom_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))

        btn_add = ttk.Button(buttons_frame, text="Добавить", command=self.add_note)
        btn_add.pack(side=tk.LEFT, padx=5)

        btn_edit = ttk.Button(buttons_frame, text="Редактировать", command=self.edit_note)
        btn_edit.pack(side=tk.LEFT, padx=5)

        btn_delete = ttk.Button(buttons_frame, text="Удалить", command=self.delete_note)
        btn_delete.pack(side=tk.LEFT, padx=5)



        # Поля ввода под кнопками (каждое на своей строке)
        fields_frame = ttk.Frame(bottom_frame)
        fields_frame.pack(fill=tk.X)

        # Заметка:
        note_frame = ttk.Frame(fields_frame)
        note_frame.pack(fill=tk.X, pady=2)
        note_label = ttk.Label(note_frame, text="Заметка:")
        note_label.pack(side=tk.LEFT, padx=5)
        self.note_entry = ttk.Entry(note_frame)
        self.note_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Категория:
        category_frame = ttk.Frame(fields_frame)
        category_frame.pack(fill=tk.X, pady=2)
        category_label = ttk.Label(category_frame, text="Категория:")
        category_label.pack(side=tk.LEFT, padx=5)
        self.input_category_var = tk.StringVar()
        input_categories = ["Работа", "Учёба", "Дом", "Здоровье", "Другое"]
        category_input_combo = ttk.Combobox(category_frame, textvariable=self.input_category_var, values=input_categories, state="readonly")
        category_input_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        category_input_combo.set(input_categories[0])

        # Данные заметок (пример)
        self.all_notes = []

        self.populate_notes()



    def populate_notes(self):
        # Очистить таблицу
        for item in self.note_tree.get_children():
            self.note_tree.delete(item)
        # Добавить заметки, отфильтрованные по поиску и категории
        search_text = self.search_var.get().lower()
        selected_category = self.category_var.get()
        for note, category in self.all_notes:
            if search_text in note.lower() and (selected_category == "Все" or category == selected_category):
                self.note_tree.insert("", tk.END, values=(note, category))

    def update_filter(self, *args):
        self.populate_notes()



    def add_note(self):
        note = self.note_entry.get().strip()
        category = self.input_category_var.get()

        if not note or not category:
            messagebox.showwarning("Внимание", "Пожалуйста, заполните все поля.")
            return

        self.all_notes.append((note, category))
        self.populate_notes()

        self.note_entry.delete(0, tk.END)
        self.input_category_var.set("Работа")

    def edit_note(self):
        selected_items = self.note_tree.selection()
        if not selected_items:
            messagebox.showwarning("Внимание", "Пожалуйста, выберете задачу.")
            return

        item = selected_items[0]
        values = self.note_tree.item(item, "values")

        self.note_entry.delete(0, tk.END)
        self.note_entry.insert(0, values[0])

        self.input_category_var.set(values[1])

        self.note_tree.delete(item)

        note_text = values[0]
        for i, (note, category) in enumerate(self.all_notes):
            if note == note_text:
                del self.all_notes[i]
                break

    def delete_note(self):
        selected_items = self.note_tree.selection()
        if not selected_items:
            messagebox.showwarning("Внимание", "Пожалуйста, выберете задачу.")
            return

        for item in selected_items:
            values = self.note_tree.item(item, "values")
            note_text = values[0]

            self.all_notes = [n for n in self.all_notes if n[0] != note_text]

            self.note_tree.delete(item)



# Страница "Статистики"
class StatsPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Страница статистики", font=('Arial', 40, 'bold')).pack(pady=10)

        # Фрейм для графиков
        chart_frame = ttk.Frame(self)
        chart_frame.pack(fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.axes = [self.fig.add_subplot(221),
                     self.fig.add_subplot(222),
                     self.fig.add_subplot(223),
                     self.fig.add_subplot(224)]
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_stats(self):
        # Получаем данные из главного окна
        app = self.winfo_toplevel()
        all_tasks = app.tasks_page.all_tasks
        all_notes = app.notes_page.all_notes

        # 1. Категоризация задач
        cat_tasks = {}
        for task, category, deadline, completed in all_tasks:
            cat_tasks[category] = cat_tasks.get(category, 0) + 1
        self._draw_pie(self.axes[0], cat_tasks, "Категории задач")

        # 2. Категоризация заметок
        cat_notes = {}
        for note, category in all_notes:
            cat_notes[category] = cat_notes.get(category, 0) + 1
        self._draw_pie(self.axes[1], cat_notes, "Категории заметок")

        # 3. Выполненные / невыполненные задачи
        done = sum(1 for t in all_tasks if str(t[3]).lower() == "да")
        not_done = sum(1 for t in all_tasks if str(t[3]).lower() != "да")
        self._draw_pie(self.axes[2], {"ДА": done, "НЕТ": not_done},
                       "Выполненные/Невыполненные")

        # 4. Просроченные / непросроченные задачи (только из невыполненных)
        overdue = 0
        not_overdue = 0
        today = datetime.today()
        for task, category, deadline, completed in all_tasks:
            if str(completed).lower() != "да":
                try:
                    d = datetime.strptime(deadline, "%Y-%m-%d")
                    if d < today:
                        overdue += 1
                    else:
                        not_overdue += 1
                except Exception:
                    not_overdue += 1  # если дата некорректна, считаем непросроченной
        self._draw_pie(self.axes[3], {"ДА": overdue, "НЕТ": not_overdue},
                       "Просроченные/Непросроченные")

        self.fig.tight_layout()
        self.canvas.draw()

    def _draw_pie(self, ax, data_dict, title):
        ax.clear()
        labels = list(data_dict.keys())
        sizes = list(data_dict.values())
        if sum(sizes) == 0:
            ax.text(0.5, 0.5, "Нет данных", horizontalalignment='center', verticalalignment='center', fontsize=12)
            ax.axis('off')
            ax.set_title(title)
            return
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        ax.set_title(title)



if __name__ == "__main__":
    app = ToDoJournalApp()
    app.mainloop()
