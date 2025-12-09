# Импортируем необходимые модули
import json
import os
from datetime import datetime

# Получаем путь к папке, где находится этот файл, чтобы сохранить данные рядом
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "budget.json")


class Transaction:
    """Класс для представления одной финансовой операции (доход или расход)."""
    
    def __init__(self, description, amount, transaction_type, category, date_str=None):
        """
        Создаёт новую операцию.
        date_str — дата в формате строки (например, "2025-12-09").
        Если не указана — берётся текущая дата.
        """
        self.description = description
        self.amount = amount
        self.transaction_type = transaction_type  # "доход" или "расход"
        self.category = category
        # Если дата не передана — используем сегодняшнюю
        if date_str is None:
            self.date = datetime.now().strftime("%Y-%m-%d")  # Пример: "2025-12-09"
        else:
            self.date = date_str

    def to_dict(self):
        """Преобразует операцию в словарь для сохранения в JSON."""
        return {
            "description": self.description,
            "amount": self.amount,
            "transaction_type": self.transaction_type,
            "category": self.category,
            "date": self.date
        }

    @classmethod
    def from_dict(cls, data):
        """Создаёт операцию из словаря (при загрузке из файла)."""
        return cls(
            description=data["description"],
            amount=data["amount"],
            transaction_type=data["transaction_type"],
            category=data["category"],
            date_str=data["date"]
        )

    def __str__(self):
        """Как операция будет выглядеть при выводе в консоль."""
        sign = "+" if self.transaction_type == "доход" else "-"
        return f"[{sign}] {self.date} | {self.description}: {sign}{self.amount:.2f} руб. (#{self.category})"


class BudgetTracker:
    """Основной класс для управления бюджетом."""
    
    def __init__(self):
        self.transactions = []  # Список всех операций
        self.limits = {}        # Лимиты по категориям: {"продукты": 5000}
        self.load_data()        # Загружаем данные при старте

    def add_transaction(self, description, amount, transaction_type, category, date_str=None):
        """Добавляет новую операцию в список."""
        transaction = Transaction(description, amount, transaction_type, category, date_str)
        self.transactions.append(transaction)
        print(f"Операция добавлена: {transaction}")

    def calculate_balance(self):
        """Вычисляет текущий баланс (сумма всех доходов минус расходы)."""
        balance = 0.0
        for t in self.transactions:
            if t.transaction_type == "доход":
                balance += t.amount
            else:
                balance -= t.amount
        return balance

    def show_balance(self):
        """Показывает текущий баланс."""
        balance = self.calculate_balance()
        print(f"\nТекущий баланс: {balance:.2f} руб.")

    def set_limit(self, category, limit_amount):
        """Устанавливает месячный лимит на категорию расходов."""
        if limit_amount <= 0:
            print("Ошибка: лимит должен быть больше нуля!")
            return
        self.limits[category] = limit_amount
        print(f"Установлен лимит для категории '{category}': {limit_amount:.2f} руб.")

    def check_limits(self):
        """Проверяет, не превышены ли лимиты по категориям за всё время."""
        # Группируем расходы по категориям
        expenses_by_category = {}
        for t in self.transactions:
            if t.transaction_type == "расход":
                cat = t.category
                expenses_by_category[cat] = expenses_by_category.get(cat, 0.0) + t.amount

        if not expenses_by_category:
            print("\nНет записанных расходов.")
            return

        print("\nПроверка лимитов по категориям:")
        for category, spent in expenses_by_category.items():
            if category in self.limits:
                limit = self.limits[category]
                if spent > limit:
                    print(f"⚠ Превышен лимит в '{category}': потрачено {spent:.2f}, лимит {limit:.2f}")
                else:
                    print(f"✓ В '{category}' всё в норме: потрачено {spent:.2f}, лимит {limit:.2f}")
            else:
                print(f"ℹ Для категории '{category}' лимит не задан.")

    def generate_monthly_report(self):
        """Генерирует отчёт по месяцам: доходы, расходы, баланс за каждый месяц."""
        # Группируем операции по месяцам (ключ: "2025-12")
        monthly_data = {}
        for t in self.transactions:
            # Извлекаем год и месяц из даты: "2025-12-09" → "2025-12"
            month_key = t.date[:7]  # Первые 7 символов — это "ГГГГ-ММ"
            if month_key not in monthly_data:
                monthly_data[month_key] = {"доходы": 0.0, "расходы": 0.0}
            
            if t.transaction_type == "доход":
                monthly_data[month_key]["доходы"] += t.amount
            else:
                monthly_data[month_key]["расходы"] += t.amount

        if not monthly_data:
            print("\nНет данных для формирования отчёта.")
            return

        print("\n=== ОТЧЁТ ПО МЕСЯЦАМ ===")
        # Сортируем месяцы по возрастанию (от старых к новым)
        for month in sorted(monthly_data.keys()):
            data = monthly_data[month]
            income = data["доходы"]
            expense = data["расходы"]
            balance = income - expense
            print(f"\nМесяц: {month}")
            print(f"  Доходы: {income:.2f} руб.")
            print(f"  Расходы: {expense:.2f} руб.")
            print(f"  Баланс: {balance:.2f} руб.")

    def save_data(self):
        """Сохраняет все данные в файл budget.json."""
        data = {
            "transactions": [t.to_dict() for t in self.transactions],
            "limits": self.limits
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Данные сохранены в {DATA_FILE}")

    def load_data(self):
        """Загружает данные из файла при запуске."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.transactions = [Transaction.from_dict(item) for item in data.get("transactions", [])]
                self.limits = data.get("limits", {})
                print(f"Загружено {len(self.transactions)} операций и {len(self.limits)} лимитов.")
            except (json.JSONDecodeError, KeyError, ValueError):
                print("Ошибка при загрузке файла. Начинаем с пустых данных.")
                self.transactions = []
                self.limits = {}
        else:
            print("Файл данных не найден. Начинаем с пустых данных.")

    def run(self):
        """Запускает главное меню программы."""
        print("Добро пожаловать в Трекер Бюджета!")

        while True:
            print("\n--- МЕНЮ ---")
            print("1. Добавить операцию (доход/расход)")
            print("2. Показать текущий баланс")
            print("3. Установить лимит на категорию")
            print("4. Проверить лимиты")
            print("5. Отчёт по месяцам")
            print("6. Сохранить и выйти")

            choice = input("Выберите действие (1–6): ").strip()

            if choice == "1":
                desc = input("Описание операции: ").strip()
                if not desc:
                    print("Описание не может быть пустым!")
                    continue

                try:
                    amount = float(input("Сумма (положительное число): "))
                    if amount <= 0:
                        print("Сумма должна быть больше нуля!")
                        continue
                except ValueError:
                    print("Некорректная сумма!")
                    continue

                type_choice = input("Тип: 1 — доход, 2 — расход: ").strip()
                if type_choice == "1":
                    t_type = "доход"
                elif type_choice == "2":
                    t_type = "расход"
                else:
                    print("Неверный выбор типа!")
                    continue

                cat = input("Категория (например, еда, зарплата): ").strip()
                if not cat:
                    print("Категория обязательна!")
                    continue

                # Дата устанавливается автоматически (сегодня)
                self.add_transaction(desc, amount, t_type, cat)

            elif choice == "2":
                self.show_balance()

            elif choice == "3":
                cat = input("Категория для лимита: ").strip()
                if not cat:
                    print("Категория обязательна!")
                    continue
                try:
                    limit = float(input("Месячный лимит (руб.): "))
                    self.set_limit(cat, limit)
                except ValueError:
                    print("Некорректное число!")

            elif choice == "4":
                self.check_limits()

            elif choice == "5":
                self.generate_monthly_report()

            elif choice == "6":
                self.save_data()
                print("До свидания!")
                break

            else:
                print("Неверный выбор. Введите число от 1 до 6.")


# Точка входа в программу
if __name__ == "__main__":
    app = BudgetTracker()
    app.run()