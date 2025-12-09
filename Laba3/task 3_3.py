import time
import random
import math
from functools import wraps, lru_cache, reduce
from typing import List, Tuple, Dict, Any


# ==============================================================================
# 1. ДЕКОРАТОР ДЛЯ ИЗМЕРЕНИЯ ВРЕМЕНИ ВЫПОЛНЕНИЯ
# ==============================================================================

def timing_decorator(func):
    """
    Декоратор — это "обёртка" вокруг функции, которая добавляет новое поведение.
    Здесь — замер времени выполнения.
    
    @wraps(func) сохраняет оригинальное имя и документацию функции func,
    чтобы при отладке всё выглядело как вызов исходной функции.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()          # Запоминаем момент начала
        result = func(*args, **kwargs)    # Выполняем саму функцию
        end_time = time.time()            # Запоминаем момент окончания
        duration = end_time - start_time  # Считаем разницу
        print(f"{func.__name__} выполнен за {duration:.4f} секунд")
        return result                     # Возвращаем результат функции
    return wrapper


# ==============================================================================
# 2. ГЕНЕРАЦИЯ ТОЧЕК И РАССТОЯНИЙ
# ==============================================================================

def generate_points(n: int, bounds: tuple = (0, 100)) -> List[Tuple[float, float, float]]:
    """
    Генерирует n случайных точек в 3D-пространстве.
    Каждая координата (x, y, z) — случайное число в диапазоне [bounds[0], bounds[1]].
    """
    points = []
    for _ in range(n):
        x = random.uniform(bounds[0], bounds[1])
        y = random.uniform(bounds[0], bounds[1])
        z = random.uniform(bounds[0], bounds[1])
        points.append((x, y, z))
    return points


def build_distance_matrix_cached(points: List[Tuple[float, float, float]]) -> Dict[Tuple[int, int], float]:
    """
    Создаёт словарь расстояний между всеми парами точек.
    Использует @lru_cache для ускорения повторных вычислений расстояний.
    """
    # Внутренняя функция с кэшированием: принимает две точки и возвращает расстояние
    @lru_cache(maxsize=10000)
    def cached_distance(p1: Tuple[float, float, float], p2: Tuple[float, float, float]) -> float:
        # Вычисляем евклидово расстояние в 3D: sqrt((x1-x2)^2 + (y1-y2)^2 + (z1-z2)^2)
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        dz = p1[2] - p2[2]
        return math.sqrt(dx*dx + dy*dy + dz*dz)

    n = len(points)
    distances = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                # Передаём кортежи точек — они хешируемые, поэтому подходят для lru_cache
                distances[(i, j)] = cached_distance(points[i], points[j])
    return distances


# ==============================================================================
# 3. ФУНКЦИИ ДЛЯ PIPELINE ОБРАБОТКИ ДАННЫХ
# ==============================================================================

def normalize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Нормализует числовые данные: округляет до удобного числа знаков.
    Это делает вывод чище и избавляет от "мусора" вроде 28.3648123948123.
    """
    normalized = data.copy()  # создаём копию, чтобы не менять оригинал
    if 'best_length' in normalized:
        normalized['best_length'] = round(normalized['best_length'], 4)
    if 'avg_edge_length' in normalized:
        normalized['avg_edge_length'] = round(normalized['avg_edge_length'], 4)
    return normalized


def calculate_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Вычисляет дополнительные метрики на основе переданных данных.
    В данном случае — уже передаётся готовая средняя длина ребра,
    но эта функция показывает, как можно расширять анализ.
    """
    # Просто возвращаем данные, так как метрики уже рассчитаны
    return data.copy()


def generate_report(data: Dict[str, Any]) -> str:
    """
    Преобразует структурированные данные в читаемый текстовый отчёт.
    """
    report = (
        f"=== Отчёт для набора из {data['points_count']} точек ===\n"
        f"Лучшая длина маршрута: {data['best_length']}\n"
        f"Средняя длина ребра: {data['avg_edge_length']}\n"
        f"Количество итераций: {data['iterations']}\n"
        f"Количество муравьёв: {data['ants']}\n"
        f"----------------------------------------\n"
    )
    return report


def compose(*functions):
    """
    Объединяет несколько функций в одну.
    Например: compose(f, g, h)(x) = f(g(h(x)))
    Используется для создания конвейера обработки данных.
    """
    return reduce(lambda f, g: lambda x: f(g(x)), functions)


# Создаём pipeline: данные проходят через три этапа обработки
analysis_pipeline = compose(
    generate_report,      # последний этап — генерация текста
    calculate_metrics,    # второй этап — расчёт метрик
    normalize_data        # первый этап — округление чисел
)


# ==============================================================================
# 4. УПРОЩЁННЫЙ МУРАВЬИНЫЙ АЛГОРИТМ (БЕЗ ВИЗУАЛИЗАЦИИ)
# ==============================================================================

def ant_colony_optimization_simple(
    points: List[Tuple[float, float, float]],
    iterations: int = 50,
    ants: int = 20,
    alpha: float = 1.0,
    beta: float = 2.0,
    evaporation: float = 0.1,
    q: float = 100.0
) -> Tuple[List[int], float]:
    """
    Реализация муравьиного алгоритма без графики.
    Возвращает лучший найденный маршрут и его длину.
    """
    n = len(points)
    distances = build_distance_matrix_cached(points)

    # Инициализация феромонов: небольшое начальное значение на каждом ребре
    pheromone = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                pheromone[(i, j)] = 0.1

    best_path_overall = None
    best_length_overall = float('inf')  # бесконечность — чтобы любое число было меньше

    for iteration in range(iterations):
        all_paths = []

        # Каждый муравей строит свой маршрут
        for ant in range(ants):
            visited = set()
            path = []
            current = random.randint(0, n - 1)
            path.append(current)
            visited.add(current)

            # Пока не посетили все точки
            while len(visited) < n:
                unvisited = [i for i in range(n) if i not in visited]
                if not unvisited:
                    break

                # Рассчитываем вероятности перехода в каждую непосещённую точку
                probs = []
                total_prob = 0.0
                for node in unvisited:
                    if current == node:
                        prob = 0.0
                    else:
                        tau = pheromone.get((current, node), 0.1)  # уровень феромона
                        eta = 1.0 / distances[(current, node)]      # привлекательность
                        prob = (tau ** alpha) * (eta ** beta)
                    probs.append(prob)
                    total_prob += prob

                # Выбираем следующую точку
                if total_prob == 0:
                    next_node = random.choice(unvisited)
                else:
                    normalized_probs = [p / total_prob for p in probs]
                    next_node = random.choices(unvisited, weights=normalized_probs)[0]

                path.append(next_node)
                visited.add(next_node)
                current = next_node

            all_paths.append(path)

        # Находим лучший путь среди всех муравьёв на этой итерации
        def compute_path_length(path):
            total = 0.0
            for i in range(len(path)):
                a = path[i]
                b = path[(i + 1) % len(path)]
                total += distances.get((a, b), float('inf'))
            return total

        current_best_path = min(all_paths, key=compute_path_length)
        current_best_length = compute_path_length(current_best_path)

        # Обновляем общий лучший результат
        if current_best_length < best_length_overall:
            best_length_overall = current_best_length
            best_path_overall = current_best_path

        # Испарение феромонов
        for key in pheromone:
            pheromone[key] *= (1 - evaporation)

        # Усиление феромона на лучшем пути этой итерации
        if current_best_length > 0:
            for i in range(len(current_best_path)):
                a = current_best_path[i]
                b = current_best_path[(i + 1) % len(current_best_path)]
                if (a, b) in pheromone:
                    pheromone[(a, b)] += q / current_best_length

    return best_path_overall, best_length_overall


# ==============================================================================
# 5. ОСНОВНАЯ ФУНКЦИЯ — СРАВНИТЕЛЬНЫЙ АНАЛИЗ
# ==============================================================================

def main():
    """
    Запускает анализ на трёх наборах данных (200, 500, 1000 точек),
    собирает результаты и выводит подробную сводку.
    """
    print("Сравнительный анализ муравьиного алгоритма на разных объёмах данных")
    print("=" * 60)

    sizes = [200, 500, 1000]
    results = []  # список для хранения результатов по каждому размеру

    for size in sizes:
        print(f"\nЗапуск анализа для {size} точек...")

        # Замеряем время выполнения вручную, чтобы сохранить его
        start_time = time.time()

        # Генерация точек
        points = generate_points(size, bounds=(0, 100))

        # Запуск алгоритма
        best_path, best_length = ant_colony_optimization_simple(
            points, iterations=30, ants=15
        )

        end_time = time.time()
        elapsed_time = end_time - start_time

        # Вычисление средней длины ребра в лучшем маршруте
        if best_path and len(best_path) > 0:
            total_distance = 0.0
            n = len(best_path)
            for i in range(n):
                a_index = best_path[i]
                b_index = best_path[(i + 1) % n]
                # Извлекаем координаты точек
                p_a = points[a_index]
                p_b = points[b_index]
                dx = p_a[0] - p_b[0]
                dy = p_a[1] - p_b[1]
                dz = p_a[2] - p_b[2]
                edge_length = math.sqrt(dx*dx + dy*dy + dz*dz)
                total_distance += edge_length
            avg_edge_length = total_distance / n
        else:
            avg_edge_length = 0.0

        # Сохраняем результаты для сводки
        result_entry = {
            'size': size,
            'time': elapsed_time,
            'best_length': best_length,
            'avg_edge_length': avg_edge_length
        }
        results.append(result_entry)

        # Подготавливаем данные для pipeline и выводим полный отчёт
        raw_data = {
            'points_count': size,
            'points': points,
            'best_path': best_path,
            'best_length': best_length,
            'avg_edge_length': avg_edge_length,
            'iterations': 30,
            'ants': 15
        }
        full_report = analysis_pipeline(raw_data)
        print(full_report)

    # === Вывод информативной сводки ===
    print("\n=== СВОДКА РЕЗУЛЬТАТОВ ===")
    # Заголовок таблицы с выравниванием
    print(f"{'Точек':<8} {'Время (с)':<12} {'Лучшая длина':<15} {'Среднее ребро':<15}")
    print("-" * 58)

    # Построчный вывод результатов
    for entry in results:
        print(
            f"{entry['size']:<8} "
            f"{entry['time']:<12.2f} "
            f"{entry['best_length']:<15.2f} "
            f"{entry['avg_edge_length']:<15.2f}"
        )


# ==============================================================================
# ТОЧКА ВХОДА В ПРОГРАММУ
# ==============================================================================

if __name__ == "__main__":
    main()