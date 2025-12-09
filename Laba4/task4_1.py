import numpy as np
import time
import memory_profiler
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Шаг 1: Создание наборов данных разных размеров
def generate_test_datasets():
    """
    Генерирует четыре набора данных разного размера:
    small: 10^4 элементов
    medium: 10^5 элементов
    large: 10^6 элементов
    xlarge: 10^7 элементов
    Все данные — случайные числа от 0 до 100.
    """
    return {
        'small': np.random.randint(0, 100, size=10**4),
        'medium': np.random.randint(0, 100, size=10**5),
        'large': np.random.randint(0, 100, size=10**6),
        'xlarge': np.random.randint(0, 100, size=10**7)
    }


# Шаг 2: Реализация операций для чистого Python
def py_square(data):
    """Возведение в квадрат каждого элемента списка с помощью цикла."""
    return [x ** 2 for x in data]

def py_sum(data):
    """Вычисление суммы всех элементов списка."""
    return sum(data)

def py_max(data):
    """Поиск максимального элемента в списке."""
    return max(data)


# Шаг 3: Реализация операций для NumPy
def np_square(data):
    """Возведение в квадрат каждого элемента массива NumPy."""
    return np.square(data)

def np_sum(data):
    """Вычисление суммы всех элементов массива NumPy."""
    return np.sum(data)

def np_max(data):
    """Поиск максимального элемента в массиве NumPy."""
    return np.max(data)


# Шаг 4: Функция измерения времени и памяти
def benchmark_operations():
    """
    Запускает тесты для всех наборов данных и всех операций.
    Измеряет время выполнения и потребление памяти.
    Возвращает словарь с результатами.
    """
    datasets = generate_test_datasets()
    results = {}

    # Определяем операции и их названия
    operations = [
        ('square', py_square, np_square),
        ('sum', py_sum, np_sum),
        ('max', py_max, np_max)
    ]

    for name, py_func, np_func in operations:
        print(f"\n--- Тестирование операции '{name}' ---")
        results[name] = {}

        for size_name, data in datasets.items():
            print(f"  Размер данных: {size_name}")

            # Преобразуем NumPy-массив в список для чистого Python (если нужно)
            if isinstance(data, np.ndarray):
                data_list = data.tolist()
            else:
                data_list = data

            # Измеряем время и память для чистого Python
            start_time = time.time()
            # Используем memory_profiler для замера памяти
            mem_usage_py = memory_profiler.memory_usage(
                (py_func, (data_list,)), 
                interval=0.1, 
                timeout=None
            )
            end_time = time.time()
            time_py = end_time - start_time
            max_mem_py = max(mem_usage_py) if mem_usage_py else 0

            # Измеряем время и память для NumPy
            start_time = time.time()
            mem_usage_np = memory_profiler.memory_usage(
                (np_func, (data,)), 
                interval=0.1, 
                timeout=None
            )
            end_time = time.time()
            time_np = end_time - start_time
            max_mem_np = max(mem_usage_np) if mem_usage_np else 0

            # Сохраняем результаты
            results[name][size_name] = {
                'time_python': time_py,
                'time_numpy': time_np,
                'memory_python': max_mem_py,
                'memory_numpy': max_mem_np
            }

            print(f"    Python: время={time_py:.4f}с, память={max_mem_py:.2f} MiB")
            print(f"    NumPy:  время={time_np:.4f}с, память={max_mem_np:.2f} MiB")

    return results


# Шаг 5: Построение графиков
def plot_results(results):
    """
    Строит графики:
    1. Время выполнения в зависимости от размера данных.
    2. Потребление памяти в зависимости от размера данных.
    3. Тепловая карта ускорения NumPy над Python.
    """
    sizes = ['small', 'medium', 'large', 'xlarge']
    size_labels = [r'$10^4$', r'$10^5$', r'$10^6$', r'$10^7$']

    # Подготовка данных для графиков
    time_data = {'Python': [], 'NumPy': []}
    memory_data = {'Python': [], 'NumPy': []}
    speedup_data = []

    for op_name in results.keys():
        times_py = []
        times_np = []
        mems_py = []
        mems_np = []
        speedups = []

        for size in sizes:
            res = results[op_name][size]
            times_py.append(res['time_python'])
            times_np.append(res['time_numpy'])
            mems_py.append(res['memory_python'])
            mems_np.append(res['memory_numpy'])
            # Ускорение = время Python / время NumPy
            speedup = res['time_python'] / res['time_numpy'] if res['time_numpy'] > 0 else 0
            speedups.append(speedup)

        time_data['Python'].append(times_py)
        time_data['NumPy'].append(times_np)
        memory_data['Python'].append(mems_py)
        memory_data['NumPy'].append(mems_np)
        speedup_data.append(speedups)

    # График времени выполнения
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    for i, op_name in enumerate(results.keys()):
        plt.plot(size_labels, time_data['Python'][i], marker='o', label=f'{op_name} (Python)')
        plt.plot(size_labels, time_data['NumPy'][i], marker='s', label=f'{op_name} (NumPy)')
    plt.title('Время выполнения операций')
    plt.xlabel('Размер данных')
    plt.ylabel('Время (секунды)')
    plt.legend()
    plt.grid(True)

    # График потребления памяти
    plt.subplot(1, 2, 2)
    for i, op_name in enumerate(results.keys()):
        plt.plot(size_labels, memory_data['Python'][i], marker='o', label=f'{op_name} (Python)')
        plt.plot(size_labels, memory_data['NumPy'][i], marker='s', label=f'{op_name} (NumPy)')
    plt.title('Потребление памяти')
    plt.xlabel('Размер данных')
    plt.ylabel('Память (MiB)')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

    # Тепловая карта ускорения NumPy над Python
    speedup_matrix = np.array(speedup_data)
    operation_names = list(results.keys())
    df_speedup = pd.DataFrame(speedup_matrix, index=operation_names, columns=size_labels)

    plt.figure(figsize=(8, 6))
    sns.heatmap(df_speedup, annot=True, cmap='YlGnBu', fmt='.1f')
    plt.title('Тепловая карта ускорения NumPy над чистым Python')
    plt.xlabel('Размер данных')
    plt.ylabel('Операция')
    plt.show()


# Главная функция
def main():
    """Запускает весь тест и строит графики."""
    print("Начинаем сравнительный анализ производительности NumPy и чистого Python...")

    # Запускаем тесты
    results = benchmark_operations()

    # Строим графики
    plot_results(results)

    print("\nАнализ завершён. Графики построены.")


# Запуск программы
if __name__ == "__main__":
    main()