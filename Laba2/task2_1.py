# Импортируем модуль json — он нужен, чтобы сохранять и загружать данные в формате JSON (удобный текстовый формат для хранения структурированных данных).
import json

# Импортируем модуль os — он позволяет работать с файловой системой (например, проверять, существует ли файл).
import os

# Указываем имя файла, в котором будут храниться задачи. Это константа — значение не меняется в программе.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "tasks.json")

# Определяем класс Task — это "шаблон" для одной задачи. У каждой задачи есть описание, категория и статус (выполнена или нет).
class Task:
    # Конструктор класса — вызывается при создании новой задачи. Принимает описание, категорию и (опционально) статус выполнения.
    def __init__(self, description, category, completed=False):
        self.description = description  # Сохраняем описание задачи (например, "Помыть посуду")
        self.category = category        # Сохраняем категорию (например, "дом" или "работа")
        self.completed = completed      # Сохраняем, выполнена задача или нет (по умолчанию — False)

    # Метод, который превращает объект задачи в словарь (нужен для сохранения в JSON).
    def to_dict(self):
        return {
            "description": self.description,  # Описание задачи
            "category": self.category,        # Категория задачи
            "completed": self.completed       # Статус выполнения
        }

    # Метод класса, который создаёт объект Task из словаря (нужен при загрузке из JSON).
    @classmethod
    def from_dict(cls, data):
        # Создаём новую задачу, используя данные из словаря
        return cls(
            description=data["description"],  # Берём описание из данных
            category=data["category"],        # Берём категорию
            completed=data["completed"]       # Берём статус выполнения
        )

    # Метод, который определяет, как задача будет выглядеть при печати (в консоли).
    def __str__(self):
        # Если задача выполнена, покажем [x], иначе [ ]
        status = "[x]" if self.completed else "[ ]"
        # Возвращаем строку вида: "[x] Помыть посуду #дом"
        return f"{status} {self.description} #{self.category}"


# Определяем класс TaskTracker — это "менеджер задач", который управляет всеми задачами.
class TaskTracker:
    # Конструктор — вызывается при создании объекта трекера.
    def __init__(self):
        self.tasks = []        # Список для хранения всех задач
        self.load_tasks()      # Сразу пытаемся загрузить задачи из файла

    # Метод для добавления новой задачи
    def add_task(self, description, category):
        task = Task(description, category)  # Создаём объект задачи
        self.tasks.append(task)             # Добавляем её в список задач
        print(f"Задача добавлена: {task}")  # Выводим подтверждение

    # Метод для отметки задачи как выполненной по её номеру (индексу)
    def mark_completed(self, index):
        # Проверяем, что номер задачи корректный (не меньше 0 и меньше длины списка)
        if 0 <= index < len(self.tasks):
            self.tasks[index].completed = True  # Меняем статус на "выполнено"
            print(f"Задача отмечена как выполненная: {self.tasks[index]}")
        else:
            print("Неверный номер задачи.")  # Если номер неправильный

    # Метод для вывода всех задач
    def list_tasks(self):
        if not self.tasks:  # Если список задач пуст
            print(" Список задач пуст.")
        else:
            print("\n ВСЕ ЗАДАЧИ:")
            # Проходим по всем задачам, нумеруя их с 1 (а не с 0)
            for i, task in enumerate(self.tasks, 1):
                print(f"{i}. {task}")  # Выводим номер и строковое представление задачи

    # Метод для поиска задач по категории
    def search_by_category(self, category):
        # Создаём новый список только из задач с нужной категорией
        found = [task for task in self.tasks if task.category == category]
        if found:  # Если нашли хотя бы одну задачу
            print(f"\n Задачи в категории '#{category}':")
            for i, task in enumerate(found, 1):
                print(f"{i}. {task}")
        else:
            print(f"Нет задач в категории '#{category}'.")

    # Метод для сохранения задач в файл
    def save_tasks(self):
        # Открываем файл для записи (режим 'w'), используя кодировку UTF-8 (чтобы поддерживать русский язык)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            # Преобразуем все задачи в словари и записываем их в файл в формате JSON (с отступами для читаемости)
            json.dump([task.to_dict() for task in self.tasks], f, ensure_ascii=False, indent=2)
        print(f"Данные сохранены в {DATA_FILE}")

    # Метод для загрузки задач из файла при запуске программы
    def load_tasks(self):
        # Проверяем, существует ли файл с задачами
        if os.path.exists(DATA_FILE):
            try:
                # Открываем файл для чтения
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)  # Загружаем данные из JSON в Python-список словарей
                    # Преобразуем каждый словарь обратно в объект Task
                    self.tasks = [Task.from_dict(item) for item in data]
                print(f"Загружено {len(self.tasks)} задач из {DATA_FILE}")
            except (json.JSONDecodeError, KeyError):
                # Если файл повреждён или содержит неверные данные
                print("Ошибка загрузки файла. Создан новый список задач.")
                self.tasks = []  # Начинаем с пустого списка
        else:
            # Если файла ещё нет — это нормально, просто начинаем с нуля
            print("Файл с задачами не найден. Создан новый список.")

    # Основной метод — запускает интерактивное меню
    def run(self):
        print("TaskTracker!")
        # Бесконечный цикл — программа работает, пока пользователь не выберет "выйти"
        while True:
            print("\n--- МЕНЮ ---")
            print("1. Добавить задачу")
            print("2. Отметить задачу как выполненную")
            print("3. Показать все задачи")
            print("4. Поиск по категории")
            print("5. Сохранить и выйти")

            # Спрашиваем у пользователя выбор, убираем лишние пробелы
            choice = input("Выберите действие (1-5): ").strip()

            # Действие 1: добавить задачу
            if choice == "1":
                desc = input("Введите описание задачи: ").strip()
                cat = input("Введите категорию (например, work, pstu): ").strip()
                # Проверяем, что пользователь ввёл и описание, и категорию
                if desc and cat:
                    self.add_task(desc, cat)
                else:
                    print("Описание и категория обязательны!")

            # Действие 2: отметить задачу как выполненную
            elif choice == "2":
                self.list_tasks()  # Сначала показываем список задач
                try:
                    # Пользователь вводит номер задачи (мы вычитаем 1, потому что в списке отсчёт с 0)
                    idx = int(input("Введите номер задачи для отметки: ")) - 1
                    self.mark_completed(idx)
                except ValueError:
                    # Если пользователь ввёл не число
                    print("Введите число!")

            # Действие 3: показать все задачи
            elif choice == "3":
                self.list_tasks()

            # Действие 4: поиск по категории
            elif choice == "4":
                cat = input("Введите категорию для поиска: ").strip()
                if cat:
                    self.search_by_category(cat)
                else:
                    print("Укажите категорию!")

            # Действие 5: сохранить и выйти
            elif choice == "5":
                self.save_tasks()  # Сохраняем задачи в файл
                print("До свидания!")
                break  # Прерываем цикл — программа завершается

            # Если пользователь ввёл что-то кроме 1-5
            else:
                print("Неверный выбор. Попробуйте снова.")


# Эта проверка означает: запускать программу только если файл запущен напрямую (а не импортирован как модуль)
if __name__ == "__main__":
    tracker = TaskTracker()  # Создаём объект трекера задач
    tracker.run()           # Запускаем основное меню