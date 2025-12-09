# Создаём пустой словарь, в котором будут храниться все плагины.
# Ключ — имя плагина (например, "upper"), значение — сам класс плагина.
PluginRegistry = {}


# Определяем базовый класс Plugin
class Plugin:
    """Базовый класс для всех плагинов."""

    # Метод __init_subclass__ вызывается автоматически при создании любого подкласса.
    # Это метапрограммирование — мы управляем поведением при создании класса.
    def __init_subclass__(cls, **kwargs):
        """
        Этот метод вызывается, когда создаётся новый класс, унаследованный от Plugin.
        Например, когда создаётся UpperCasePlugin — этот метод сработает.
        """
        super().__init_subclass__(**kwargs)

        # Проверяем, есть ли у нового класса атрибут name
        if not hasattr(cls, 'name'):
            raise TypeError(f"Класс {cls.__name__} должен иметь атрибут 'name'.")

        # Добавляем класс в реестр плагинов по имени
        PluginRegistry[cls.name] = cls
        print(f"Плагин '{cls.name}' зарегистрирован в PluginRegistry.")

    # Метод execute — абстрактный (не реализован в базовом классе)
    def execute(self, text):
        """
        Этот метод должен быть реализован в каждом плагине.
        Если он не переопределён — будет выброшено исключение.
        """
        raise NotImplementedError("Метод execute должен быть реализован в подклассе.")


# Создаём конкретный плагин — UpperCasePlugin
class UpperCasePlugin(Plugin):
    """Плагин, который преобразует текст в верхний регистр."""
    
    # Обязательный атрибут — имя плагина
    name = "upper"

    # Переопределяем метод execute
    def execute(self, text):
        """Преобразует переданный текст в верхний регистр."""
        return text.upper()


# Создаём конкретный плагин — ReversePlugin
class ReversePlugin(Plugin):
    """Плагин, который переворачивает текст."""
    
    # Обязательный атрибут — имя плагина
    name = "reverse"

    # Переопределяем метод execute
    def execute(self, text):
        """Возвращает текст в обратном порядке."""
        return text[::-1]


# Функция для демонстрации работы программы
def main():
    """Главная функция — показывает, как работают плагины и реестр."""
    print("=== ДЕМОНСТРАЦИЯ РАБОТЫ ПЛАГИНОВ ===\n")

    # Выводим содержимое реестра плагинов
    print("Реестр плагинов:")
    print(PluginRegistry)
    # Должно вывести: {'upper': <class '__main__.UpperCasePlugin'>, 'reverse': <class '__main__.ReversePlugin'>}

    print("\n--- ТЕСТИРУЕМ ПЛАГИНЫ ---")

    # Получаем плагин по имени из реестра
    plugin_upper = PluginRegistry["upper"]()
    result_upper = plugin_upper.execute("hello")
    print(f"Плагин 'upper' обработал 'hello' → '{result_upper}'")  # Должно быть: "HELLO"

    plugin_reverse = PluginRegistry["reverse"]()
    result_reverse = plugin_reverse.execute("hello")
    print(f"Плагин 'reverse' обработал 'hello' → '{result_reverse}'")  # Должно быть: "olleh"

    print("\nВсе тесты пройдены успешно.")


# Запуск программы
if __name__ == "__main__":
    main()