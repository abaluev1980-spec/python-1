# Класс Queue реализует очередь по принципу FIFO (First In — First Out).
class Queue:
    """Очередь: первый добавленный элемент будет первым удалённым."""

    def __init__(self):
        """Создаёт пустую очередь на основе списка."""
        self.items = []  # Внутренний список для хранения элементов

    def enqueue(self, item):
        """Добавляет элемент в конец очереди."""
        self.items.append(item)
        print(f"Элемент '{item}' добавлен в очередь.")

    def dequeue(self):
        """Удаляет и возвращает первый элемент из очереди."""
        if len(self.items) == 0:
            print("Ошибка: очередь пуста. Невозможно удалить элемент.")
            return None
        # pop(0) удаляет и возвращает первый элемент списка
        return self.items.pop(0)

    def peek(self):
        """Возвращает первый элемент очереди без его удаления."""
        if len(self.items) == 0:
            print("Ошибка: очередь пуста. Нет элемента для просмотра.")
            return None
        return self.items[0]


# Класс Stack реализует стек по принципу LIFO (Last In — First Out).
class Stack:
    """Стек: последний добавленный элемент будет первым удалённым."""

    def __init__(self):
        """Создаёт пустой стек на основе списка."""
        self.items = []  # Внутренний список для хранения элементов

    def push(self, item):
        """Добавляет элемент на вершину стека (в конец списка)."""
        self.items.append(item)
        print(f"Элемент '{item}' добавлен в стек.")

    def pop(self):
        """Удаляет и возвращает элемент с вершины стека."""
        if len(self.items) == 0:
            print("Ошибка: стек пуст. Невозможно удалить элемент.")
            return None
        # pop() без аргументов удаляет и возвращает последний элемент
        return self.items.pop()

    def peek(self):
        """Возвращает верхний элемент стека без его удаления."""
        if len(self.items) == 0:
            print("Ошибка: стек пуст. Нет элемента для просмотра.")
            return None
        return self.items[-1]


def main():
    """Демонстрирует работу очереди и стека."""
    print("Демонстрация работы очереди (FIFO) и стека (LIFO)")

    # Работа с очередью
    print("\n--- Очередь (FIFO) ---")
    queue = Queue()

    queue.enqueue("первый")
    queue.enqueue("второй")
    queue.enqueue("третий")

    print("Первый элемент в очереди:", queue.peek())
    print("Удалён:", queue.dequeue())
    print("Удалён:", queue.dequeue())
    print("Текущий первый элемент:", queue.peek())
    print("Удалён:", queue.dequeue())
    # Попытка удалить из пустой очереди
    print("Попытка удалить из пустой очереди:", queue.dequeue())

    # Работа со стеком
    print("\n--- Стек (LIFO) ---")
    stack = Stack()

    stack.push("A")
    stack.push("B")
    stack.push("C")

    print("Верхний элемент стека:", stack.peek())
    print("Удалён:", stack.pop())
    print("Удалён:", stack.pop())
    print("Текущий верхний элемент:", stack.peek())
    print("Удалён:", stack.pop())
    # Попытка удалить из пустого стека
    print("Попытка удалить из пустого стека:", stack.pop())


# Точка входа в программу
if __name__ == "__main__":
    main()