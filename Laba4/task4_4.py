import numpy as np
import scipy.optimize as opt
import scipy.signal as signal
import matplotlib.pyplot as plt
import time

# --- ЧАСТЬ 1: ОПТИМИЗАЦИЯ ФУНКЦИИ РОЗЕНБРОКА ---

def rosenbrock(x):
    """
    Функция Розенброка — сложная многомерная функция.
    Минимум находится в точке x = [1, 1, ..., 1], значение = 0.
    Формула: sum(100*(x[i+1] - x[i]**2)**2 + (1 - x[i])**2)
    """
    return sum(100.0 * (x[1:] - x[:-1]**2)**2.0 + (1 - x[:-1])**2.0)

def benchmark_optimization():
    """
    Тестирует разные методы оптимизации для функции Розенброка.
    Для каждой точки старта генерируется случайный вектор размерности 10.
    Измеряется время, количество итераций, успешность и значение минимума.
    """
    methods = ['BFGS', 'CG', 'Nelder-Mead', 'Powell']
    results = {}

    for method in methods:
        print(f"\n--- Тестирование метода: {method} ---")
        
        start_time = time.time()
        
        # Генерируем случайную начальную точку (вектор из 10 элементов)
        x0 = np.random.random(10) * 2  # значения от 0 до 2
        
        # Запускаем оптимизацию
        result = opt.minimize(
            rosenbrock,     # целевая функция
            x0,             # начальная точка
            method=method   # метод оптимизации
        )
        
        end_time = time.time()
        
        # Сохраняем результаты
        results[method] = {
            'time': end_time - start_time,
            'iterations': result.nit,      # количество итераций
            'success': result.success,     # успешно ли найдено решение
            'minimum': result.fun          # значение функции в минимуме
        }
        
        print(f"  Время: {results[method]['time']:.4f} сек.")
        print(f"  Итерации: {results[method]['iterations']}")
        print(f"  Успешно: {results[method]['success']}")
        print(f"  Минимум: {results[method]['minimum']:.6f}")

    return results


# --- ЧАСТЬ 2: ЦИФРОВАЯ ОБРАБОТКА СИГНАЛА ---

def generate_test_signal(duration=2.0, sampling_rate=1000, noise_level=0.5):
    """
    Генерирует тестовый сигнал: синусоида + шум.
    Параметры:
    - duration: длительность сигнала в секундах
    - sampling_rate: частота дискретизации (точек в секунду)
    - noise_level: уровень шума (амплитуда)
    """
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    # Основной сигнал — синусоида с частотой 5 Гц
    signal_clean = np.sin(2 * np.pi * 5 * t)
    # Добавляем шум
    noise = np.random.normal(0, noise_level, len(t))
    signal_noisy = signal_clean + noise
    
    return t, signal_clean, signal_noisy

def apply_fourier_analysis(t, signal_noisy, sampling_rate):
    """
    Применяет Фурье-анализ для выделения частот в сигнале.
    Возвращает частоты и амплитуды.
    """
    # Вычисляем FFT (быстрое преобразование Фурье)
    fft_result = np.fft.fft(signal_noisy)
    # Частоты
    freqs = np.fft.fftfreq(len(t), 1 / sampling_rate)
    # Амплитуды (берём только положительные частоты)
    positive_freqs = freqs[:len(freqs)//2]
    amplitudes = np.abs(fft_result[:len(fft_result)//2]) * 2 / len(t)
    
    return positive_freqs, amplitudes

def apply_filter(t, signal_noisy, cutoff_freq=10, sampling_rate=1000):
    """
    Применяет низкочастотный фильтр (фильтр Баттерворта) для очистки сигнала от шума.
    cutoff_freq — частота среза (в Гц).
    """
    # Нормализация частоты (относительно Nyquist частоты)
    nyquist = 0.5 * sampling_rate
    normal_cutoff = cutoff_freq / nyquist
    
    # Создаём фильтр Баттерворта 4-го порядка
    b, a = signal.butter(4, normal_cutoff, btype='low', analog=False)
    
    # Применяем фильтр
    filtered_signal = signal.filtfilt(b, a, signal_noisy)
    
    return filtered_signal

def visualize_signals(t, signal_clean, signal_noisy, filtered_signal):
    """
    Визуализирует исходный, зашумлённый и отфильтрованный сигналы.
    """
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.plot(t, signal_clean, label='Чистый сигнал', color='green')
    plt.title('Чистый сигнал (без шума)')
    plt.xlabel('Время (с)')
    plt.ylabel('Амплитуда')
    plt.grid(True)
    plt.legend()
    
    plt.subplot(1, 3, 2)
    plt.plot(t, signal_noisy, label='Зашумлённый сигнал', color='red', alpha=0.7)
    plt.title('Зашумлённый сигнал')
    plt.xlabel('Время (с)')
    plt.ylabel('Амплитуда')
    plt.grid(True)
    plt.legend()
    
    plt.subplot(1, 3, 3)
    plt.plot(t, filtered_signal, label='Отфильтрованный сигнал', color='blue')
    plt.title('Сигнал после фильтрации')
    plt.xlabel('Время (с)')
    plt.ylabel('Амплитуда')
    plt.grid(True)
    plt.legend()
    
    plt.tight_layout()
    plt.show()

def main():
    """Главная функция — запускает обе части программы."""
    print("Начинаем научные вычисления с SciPy...\n")

    # --- ЧАСТЬ 1: Оптимизация ---
    print("=== ОПТИМИЗАЦИЯ ФУНКЦИИ РОЗЕНБРОКА ===")
    optimization_results = benchmark_optimization()
    
    print("\n=== РЕЗУЛЬТАТЫ ОПТИМИЗАЦИИ ===")
    for method, res in optimization_results.items():
        print(f"{method}: время={res['time']:.4f}s, итерации={res['iterations']}, минимум={res['minimum']:.6f}, успех={res['success']}")

    # --- ЧАСТЬ 2: Цифровая обработка сигнала ---
    print("\n=== ЦИФРОВАЯ ОБРАБОТКА СИГНАЛА ===")
    t, clean_signal, noisy_signal = generate_test_signal()
    print("Тестовый сигнал сгенерирован.")
    
    # Фурье-анализ
    freqs, amplitudes = apply_fourier_analysis(t, noisy_signal, 1000)
    print(f"Фурье-анализ выполнен. Максимальная амплитуда на частоте {freqs[np.argmax(amplitudes)]:.1f} Гц.")

    # Фильтрация
    filtered_signal = apply_filter(t, noisy_signal)
    print("Фильтрация сигнала завершена.")

    # Визуализация
    visualize_signals(t, clean_signal, noisy_signal, filtered_signal)
    print("Графики построены.")

    print("\nВсе задачи выполнены успешно.")


# Запуск программы
if __name__ == "__main__":
    main()