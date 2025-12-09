import random
import math
import asyncio
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Tuple, Dict


# ==============================================================================
# Класс для хранения состояния управления программой
# ==============================================================================

class ControlState:
    """
    Хранит флаги, управляющие поведением программы.
    Используется глобально, чтобы обработчик клавиш и основной цикл "видели" одно состояние.
    """
    def __init__(self):
        self.paused = False              # True, если алгоритм приостановлен
        self.restart_requested = False   # True, если нужно перезапустить
        self.quit_requested = False      # True, если пользователь нажал Q (но ещё не подтвердил выход)
        self.confirmed_quit = False      # True, если пользователь подтвердил выход
        self.delay = 0.05                # Задержка между кадрами (в секундах)


# Создаём один экземпляр состояния
control = ControlState()


# ==============================================================================
# Обработчик нажатий клавиш в окне графика
# ==============================================================================

def on_key(event):
    """
    Вызывается при нажатии клавиши, когда окно графика активно.
    Меняет состояние в объекте `control`.
    """
    key = event.key

    if key == 'p' or key == 'P':
        control.paused = not control.paused
        if control.paused:
            print("Пауза включена")
        else:
            print("Алгоритм возобновлён")

    elif key == 'r' or key == 'R':
        control.restart_requested = True
        print("Запрошен перезапуск")

    elif key == 'q' or key == 'Q':
        control.quit_requested = True
        print("Нажата клавиша Q. Подтвердите выход в консоли.")

    elif key == 'up':
        control.delay = max(0.001, control.delay * 0.7)
        print(f"Анимация ускорена. Задержка: {control.delay:.3f} сек")

    elif key == 'down':
        control.delay = min(1.0, control.delay / 0.7)
        print(f"Анимация замедлена. Задержка: {control.delay:.3f} сек")


# ==============================================================================
# Генератор точек в 3D
# ==============================================================================

def generate_points(n: int, bounds: tuple = (0, 100)):
    """
    Генерирует n точек с координатами (x, y, z) в заданном диапазоне.
    """
    for _ in range(n):
        x = random.uniform(bounds[0], bounds[1])
        y = random.uniform(bounds[0], bounds[1])
        z = random.uniform(bounds[0], bounds[1])
        yield (x, y, z)


# ==============================================================================
# Генератор рёбер (расстояний между точками)
# ==============================================================================

def generate_edges(points: List[Tuple[float, float, float]]):
    """
    Для каждой пары разных точек вычисляет расстояние и возвращает (i, j, расстояние).
    """
    n = len(points)
    for i in range(n):
        for j in range(n):
            if i != j:
                dx = points[i][0] - points[j][0]
                dy = points[i][1] - points[j][1]
                dz = points[i][2] - points[j][2]
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                yield (i, j, dist)


# ==============================================================================
# Вспомогательные функции муравьиного алгоритма
# ==============================================================================

def initialize_pheromones(n: int) -> Dict[Tuple[int, int], float]:
    """Создаёт начальную карту феромонов со значением 0.1 на каждом ребре."""
    pheromone = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                pheromone[(i, j)] = 0.1
    return pheromone


def calculate_transition_prob(pheromone, distances, current, next_node, alpha=1.0, beta=2.0):
    """Вычисляет вероятность перехода из current в next_node на основе феромонов и расстояния."""
    if current == next_node:
        return 0.0
    try:
        tau = pheromone[(current, next_node)]
        eta = 1.0 / distances[(current, next_node)]
        return (tau ** alpha) * (eta ** beta)
    except KeyError:
        return 0.0


def construct_path(pheromone, distances, n):
    """Один муравей строит маршрут, посещая все точки по одному разу."""
    visited = set()
    path = []
    current = random.randint(0, n - 1)
    path.append(current)
    visited.add(current)

    while len(visited) < n:
        unvisited = [i for i in range(n) if i not in visited]
        if not unvisited:
            break

        probs = []
        total = 0.0
        for node in unvisited:
            prob = calculate_transition_prob(pheromone, distances, current, node)
            probs.append(prob)
            total += prob

        if total == 0:
            next_node = random.choice(unvisited)
        else:
            normalized = [p / total for p in probs]
            next_node = random.choices(unvisited, weights=normalized)[0]

        path.append(next_node)
        visited.add(next_node)
        current = next_node

    return path


def path_length(path, distances):
    """Вычисляет общую длину замкнутого маршрута."""
    total = 0.0
    n = len(path)
    for i in range(n):
        a = path[i]
        b = path[(i + 1) % n]
        total += distances.get((a, b), float('inf'))
    return total


def update_pheromones(pheromone, best_path, distances, evaporation=0.1, q=100.0):
    """Обновляет феромоны: испарение + усиление на лучшем пути."""
    for key in pheromone:
        pheromone[key] *= (1 - evaporation)

    length = path_length(best_path, distances)
    if length > 0:
        n = len(best_path)
        for i in range(n):
            a = best_path[i]
            b = best_path[(i + 1) % n]
            if (a, b) in pheromone:
                pheromone[(a, b)] += q / length

    return pheromone


# ==============================================================================
# Основная функция визуализации с встроенным алгоритмом
# ==============================================================================

async def visualize_optimization(points: List[Tuple[float, float, float]], iterations=50, ants=20):
    """
    Выполняет алгоритм и отображает результат в реальном времени.
    Поддерживает паузу, перезапуск и запрос на выход.
    """
    plt.ion()
    fig = plt.figure(figsize=(12, 5))
    fig.canvas.mpl_connect('key_press_event', on_key)
    ax3d = fig.add_subplot(121, projection='3d')
    ax2d = fig.add_subplot(122)

    ax3d.set_title("3D TSP — лучший маршрут\n(P=пауза, R=перезапуск, Q=выход, ↑↓=скорость)")
    ax2d.set_title("Длина маршрута")
    ax2d.set_xlabel("Итерация")
    ax2d.set_ylabel("Длина")

    n = len(points)
    distances = { (i, j): dist for i, j, dist in generate_edges(points) }
    pheromone = initialize_pheromones(n)

    lengths = []
    iteration = 1

    for it in range(iterations):
        # Если пользователь нажал Q — выходим из цикла, но не закрываем сразу
        if control.quit_requested:
            break

        # Обработка паузы с обновлением GUI
        while control.paused:
            if control.quit_requested:
                break
            fig.canvas.flush_events()
            plt.pause(0.01)
            await asyncio.sleep(0.01)

        if control.restart_requested:
            plt.ioff()
            plt.close(fig)
            return

        # Генерация путей
        paths = [construct_path(pheromone, distances, n) for _ in range(ants)]
        best_path = min(paths, key=lambda p: path_length(p, distances))
        best_len = path_length(best_path, distances)
        pheromone = update_pheromones(pheromone, best_path, distances)

        # Визуализация
        ax3d.clear()
        xs, ys, zs = zip(*points)
        ax3d.scatter(xs, ys, zs, c='blue', s=30)

        if best_path:
            cycle = best_path + [best_path[0]]
            px = [points[i][0] for i in cycle]
            py = [points[i][1] for i in cycle]
            pz = [points[i][2] for i in cycle]
            ax3d.plot(px, py, pz, 'r-', linewidth=1.5)

        ax3d.grid(True)

        lengths.append(best_len)
        ax2d.clear()
        ax2d.plot(range(1, len(lengths) + 1), lengths, 'b-o', markersize=3)
        ax2d.set_title(f"Итерация {iteration}, длина: {best_len:.2f}")

        plt.draw()
        fig.canvas.flush_events()

        await asyncio.sleep(control.delay)
        iteration += 1

    # Алгоритм завершил все итерации
    plt.ioff()
    plt.close(fig)


# ==============================================================================
# Спрашиваем у пользователя, хочет ли он выйти
# ==============================================================================

def ask_for_exit():
    """
    Запрашивает у пользователя подтверждение выхода.
    Возвращает True, если пользователь подтверждает выход.
    """
    while True:
        answer = input("Алгоритм завершён. Хотите выйти из программы? (y/n): ").strip().lower()
        if answer in ('y', 'yes', 'да'):
            return True
        elif answer in ('n', 'no', 'нет'):
            return False
        else:
            print("Пожалуйста, введите 'y' (да) или 'n' (нет).")


# ==============================================================================
# Запуск одной сессии
# ==============================================================================

async def run_session(n_points=50, n_iterations=50, n_ants=20):
    """
    Генерирует точки и запускает визуализацию.
    """
    print(f"Генерация {n_points} точек...")
    points_list = list(generate_points(n_points, bounds=(0, 100)))
    await visualize_optimization(points_list, iterations=n_iterations, ants=n_ants)


# ==============================================================================
# Главная функция программы
# ==============================================================================

async def main():
    """
    Основной цикл программы.
    Позволяет перезапускать, запрашивает подтверждение на выход.
    """
    print("Запуск интерактивного муравьиного алгоритма для задачи коммивояжёра в 3D")
    print("Управление (активно, когда окно графика в фокусе):")
    print("  P — пауза/возобновление")
    print("  R — перезапуск с новыми точками")
    print("  Q — запрос на выход")
    print("  Стрелка вверх/вниз — ускорить/замедлить анимацию")
    print("-" * 60)

    while True:
        control.restart_requested = False
        control.quit_requested = False
        control.confirmed_quit = False

        plt.close('all')
        await run_session()

        # Проверяем, был ли запрошен выход во время работы
        if control.quit_requested:
            # Запрашиваем подтверждение в консоли
            print("\nОбнаружено нажатие Q.")
            if ask_for_exit():
                break
            else:
                print("Продолжаем работу...")
                continue

        # Если алгоритм просто завершился сам
        else:
            if ask_for_exit():
                break
            else:
                print("Запуск новой сессии...")
                continue

    plt.close('all')
    print("Программа завершена.")


# ==============================================================================
# Точка входа
# ==============================================================================

if __name__ == "__main__":
    asyncio.run(main())