import tkinter as tk
import json
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk, messagebox
from datetime import datetime



class App:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do Journal")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)

        # Создаем контейнер для страниц
        self.pages = {}
        self.create_pages()

        # Создаем кнопки для навигации
        self.create_nav_buttons()
        self.style = ttk.Style().configure("Big.TButton", font=('Arial', 14))

        # Показываем первую страницу
        self.show_page("tasks")

        # Загружаем данные при запуске
        self.load_data()

        # Сохраняем данные при закрытии окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)



    def create_pages(self):
        # Страница 1: "Задачи"
        self.pages["tasks"] = ttk.Frame(self.root)
        ttk.Label(self.pages["tasks"], text="Список задач", font=("Arial", 40, 'bold')).pack(pady=10)
        self.create_tasks_filters()
        self.create_tasks_table()
        self.create_tasks_controls()

        # Страница 2: "Заметки"
        self.pages["notes"] = ttk.Frame(self.root)
        ttk.Label(self.pages["notes"], text="Список заметок", font=("Arial", 40, 'bold')).pack(pady=10)
        self.create_notes_filters()
        self.create_notes_table()
        self.create_notes_controls()

        # Страница 3: "Статистика"
        self.pages["stats"] = ttk.Frame(self.root)
        ttk.Label(self.pages["stats"], text="Статистика", font=("Arial", 40, 'bold')).pack(pady=10)
        self.create_stats_upper_block()
        self.create_stats_lower_block()



    def create_nav_buttons(self):
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(nav_frame, text="Задачи", style="Big.TButton",
                   command=lambda: self.show_page("tasks")).pack(side="left", expand=True, fill="both")
        ttk.Button(nav_frame, text="Заметки", style="Big.TButton",
                   command=lambda: self.show_page("notes")).pack(side="left", expand=True, fill="both")
        ttk.Button(nav_frame, text="Статистика", style="Big.TButton",
                   command=lambda: self.show_page("stats")).pack(side="left", expand=True, fill="both")



    def show_page(self, page_name):
        for page in self.pages.values():
            page.pack_forget()

        self.pages[page_name].pack(fill="both", expand=True)

        if page_name == "stats":
            self.update_diagrams()
            self.update_completion_diagram()
            self.update_overdue_diagram()



    def create_tasks_filters(self):
        # Поле ввода
        search_frame = ttk.Frame(self.pages["tasks"])
        search_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(search_frame, text="Поиск:").pack(side="left", padx =5)

        self.tasks_search_var = tk.StringVar()
        self.tasks_search_entry = ttk.Entry(search_frame, textvariable=self.tasks_search_var)
        self.tasks_search_entry.pack(side="left", fill="x", padx=5, expand=True)
        self.tasks_search_var.trace_add("write", self.filter_tasks)


        # Категории
        filter_frame = ttk.Frame(self.pages["tasks"])
        filter_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(filter_frame, text="Категория:").pack(side="left", padx=5)

        self.categories = ["Работа", "Учёба", "Дом", "Здоровье", "Другое"]
        self.tasks_category_var = tk.StringVar(value="Все")
        self.tasks_category_menu = ttk.Combobox(filter_frame,
            textvariable=self.tasks_category_var, values=['Все'] + self.categories, state="readonly")
        self.tasks_category_menu.pack(side="left", fill="x", padx=5, expand=True)
        self.tasks_category_var.trace_add("write", self.filter_tasks)



    def create_notes_filters(self):
        # Поле ввода
        search_frame = ttk.Frame(self.pages["notes"])
        search_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(search_frame, text="Поиск:").pack(side="left", padx=5)

        self.notes_search_var = tk.StringVar()
        self.notes_search_entry = ttk.Entry(search_frame, textvariable=self.notes_search_var)
        self.notes_search_entry.pack(side="left", fill="x", padx=5, expand=True)
        self.notes_search_var.trace_add("write", self.filter_notes)


        # Категории
        filter_frame = ttk.Frame(self.pages["notes"])
        filter_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(filter_frame, text="Категория:").pack(side="left", padx=5)

        self.notes_category_var = tk.StringVar(value="Все")
        self.notes_category_menu = ttk.Combobox(
            filter_frame, textvariable=self.notes_category_var, values=['Все'] + self.categories, state="readonly")
        self.notes_category_menu.pack(side="left", fill="x", padx=5, expand=True)
        self.notes_category_var.trace_add("write", self.filter_notes)



    def create_tasks_table(self):
        # Создаем Treeview (таблицу) для отображения задач
        self.tasks_tree = ttk.Treeview(self.pages["tasks"],
                                       columns=("task", "category", "due_date", "done"), show="headings")

        # Настраиваем столбцы
        self.tasks_tree.heading("task", text="Задача")
        self.tasks_tree.heading("category", text="Категория")
        self.tasks_tree.heading("due_date", text="Срок выполнения")
        self.tasks_tree.heading("done", text="Выполнено")

        # Устанавливаем ширину столбцов
        self.tasks_tree.column("task", width=400)
        self.tasks_tree.column("category", width=100)
        self.tasks_tree.column("due_date", width=100)
        self.tasks_tree.column("done", width=100)

        # Упаковываем таблицу
        self.tasks_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Список задач
        self.all_tasks = []



    def create_notes_table(self):
        # Создаем Treeview (таблицу) для отображения задач
        self.notes_tree = ttk.Treeview(self.pages["notes"],
                                       columns=("note", "category"), show="headings")

        # Настраиваем столбцы
        self.notes_tree.heading("note", text="Заметка")
        self.notes_tree.heading("category", text="Категория")

        # Устанавливаем ширину столбцов
        self.notes_tree.column("note", width=650)
        self.notes_tree.column("category", width=50)

        # Упаковываем таблицу
        self.notes_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Список задач
        self.all_notes = []



    def create_tasks_controls(self):
        # Создаем панель управления задачами
        control_frame = ttk.Frame(self.pages["tasks"])
        control_frame.pack(fill="x", padx=5, side="bottom")


        # Кнопки управления
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill="x", pady=5)

        ttk.Button(btn_frame, command=self.add_task, text="Добавить").pack(side="left", padx=5)
        ttk.Button(btn_frame, command=self.edit_task, text="Редактировать").pack(side="left", padx=5)
        ttk.Button(btn_frame, command=self.delete_task, text="Удалить").pack(side="left", padx=5)
        ttk.Button(btn_frame, command=self.done_task, text="Отметить выполненной").pack(side="left", padx=5)


        # Поле "Задача"
        task_frame = ttk.Frame(control_frame)
        task_frame.pack(fill="x", pady=5)

        ttk.Label(task_frame, text="Задача:").pack(side="left", padx=5)

        self.task_entry = ttk.Entry(task_frame)
        self.task_entry.pack(side="left", fill="x", expand=True, padx=5)


        # Выпадающий список "Категория"
        task_category_frame = ttk.Frame(control_frame)
        task_category_frame.pack(fill="x", pady=5)

        ttk.Label(task_category_frame, text="Категория:").pack(side="left", padx=5)

        self.task_category_combo = ttk.Combobox(task_category_frame, values=self.categories, state="readonly")
        self.task_category_combo.pack(side="left", fill="x", expand=True, padx=5)
        self.task_category_combo.current(0)


        # Поле "Срок выполнения"
        date_frame = ttk.Frame(control_frame)
        date_frame.pack(fill="x", pady=5)

        ttk.Label(date_frame, text="Срок выполнения:").pack(side="left", padx=5)

        self.due_date_entry = ttk.Entry(date_frame)
        self.due_date_entry.pack(side="left", fill="x", expand=True, padx=5)



    def create_notes_controls(self):
        # Создаем панель управления задачами
        control_frame = ttk.Frame(self.pages["notes"])
        control_frame.pack(fill="x", padx=5, side="bottom")


        # Кнопки управления
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill="x", pady=5)

        ttk.Button(btn_frame, command=self.add_note, text="Добавить").pack(side="left", padx=5)
        ttk.Button(btn_frame, command=self.edit_note, text="Редактировать").pack(side="left", padx=5)
        ttk.Button(btn_frame, command=self.delete_note, text="Удалить").pack(side="left", padx=5)


        # Поле "Заметка"
        note_frame = ttk.Frame(control_frame)
        note_frame.pack(fill="x", pady=5)

        ttk.Label(note_frame, text="Заметка:").pack(side="left", padx=5)

        self.note_entry = ttk.Entry(note_frame)
        self.note_entry.pack(side="left", fill="x", expand=True, padx=5)


        # Выпадающий список "Категория"
        note_category_frame = ttk.Frame(control_frame)
        note_category_frame.pack(fill="x", pady=5)

        ttk.Label(note_category_frame, text="Категория:").pack(side="left", padx=5)

        self.note_category_combo = ttk.Combobox(note_category_frame, values=self.categories, state="readonly")
        self.note_category_combo.pack(side="left", fill="x", expand=True, padx=5)
        self.note_category_combo.current(0)



    def add_task(self):
        # Получаем данные из полей ввода
        task_text = self.task_entry.get().strip()
        category = self.task_category_combo.get()
        due_date = self.due_date_entry.get().strip()

        # Проверяем, что поле задачи не пустое
        if not task_text:
            messagebox.showwarning("Предупреждение", "Введите текст задачи!")
            return

        # Проверяем формат даты (допустим формат ГГГГ-ММ-ДД)
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Предупреждение",
                                       "Некорректный формат даты!\nИспользуйте ГГГГ-ММ-ДД")
                return

        # Создаем новую задачу
        new_task = (task_text, category, due_date, "Нет")

        # Добавляем задачу в основной список
        self.all_tasks.append(new_task)

        # Добавляем задачу в таблицу
        self.tasks_tree.insert("", "end", values=new_task)

        # Очищаем поля ввода
        self.task_entry.delete(0, tk.END)
        self.due_date_entry.delete(0, tk.END)

        # Показываем сообщение об успехе
        messagebox.showinfo("Успех", "Задача успешно добавлена!")



    def add_note(self):
        # Получаем данные из полей ввода
        note_text = self.note_entry.get().strip()
        category = self.note_category_combo.get()

        # Проверяем, что поле задачи не пустое
        if not note_text:
            messagebox.showwarning("Предупреждение", "Введите текст заметки!")
            return

        # Создаем новую заметку
        new_note = (note_text, category)

        # Добавляем заметку в основной список
        self.all_notes.append(new_note)

        # Добавляем заметку в таблицу
        self.notes_tree.insert("", "end", values=new_note)

        # Очищаем поля ввода
        self.note_entry.delete(0, tk.END)

        # Показываем сообщение об успехе
        messagebox.showinfo("Успех", "Заметка успешно добавлена!")



    def edit_task(self):
        # Получаем выделенный элемент в таблице задач
        selected_item = self.tasks_tree.selection()


        # Проверяем, выбрана ли задача
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите задачу для редактирования!")
            return


        # Получаем текущие значения задачи
        item_values = self.tasks_tree.item(selected_item)['values']


        # Заполняем поля формы данными выбранной задачи
        self.task_entry.delete(0, tk.END)
        self.task_entry.insert(0, item_values[0])

        self.task_category_combo.set(item_values[1])

        self.due_date_entry.delete(0, tk.END)
        self.due_date_entry.insert(0, item_values[2])


        # Удаляем старую задачу
        self.tasks_tree.delete(selected_item)
        for i, task in enumerate(self.all_tasks):
            if task[0] == item_values[0] and task[1] == item_values[1] and task[2] == item_values[2]:
                del self.all_tasks[i]
                break


        # Фокус в поле задачи для удобного редактирования
        self.task_entry.focus_set()



    def edit_note(self):
        # Получаем выделенный элемент в таблице заметок
        selected_item = self.notes_tree.selection()


        # Проверяем, выбрана ли заметка
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите заметку для редактирования!")
            return


        # Получаем текущие значения заметки
        item_values = self.notes_tree.item(selected_item)['values']


        # Заполняем поля формы данными выбранной заметки
        self.note_entry.delete(0, tk.END)
        self.note_entry.insert(0, item_values[0])

        self.note_category_combo.set(item_values[1])


        # Удаляем старую заметку
        self.notes_tree.delete(selected_item)
        for i, note in enumerate(self.all_notes):
            if note[0] == item_values[0] and note[1] == item_values[1]:
                del self.all_notes[i]
                break


        # Фокус в поле заметки для удобного редактирования
        self.note_entry.focus_set()



    def delete_task(self):
        # Получаем выделенный элемент в таблице задач
        selected_items = self.tasks_tree.selection()

        # Проверяем, выбрана ли задача
        if not selected_items:
            messagebox.showwarning("Предупреждение", "Выберите задачу для удаления!")
            return

        # Получаем данные выбранной задачи
        item_values = self.tasks_tree.item(selected_items[0])['values']

        # Подтверждение удаления
        if not messagebox.askyesno("Подтверждение",
                                   f"Удалить задачу \n{item_values[0]}?"):
            return

        # Удаляем из таблицы
        self.tasks_tree.delete(selected_items[0])

        # Удаляем из основного списка
        for i, task in enumerate(self.all_tasks):
            if task[0] == item_values[0] and task[1] == item_values[1] and task[2] == item_values[2]:
                del self.all_tasks[i]
                break

        messagebox.showinfo("Успех", "Задача успешно удалена!")



    def delete_note(self):
        # Получаем выделенный элемент в таблице заметок
        selected_items = self.notes_tree.selection()

        # Проверяем, выбрана ли заметка
        if not selected_items:
            messagebox.showwarning("Предупреждение", "Выберите заметку для удаления!")
            return

        # Получаем данные выбранной заметки
        item_values = self.notes_tree.item(selected_items[0])['values']

        # Подтверждение удаления
        if not messagebox.askyesno("Подтверждение",
                                   f"Удалить заметку \n{item_values[0]}?"):
            return

        # Удаляем из таблицы
        self.notes_tree.delete(selected_items[0])

        # Удаляем из основного списка
        for i, note in enumerate(self.all_notes):
            if note[0] == item_values[0] and note[1] == item_values[1]:
                del self.all_notes[i]
                break

        messagebox.showinfo("Успех", "Заметка успешно удалена!")



    def done_task(self):
        # Получаем выделенный элемент в таблице задач
        selected_item = self.tasks_tree.selection()

        # Проверяем, выбрана ли задача
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите задачу для отметки!")
            return

        # Получаем текущие значения задачи
        item_values = self.tasks_tree.item(selected_item)['values']

        # Если задача уже выполнена
        if item_values[3] == "Да":
            messagebox.showinfo("Информация", "Эта задача уже выполнена!")
            return

        # Подтверждение обновления
        if not messagebox.askyesno("Подтверждение",
                                   f"Отметить задачу \n{item_values[0]} выполненной?"):
            return

        # Обновляем статус задачи
        self.tasks_tree.item(selected_item, values=(item_values[0],  item_values[1], item_values[2], "Да" ))

        # Обновляем данные в all_tasks
        for i, task in enumerate(self.all_tasks):
            if task[0] == item_values[0] and task[1] == item_values[1] and task[2] == item_values[2]:
                self.all_tasks[i] = (task[0], task[1], task[2], "Да")
                break

        messagebox.showinfo("Успех", "Задача отмечена как выполненная!")



    def filter_tasks(self, *args):
        #Фильтрация задач по поиску и категории
        search_term = self.tasks_search_var.get().lower()
        selected_category = self.tasks_category_var.get()

        # Очищаем таблицу
        for item in self.tasks_tree.get_children():
            self.tasks_tree.delete(item)

        # Фильтруем задачи
        for task in self.all_tasks:
            task_text = task[0].lower()
            task_category = task[1]

            # Проверяем соответствие поиску и категории
            search_ok = search_term in task_text
            category_ok = (selected_category == "Все") or (selected_category == task_category)

            if search_ok and category_ok:
                self.tasks_tree.insert("", "end", values=task)



    def filter_notes(self, *args):
        # Фильтрация заметок по поиску и категории
        search_term = self.notes_search_var.get().lower()
        selected_category = self.notes_category_var.get()

        # Очищаем таблицу
        for item in self.notes_tree.get_children():
            self.notes_tree.delete(item)

        # Фильтруем заметки
        for note in self.all_notes:
            note_text = note[0].lower()
            note_category = note[1]

            # Проверяем соответствие поиску и категории
            search_ok = search_term in note_text
            category_ok = (selected_category == "Все") or (selected_category == note_category)

            if search_ok and category_ok:
                self.notes_tree.insert("", "end", values=note)



    def create_stats_upper_block(self):
        upper_frame = ttk.Frame(self.pages["stats"])
        upper_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Создаем контейнер для колонок
        columns_frame = ttk.Frame(upper_frame)
        columns_frame.pack(fill="both", expand=True)

        # Левая часть - диаграмма задач (оставляем как было)
        self.tasks_diagram_container = ttk.Frame(columns_frame)
        self.tasks_diagram_container.pack(side="left", fill="both", expand=True, padx=5)

        # Правая часть - добавляем контейнер для диаграммы заметок
        self.notes_diagram_container = ttk.Frame(columns_frame)
        self.notes_diagram_container.pack(side="left", fill="both", expand=True, padx=5)



    def create_stats_lower_block(self):
        lower_frame = ttk.Frame(self.pages["stats"])
        lower_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Создаем контейнер для колонок
        columns_frame = ttk.Frame(lower_frame)
        columns_frame.pack(fill="both", expand=True)

        # Левая часть
        self.completion_diagram_container = ttk.Frame(columns_frame)
        self.completion_diagram_container.pack(side="left", fill="both", expand=True, padx=5)

        # Правая часть
        self.overdue_diagram_container = ttk.Frame(columns_frame)
        self.overdue_diagram_container.pack(side="left", fill="both", expand=True, padx=5)



    def update_diagram(self, container, data_list, title):
        # Очищаем контейнер
        for widget in container.winfo_children():
            widget.destroy()


        # Собираем данные
        categories = {}
        for item in data_list:
            cat = item[1]
            categories[cat] = categories.get(cat, 0) + 1


        # Создаем диаграмму
        fig = Figure(figsize=(1, 1), dpi=80)
        ax = fig.add_subplot(111)

        if categories:
            ax.pie(categories.values(), labels=categories.keys(),
                   autopct=lambda p: f'{int(round(p * sum(categories.values())/100))}',
                   startangle=90, textprops={'fontsize': 14})
            ax.set_title(title, fontsize=16)
        else:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', fontsize=10)


        # Встраиваем в контейнер
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)



    def update_diagrams(self):
        # Диаграмма для задач (оставляем ваш код)
        self.update_diagram(self.tasks_diagram_container, self.all_tasks, "Распределение задач")

        # Новая диаграмма для заметок
        self.update_diagram(self.notes_diagram_container, self.all_notes, "Распределение заметок")



    def update_completion_diagram(self):
        # Очищаем контейнер
        for widget in self.completion_diagram_container.winfo_children():
            widget.destroy()


        # Выполненные и невыполненные задачи
        completed = 0
        not_completed = 0

        for task in self.all_tasks:
            if task[3] == "Да":
                completed += 1
            else:
                not_completed += 1


        # Создаем данные для диаграммы
        sizes = [completed, not_completed]
        labels = ['Выполнено', 'Не выполнено']
        colors = ['#4CAF50', '#F44336']


        # Создаем диаграмму
        fig = Figure(figsize=(1, 1), dpi=80)
        ax = fig.add_subplot(111)

        if sum(sizes) > 0:
            ax.pie(sizes, labels=labels, autopct=lambda p: f'{int(round(p * sum(sizes) / 100))}',
                   colors=colors, startangle=90, textprops={'fontsize': 14})
            ax.set_title("Статус выполнения задач", fontsize=16)
        else:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', fontsize=10)

        # Встраиваем в контейнер
        canvas = FigureCanvasTkAgg(fig, master=self.completion_diagram_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)



    def update_overdue_diagram(self):
        # Очищаем контейнер
        for widget in self.overdue_diagram_container.winfo_children():
            widget.destroy()


        # Просроченные и непросроченные задачи
        today = datetime.now().date()
        expired = 0
        not_expired = 0

        for task in self.all_tasks:
            due_date = datetime.strptime(task[2], "%Y-%m-%d").date() if task[2] else None
            if not due_date:
                continue

            if task[3] == "Нет":
                if due_date >= today:
                    not_expired += 1
                else:
                    expired += 1

        # Создаем данные для диаграммы
        sizes = [expired, not_expired]
        labels = ['Просрочено', 'Не просрочено']
        colors = ['#F44336', '#4CAF50']


        # Создаем диаграмму
        fig = Figure(figsize=(1, 1), dpi=80)
        ax = fig.add_subplot(111)

        if sum(sizes) > 0:
            ax.pie(sizes, labels=labels, autopct=lambda p: f'{int(round(p * sum(sizes)/100))}',
                   colors=colors, startangle=90, textprops = {'fontsize': 14})
            ax.set_title("Статус задач по срокам", fontsize=16)
        else:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', fontsize=10)


        # Встраиваем в контейнер
        canvas = FigureCanvasTkAgg(fig, master=self.overdue_diagram_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)



    def save_data(self):
        data = {
            "tasks": self.all_tasks,
            "notes": self.all_notes
        }
        with open("todo_data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)



    def load_data(self):
        try:
            with open("todo_data.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                self.all_tasks = data.get("tasks", [])
                self.all_notes = data.get("notes", [])

                # Обновляем таблицы после загрузки
                self.update_tasks_table()
                self.update_notes_table()
        except FileNotFoundError:
            # Если файла нет, оставляем пустые списки
            self.all_tasks = []
            self.all_notes = []



    def update_tasks_table(self):
        for item in self.tasks_tree.get_children():
            self.tasks_tree.delete(item)
        for task in self.all_tasks:
            self.tasks_tree.insert("", "end", values=task)



    def update_notes_table(self):
        for item in self.notes_tree.get_children():
            self.notes_tree.delete(item)
        for note in self.all_notes:
            self.notes_tree.insert("", "end", values=note)



    def on_close(self):
        self.save_data()
        self.root.destroy()



if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
