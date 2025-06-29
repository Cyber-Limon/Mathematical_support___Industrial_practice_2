import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime



# === Список задач и заметок ===
tasks = []
notes = []



# === Функции сохранения и загрузки ===
DATA_FILE = "todo_data.json"

def save_data():
    data = {
        "tasks": tasks,
        "notes": notes
    }
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            tasks.extend(data.get("tasks", []))
            notes.extend(data.get("notes", []))
    except FileNotFoundError:
        # Файл не найден — начнём с пустых списков
        pass



# === Функция переключения страниц ===
prev = None
def show_frame(frame):
    global prev
    if prev:
        prev.pack_forget()

    frame.pack(fill="both", expand=True)
    prev = frame

def show_tasks():
    show_frame(frame_tasks)

def show_notes():
    show_frame(frame_notes)

def show_stats():
    show_frame(frame_stats)
    update_charts()
    update_task_status_charts()



# === Функция поиска задач ===
def task_search(event=None):
    query = search_entry.get().lower()
    selected_category = category_var.get()

    # Очистка таблицы
    for row in task_tree.get_children():
        task_tree.delete(row)

    # Фильтрация
    for idx, task in enumerate(tasks):
        task_name = task[0].lower()
        task_category = task[1]

        if query not in task_name:
            continue
        if selected_category != "Все" and task_category != selected_category:
            continue

        task_tree.insert("", tk.END, values=task, tags=(idx,))



# === Функция добавления задач ===
def add_task():
    # Получение данных из полей
    name = entry_task_name.get().strip()
    category = combo_category.get().strip()
    due_date = entry_due_date.get().strip()

    # Проверка заполненности полей
    if not name or not category or not due_date:
        messagebox.showwarning("Предупреждение", "Заполните все поля!")
        return

    # Проверка формата даты
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        tk.messagebox.showwarning("Предупреждение", "Дата должна быть в формате ГГГГ-ММ-ДД")
        return

    new_task = (name, category, due_date, "Нет")
    tasks.append(new_task)

    # Очистка полей ввода
    entry_task_name.delete(0, tk.END)
    entry_due_date.delete(0, tk.END)
    combo_category.current(0)

    # Обновление таблицы
    task_search()



# === Функция редактирования задач ===
def edit_task():
    selected_item = task_tree.selection()
    if not selected_item:
        tk.messagebox.showwarning("Предупреждение", "Выберите задачу для редактирования!")
        return

    # Получаем индекс задачи и преобразуем в int
    item = selected_item[0]
    index = int(task_tree.item(item, "tags")[0])

    # Получаем данные задачи
    name, category, due_date, done = tasks[index]

    # Заполняем поля формы
    entry_task_name.delete(0, tk.END)
    entry_task_name.insert(0, name)

    combo_category.set(category)

    entry_due_date.delete(0, tk.END)
    entry_due_date.insert(0, due_date)

    # Удаляем задачу из списка (чтобы потом добавить изменённую)
    del tasks[index]

    # Обновляем таблицу (удалённая задача исчезнет)
    task_search()



# === Функция удаления задач ===
def delete_task():
    selected_item = task_tree.selection()
    if not selected_item:
        tk.messagebox.showwarning("Предупреждение", "Выберите задачу для удаления!")
        return

    # Получаем индекс задачи и преобразуем в int
    item = selected_item[0]
    index = int(task_tree.item(item, "tags")[0])

    # Удаляем задачу по индексу
    del tasks[index]

    # Обновляем таблицу
    task_search()



# === Функция выполнения задач ===
def done_task():
    selected_item = task_tree.selection()
    if not selected_item:
        messagebox.showwarning("Предупреждение", "Выберите задачу для отметки!")
        return

    # Получаем индекс из тега
    item = selected_item[0]
    index = int(task_tree.item(item, "tags")[0])

    # Обновляем запись в sample_tasks (заменяем кортеж)
    task_list = list(tasks[index])
    task_list[3] = "Да"
    tasks[index] = tuple(task_list)

    # Обновляем таблицу
    task_search()



# === Функция поиска заметок ===
def note_search(event=None):
    query = note_search_entry.get().lower()
    selected_category = note_category_var.get()

    # Очистка таблицы
    for row in note_tree.get_children():
        note_tree.delete(row)

    # Фильтрация и отображение
    for idx, note in enumerate(notes):
        note_text = note[0].lower()
        note_category = note[1]

        if query not in note_text:
            continue
        if selected_category != "Все" and note_category != selected_category:
            continue

        note_tree.insert("", tk.END, values=note, tags=(idx,))



# === Функция добавления заметки ===
def add_note():
    text = entry_note_text.get().strip()
    category = note_combo_category.get().strip()

    if not text or not category:
        messagebox.showwarning("Предупреждение", "Заполните все поля!")
        return

    new_note = (text, category)
    notes.append(new_note)

    # Очистка полей
    entry_note_text.delete(0, tk.END)
    note_combo_category.current(0)

    # Обновление таблицы
    note_search()



# === Функция редактирования заметки ===
def edit_note():
    selected_item = note_tree.selection()
    if not selected_item:
        messagebox.showwarning("Предупреждение", "Выберите заметку для редактирования!")
        return

    item = selected_item[0]
    index = int(note_tree.item(item, "tags")[0])

    # Получаем данные
    text, category = notes[index]

    # Заполняем форму
    entry_note_text.delete(0, tk.END)
    entry_note_text.insert(0, text)

    note_combo_category.set(category)

    # Удаляем старую заметку
    del notes[index]

    # Обновляем таблицу
    note_search()



# === Функция удаления заметки ===
def delete_note():
    selected_item = note_tree.selection()
    if not selected_item:
        messagebox.showwarning("Предупреждение", "Выберите заметку для удаления!")
        return

    item = selected_item[0]
    index = int(note_tree.item(item, "tags")[0])

    del notes[index]
    note_search()



# === Закрытие программы ===
def on_close():
    save_data()
    plt.close('all')
    root.destroy()



import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def update_charts():
    # Очистка старых графиков
    for widget in stats_top_left.winfo_children():
        widget.destroy()
    for widget in stats_top_right.winfo_children():
        widget.destroy()

    # === Подсчёт категорий задач ===
    task_categories = {}
    for task in tasks:
        category = task[1]
        task_categories[category] = task_categories.get(category, 0) + 1

    # === Подсчёт категорий заметок ===
    note_categories = {}
    for note in notes:
        category = note[1]
        note_categories[category] = note_categories.get(category, 0) + 1

    # === Диаграмма задач (левая верхняя часть) ===
    fig1, ax1 = plt.subplots(figsize=(1, 1))
    if task_categories:
        ax1.pie(task_categories.values(), labels=task_categories.keys(), autopct="%1.1f%%")
        ax1.set_title("Категории задач")
    else:
        ax1.text(0.5, 0.5, "Нет данных", ha="center", va="center")
        ax1.axis("off")

    canvas1 = FigureCanvasTkAgg(fig1, master=stats_top_left)
    canvas1.draw()
    canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # === Диаграмма заметок (правая верхняя часть) ===
    fig2, ax2 = plt.subplots(figsize=(1, 1))
    if note_categories:
        ax2.pie(note_categories.values(), labels=note_categories.keys(), autopct="%1.1f%%")
        ax2.set_title("Категории заметок")
    else:
        ax2.text(0.5, 0.5, "Нет данных", ha="center", va="center")
        ax2.axis("off")

    canvas2 = FigureCanvasTkAgg(fig2, master=stats_top_right)
    canvas2.draw()
    canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)



def update_task_status_charts():
    # Очистка старых графиков
    for widget in stats_bottom_left.winfo_children():
        widget.destroy()
    for widget in stats_bottom_right.winfo_children():
        widget.destroy()

    # Подсчёт выполненных / невыполненных
    done_count = sum(1 for task in tasks if task[3] == "Да")
    not_done_count = len(tasks) - done_count

    # Подсчёт просроченных среди невыполненных
    overdue_count = 0
    not_overdue_count = 0
    today = datetime.today().date()

    for task in tasks:
        if task[3] == "Нет":
            due_date = datetime.strptime(task[2], "%Y-%m-%d").date()
            if due_date < today:
                overdue_count += 1
            else:
                not_overdue_count += 1

    # === Диаграмма выполнения задач ===
    fig1, ax1 = plt.subplots(figsize=(1, 1))
    labels1 = []
    values1 = []

    if done_count > 0:
        labels1.append("Выполнено")
        values1.append(done_count)
    if not_done_count > 0:
        labels1.append("Не выполнено")
        values1.append(not_done_count)

    if labels1:
        ax1.pie(values1, labels=labels1, autopct="%1.1f%%", startangle=90, colors=['#4CAF50', '#F44336'])
        ax1.set_title("Выполнение задач")
    else:
        ax1.text(0.5, 0.5, "Нет данных", ha="center", va="center")
        ax1.axis("off")

    canvas1 = FigureCanvasTkAgg(fig1, master=stats_bottom_left)
    canvas1.draw()
    canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # === Диаграмма просроченности задач ===
    fig2, ax2 = plt.subplots(figsize=(1, 1))
    labels2 = []
    values2 = []

    if overdue_count > 0:
        labels2.append("Просрочено")
        values2.append(overdue_count)
    if not_overdue_count > 0:
        labels2.append("Не просрочено")
        values2.append(not_overdue_count)

    if labels2:
        ax2.pie(values2, labels=labels2, autopct="%1.1f%%", startangle=90, colors=['#4CAF50', '#F44336'])
        ax2.set_title("Просроченность задач")
    else:
        ax2.text(0.5, 0.5, "Нет невыполненных задач", ha="center", va="center")
        ax2.axis("off")

    canvas2 = FigureCanvasTkAgg(fig2, master=stats_bottom_right)
    canvas2.draw()
    canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)



# === Загрузка данных ===
load_data()



# === Создаем главное окно ===
root = tk.Tk()
root.title("To-Do Journal")
root.geometry("800x600")
root.minsize(800, 600)



# === Работа с верхними кнопками ===
top_frame = tk.Frame()
top_frame.pack(side="top", fill="x", padx=10, pady=5)

style = ttk.Style().configure("Big.TButton", font=("Arial", 14), padding=10)

btn_tasks = ttk.Button(top_frame, text="Задачи", command=show_tasks, style="Big.TButton")
btn_notes = ttk.Button(top_frame, text="Заметки", command=show_notes, style="Big.TButton")
btn_stats = ttk.Button(top_frame, text="Статистика", command=show_stats, style="Big.TButton")

btn_tasks.pack(side="left", expand=True, fill="both")
btn_notes.pack(side="left", expand=True, fill="both")
btn_stats.pack(side="left", expand=True, fill="both")



# === Основная область для контента ===
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

# Создаем фреймы для каждой страницы
frame_tasks = tk.Frame(main_frame)
frame_notes = tk.Frame(main_frame)
frame_stats = tk.Frame(main_frame)



# === Страница "Задачи" ===
tk.Label(frame_tasks, text="Страница задач", font=("Arial", 40, 'bold')).pack(pady=10)


# = Поле поиска =
search_frame = tk.Frame(frame_tasks)
search_frame.pack(pady=5, padx=5, fill="x")

tk.Label(search_frame, text="Поиск:").pack(side="left", padx=5)

search_entry = tk.Entry(search_frame)
search_entry.pack(side="left", fill="x", expand=True, padx=5)

# Привязка события ввода
search_entry.bind("<KeyRelease>", task_search)


# = Выпадающий список категорий =
categories = ["Все", "Работа", "Учёба", "Дом", "Здоровье", "Другое"]

category_var = tk.StringVar()
category_combobox = ttk.Combobox(search_frame, textvariable=category_var, values=categories, state="readonly")
category_combobox.pack(side="left", padx=5)
category_combobox.current(0)

# Привязка события выбора категории
category_combobox.bind("<<ComboboxSelected>>", task_search)


# = Таблица задач =
task_tree = ttk.Treeview(frame_tasks, columns=("task", "category", "due_date", "done"), show="headings")

# Настраиваем столбцы
task_tree.heading("task", text="Задача")
task_tree.heading("category", text="Категория")
task_tree.heading("due_date", text="Срок выполнения")
task_tree.heading("done", text="Выполнено")

# Устанавливаем ширину столбцов
task_tree.column("task", width=400)
task_tree.column("category", width=100)
task_tree.column("due_date", width=100)
task_tree.column("done", width=100)

# Упаковываем таблицу
task_tree.pack(fill="both", expand=True, padx=10, pady=10)


# = Кнопки =
button_frame = tk.Frame(frame_tasks)
button_frame.pack(padx=5, pady=5, fill="x")

btn_add = ttk.Button(button_frame, text="Добавить", command=add_task)
btn_edit = ttk.Button(button_frame, text="Редактировать", command=edit_task)
btn_delete = ttk.Button(button_frame, text="Удалить", command=delete_task)
btn_mark_done = ttk.Button(button_frame, text="Отметить выполненной", command=done_task)

btn_add.pack(side="left", padx=5)
btn_edit.pack(side="left", padx=5)
btn_delete.pack(side="left", padx=5)
btn_mark_done.pack(side="left", padx=5)


# = Форма добавления/редактирования задачи =
form_frame = tk.Frame(frame_tasks)
form_frame.pack(padx=5, fill="x")

# Поле "Задача"
task_row = tk.Frame(form_frame)
task_row.pack(fill="x", pady=5)

tk.Label(task_row, text="Задача:").pack(side="left", padx=5)

entry_task_name = tk.Entry(task_row, width=40)
entry_task_name.pack(side="left", padx=5, fill='x', expand=True)

# Поле "Категория"
category_row = tk.Frame(form_frame)
category_row.pack(fill="x", pady=5)

tk.Label(category_row, text="Категория:").pack(side="left", padx=5)

combo_category = ttk.Combobox(category_row, values=categories[1:], state="readonly")
combo_category.pack(side="left", padx=5, fill='x', expand=True)
combo_category.current(0)

# Поле "Срок выполнения"
due_date_row = tk.Frame(form_frame)
due_date_row.pack(fill="x", pady=5)

tk.Label(due_date_row, text="Срок выполнения:").pack(side="left", padx=5)

entry_due_date = tk.Entry(due_date_row)
entry_due_date.pack(side="left", padx=5, fill='x', expand=True)



# === Страница "Заметки" ===
tk.Label(frame_notes, text="Страница заметок", font=("Arial", 40, 'bold')).pack(pady=10)

# = Поиск =
note_top_frame = tk.Frame(frame_notes)
note_top_frame.pack(pady=5, padx=5, fill="x")

tk.Label(note_top_frame, text="Поиск:").pack(side="left", padx=5)

note_search_entry = tk.Entry(note_top_frame)
note_search_entry.pack(side="left", fill="x", expand=True, padx=5)
note_search_entry.bind("<KeyRelease>", note_search)

# = Категоризация =
categories = ["Все", "Работа", "Учёба", "Дом", "Здоровье", "Другое"]

note_category_var = tk.StringVar()
note_category_combo = ttk.Combobox(note_top_frame, textvariable=note_category_var, values=categories, state="readonly")
note_category_combo.pack(side="left", padx=5)
note_category_combo.current(0)
note_category_combo.bind("<<ComboboxSelected>>", note_search)


# = Таблица заметок =
note_tree = ttk.Treeview(frame_notes, columns=("note", "category"), show="headings")

note_tree.heading("note", text="Заметка")
note_tree.heading("category", text="Категория")

note_tree.column("note", width=600)
note_tree.column("category", width=100)

note_tree.pack(fill="both", expand=True, padx=10, pady=10)


# = Кнопки =
note_button_frame = tk.Frame(frame_notes)
note_button_frame.pack(padx=5, pady=5, fill="x")

btn_add_note = ttk.Button(note_button_frame, text="Добавить", command=add_note)
btn_edit_note = ttk.Button(note_button_frame, text="Редактировать", command=edit_note)
btn_delete_note = ttk.Button(note_button_frame, text="Удалить", command=delete_note)

btn_add_note.pack(side="left", padx=5)
btn_edit_note.pack(side="left", padx=5)
btn_delete_note.pack(side="left", padx=5)


# = Форма добавления/редактирования заметки =
note_form_frame = tk.Frame(frame_notes)
note_form_frame.pack(padx=5, fill="x")

# Поле "Заметка"
note_row = tk.Frame(note_form_frame)
note_row.pack(fill="x", pady=5)
tk.Label(note_row, text="Заметка:").pack(side="left", padx=5)
entry_note_text = tk.Entry(note_row, width=40)
entry_note_text.pack(side="left", fill="x", expand=True, padx=5)

# Поле "Категория"
note_category_row = tk.Frame(note_form_frame)
note_category_row.pack(fill="x", pady=5)
tk.Label(note_category_row, text="Категория:").pack(side="left", padx=5)

note_combo_category = ttk.Combobox(note_category_row, values=categories[1:], state="readonly")
note_combo_category.pack(side="left", fill="x", expand=True, padx=5)
note_combo_category.current(0)


# = Первое отображение =
note_search()



# === Страница "Статистика" ===
tk.Label(frame_stats, text="Страница статистики", font=("Arial", 40, 'bold')).pack(pady=10)


# = Верхний блок =
frame_stats_top = tk.Frame(frame_stats)
frame_stats_top.pack(fill="both", expand=True, side="top", padx=5, pady=5)


# = Левая часть =
stats_top_left = tk.Frame(frame_stats_top)
stats_top_left.pack(side="left", fill="both", expand=True, padx=5)


# = Правая часть =
stats_top_right = tk.Frame(frame_stats_top,)
stats_top_right.pack(side="right", fill="both", expand=True, padx=5)


# = Нижний блок =
frame_stats_bottom = tk.Frame(frame_stats)
frame_stats_bottom.pack(fill="both", expand=True, side="bottom", padx=5, pady=5)


# = Левая часть =
stats_bottom_left = tk.Frame(frame_stats_bottom)
stats_bottom_left.pack(side="left", fill="both", expand=True, padx=5)


# = Правая часть =
stats_bottom_right = tk.Frame(frame_stats_bottom,)
stats_bottom_right.pack(side="right", fill="both", expand=True, padx=5)



# === Первое отображение данных ===
task_search()
note_search()
show_frame(frame_tasks)



# === Выполнение приложения === #
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
