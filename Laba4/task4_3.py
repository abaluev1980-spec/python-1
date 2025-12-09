import numpy as np
import pandas as pd
import polars as pl
import time
import memory_profiler
import matplotlib.pyplot as plt
import seaborn as sns

# Шаг 1: Создание большого датасета (1 миллион записей)
def generate_large_dataset(n_rows=1000000):
    """
    Генерирует датафрейм с 1 миллионом записей.
    Столбцы:
    - timestamp: временные метки от 2024-01-01
    - category: случайные буквы A, B, C, D
    - value1, value2: случайные числа (нормальное и экспоненциальное распределение)
    """
    # Временные метки
    timestamps = pd.date_range('2024-01-01', periods=n_rows, freq='s')
    
    # Категории
    categories = np.random.choice(['A', 'B', 'C', 'D'], size=n_rows)
    
    # Числовые значения
    values1 = np.random.normal(0, 1, n_rows)  # Нормальное распределение
    values2 = np.random.exponential(1, n_rows)  # Экспоненциальное распределение
    
    # Создаём датафрейм pandas
    df = pd.DataFrame({
        'timestamp': timestamps,
        'category': categories,
        'value1': values1,
        'value2': values2
    })
    
    return df


# Шаг 2: Анализ с помощью pandas
def pandas_analysis(df):
    """
    Выполняет анализ с помощью pandas:
    - Фильтрация: оставляем только строки, где value1 > 0
    - Группировка: по category, вычисляем mean и count
    - JOIN: объединяем с таблицей категорий
    - Сглаживание: rolling mean по value1 за 10 минут
    """
    # Фильтрация
    filtered_df = df[df['value1'] > 0]
    
    # Группировка
    grouped = filtered_df.groupby('category').agg({
        'value1': ['mean', 'count']
    }).reset_index()
    grouped.columns = ['category', 'mean_value1', 'count']
    
    # Создаём таблицу категорий для JOIN
    category_info = pd.DataFrame({
        'category': ['A', 'B', 'C', 'D'],
        'description': ['Alpha', 'Beta', 'Charlie', 'Delta']
    })
    
    # JOIN
    result = grouped.merge(category_info, on='category', how='left')
    
    # Сглаживание (rolling average) — по временному столбцу
    df_sorted = df.sort_values('timestamp').reset_index(drop=True)
    df_sorted['rolling_mean'] = df_sorted['value1'].rolling(window=600).mean()  # 600 секунд = 10 минут
    
    return result


# Шаг 3: Анализ с помощью pandas + PyArrow
def pandas_pyarrow_analysis(df):
    """
    То же самое, что и pandas_analysis, но с использованием PyArrow типов.
    Это может ускорить работу и снизить потребление памяти.
    """
    # Преобразуем в PyArrow типы
    df_pa = df.copy()
    for col in df_pa.select_dtypes(include=['object']).columns:
        df_pa[col] = df_pa[col].astype('string[pyarrow]')
    for col in df_pa.select_dtypes(include=['int64', 'float64']).columns:
        df_pa[col] = df_pa[col].astype('int64[pyarrow]' if df_pa[col].dtype == 'int64' else 'float64[pyarrow]')
    
    # Фильтрация
    filtered_df = df_pa[df_pa['value1'] > 0]
    
    # Группировка
    grouped = filtered_df.groupby('category').agg({
        'value1': ['mean', 'count']
    }).reset_index()
    grouped.columns = ['category', 'mean_value1', 'count']
    
    # Таблица категорий
    category_info = pd.DataFrame({
        'category': ['A', 'B', 'C', 'D'],
        'description': ['Alpha', 'Beta', 'Charlie', 'Delta']
    })
    category_info['category'] = category_info['category'].astype('string[pyarrow]')
    
    # JOIN
    result = grouped.merge(category_info, on='category', how='left')
    
    # Сглаживание
    df_sorted = df_pa.sort_values('timestamp').reset_index(drop=True)
    df_sorted['rolling_mean'] = df_sorted['value1'].rolling(window=600).mean()
    
    return result


# Шаг 4: Анализ с помощью Polars
def polars_analysis(df):
    """
    Выполняет те же операции, но с помощью Polars.
    Polars работает быстрее и эффективнее по памяти.
    """
    # Конвертируем pandas DataFrame в Polars DataFrame
    pl_df = pl.from_pandas(df)
    
    # Фильтрация
    filtered_pl = pl_df.filter(pl.col('value1') > 0)
    
    # Группировка
    grouped = filtered_pl.group_by('category').agg([
        pl.col('value1').mean().alias('mean_value1'),
        pl.col('value1').count().alias('count')
    ]).sort('category')
    
    # Таблица категорий
    category_info = pl.DataFrame({
        'category': ['A', 'B', 'C', 'D'],
        'description': ['Alpha', 'Beta', 'Charlie', 'Delta']
    })
    
    # JOIN
    result = grouped.join(category_info, on='category', how='left')
    
    # Сглаживание (rolling mean) — Polars не имеет встроенной rolling по времени, поэтому используем индекс
    # Сортируем по timestamp
    sorted_df = pl_df.sort('timestamp')
    # Добавляем rolling mean по value1 с окном 600 элементов
    sorted_df = sorted_df.with_columns(
        pl.col('value1').rolling_mean(window_size=600).alias('rolling_mean')
    )
    
    return result


# Шаг 5: Функция измерения времени и памяти
def benchmark_operation(operation_func, df, name):
    """
    Измеряет время выполнения и потребление памяти для одной операции.
    Возвращает словарь с результатами.
    """
    # Замер времени
    start_time = time.time()
    # Замер памяти
    mem_usage = memory_profiler.memory_usage(
        (operation_func, (df,)), 
        interval=0.1, 
        timeout=None
    )
    end_time = time.time()
    
    time_elapsed = end_time - start_time
    max_memory = max(mem_usage) if mem_usage else 0
    
    return {
        'time': time_elapsed,
        'memory': max_memory
    }


# Шаг 6: Генерация отчёта и сравнение производительности
def generate_comparison_report(results):
    """
    Создаёт таблицу сравнения производительности и строит графики.
    """
    # Подготовка данных для таблицы
    data = []
    for method, res in results.items():
        data.append({
            'Метод': method,
            'Время (сек)': f"{res['time']:.4f}",
            'Память (MiB)': f"{res['memory']:.2f}"
        })
    
    # Создаём DataFrame для вывода
    report_df = pd.DataFrame(data)
    print("\n=== БЕНЧМАРК: СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ ===")
    print(report_df.to_string(index=False))
    
    # График времени
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    methods = [r['Метод'] for r in data]
    times = [float(r['Время (сек)']) for r in data]
    plt.bar(methods, times, color=['blue', 'orange', 'green'])
    plt.title('Время выполнения')
    plt.ylabel('Время (сек)')
    plt.xticks(rotation=45)
    plt.grid(True)
    
    # График памяти
    plt.subplot(1, 2, 2)
    memories = [float(r['Память (MiB)']) for r in data]
    plt.bar(methods, memories, color=['blue', 'orange', 'green'])
    plt.title('Потребление памяти')
    plt.ylabel('Память (MiB)')
    plt.xticks(rotation=45)
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()


# Главная функция
def main():
    print("Начинаем тестирование производительности...")
    
    # Генерируем датасет
    print("Генерация датасета (1 млн записей)...")
    df = generate_large_dataset()
    print(f"Размер датасета: {df.shape}")
    
    # Результаты
    results = {}
    
    # Тест 1: pandas
    print("\n--- Тест 1: pandas ---")
    result_pandas = benchmark_operation(pandas_analysis, df, "pandas")
    results["pandas"] = result_pandas
    
    # Тест 2: pandas + PyArrow
    print("\n--- Тест 2: pandas + PyArrow ---")
    try:
        result_pandas_pyarrow = benchmark_operation(pandas_pyarrow_analysis, df, "pandas+pyarrow")
        results["pandas+pyarrow"] = result_pandas_pyarrow
    except Exception as e:
        print(f"Ошибка при использовании PyArrow: {e}")
        print("Пропускаем этот тест.")
        results["pandas+pyarrow"] = {"time": float('nan'), "memory": float('nan')}
    
    # Тест 3: Polars
    print("\n--- Тест 3: Polars ---")
    result_polars = benchmark_operation(polars_analysis, df, "polars")
    results["polars"] = result_polars
    
    # Генерируем отчёт
    generate_comparison_report(results)
    
    print("\nВсе тесты завершены.")


# Запуск программы
if __name__ == "__main__":
    main()