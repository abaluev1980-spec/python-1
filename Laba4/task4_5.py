import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats

# Устанавливаем стиль визуализации
sns.set_style("whitegrid")

# Шаг 1: Загрузка данных
def load_wine_data():
    """
    Загружает датасет красного вина из локального файла 'winequality-red.csv',
    который использует запятую ',' в качестве разделителя.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'winequality-red.csv')
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Файл 'winequality-red.csv' не найден в папке: {current_dir}"
        )
    
    # Используем запятую как разделитель (по умолчанию)
    wine_data = pd.read_csv(file_path)
    
    # Проверяем наличие столбца 'quality'
    if 'quality' not in wine_data.columns:
        raise KeyError("Столбец 'quality' не найден. Убедитесь, что файл имеет правильный формат.")
    
    # Создаём категорию качества
    wine_data['quality_category'] = pd.cut(
        wine_data['quality'],
        bins=[0, 4, 6, 10],
        labels=['Низкое', 'Среднее', 'Высокое']
    )
    
    return wine_data

# --- ЧАСТЬ 1: ИССЛЕДОВАНИЕ ХАРАКТЕРИСТИК ---

def analyze_characteristics(wine_data):
    """
    Выполняет исследование характеристик вина.
    """
    print("=== ИССЛЕДОВАНИЕ ХАРАКТЕРИСТИК ===\n")
    
    # 1. Распределение показателей качества
    print("1. Распределение показателей качества:")
    quality_counts = wine_data['quality'].value_counts().sort_index()
    print(quality_counts)
    
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    sns.countplot(data=wine_data, x='quality')
    plt.title('Распределение оценок качества')
    plt.xlabel('Качество')
    plt.ylabel('Количество')
    
    plt.subplot(1, 2, 2)
    sns.countplot(data=wine_data, x='quality_category')
    plt.title('Распределение категорий качества')
    plt.xlabel('Категория')
    plt.ylabel('Количество')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
    # 2. Анализ выбросов в химических показателях
    print("\n2. Анализ выбросов в химических показателях:")
    # Выбираем числовые столбцы (кроме 'quality' и 'quality_category')
    numeric_cols = wine_data.select_dtypes(include=['number']).columns.drop(['quality'])
    
    plt.figure(figsize=(15, 10))
    for i, col in enumerate(numeric_cols, 1):
        plt.subplot(4, 4, i)
        sns.boxplot(y=wine_data[col])
        plt.title(col)
        plt.ylabel('')
    plt.suptitle('Ящики с усами для химических показателей')
    plt.tight_layout()
    plt.show()
    
    # 3. Изучение корреляций между свойствами вина
    print("\n3. Изучение корреляций между свойствами вина:")
    corr_matrix = wine_data[numeric_cols].corr()
    plt.figure(figsize=(12, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', center=0)
    plt.title('Матрица корреляций химических показателей')
    plt.show()

# --- ЧАСТЬ 2: СРАВНИТЕЛЬНЫЙ АНАЛИЗ ---

def comparative_analysis(wine_data):
    """
    Выполняет сравнительный анализ вин разного качества.
    """
    print("\n=== СРАВНИТЕЛЬНЫЙ АНАЛИЗ ===\n")

    # 🔴 ДОБАВЛЕНО: определяем числовые столбцы
    numeric_cols = wine_data.select_dtypes(include=['number']).columns.drop(['quality', 'quality_category'], errors='ignore')
    
    # 1. Сравнение химического состава вин разного качества
    print("1. Сравнение химического состава вин разного качества:")
    grouped = wine_data.groupby('quality_category').mean(numeric_only=True)
    print(grouped.T)

    # Визуализация
    plt.figure(figsize=(15, 10))
    for i, col in enumerate(numeric_cols, 1):
        plt.subplot(4, 4, i)
        sns.boxplot(data=wine_data, x='quality_category', y=col)
        plt.title(col)
        plt.xticks(rotation=45)
    plt.suptitle('Химический состав по категориям качества')
    plt.tight_layout()
    plt.show()

    # 2. Влияние кислотности на общую оценку
    print("\n2. Влияние кислотности на общую оценку:")
    # Общая кислотность = fixed acidity + volatile acidity
    wine_data['total_acidity'] = wine_data['fixed acidity'] + wine_data['volatile acidity']

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    sns.scatterplot(data=wine_data, x='total_acidity', y='quality')
    plt.title('Общая кислотность vs Качество')
    plt.xlabel('Общая кислотность')
    plt.ylabel('Качество')

    plt.subplot(1, 2, 2)
    sns.boxplot(data=wine_data, x='quality_category', y='total_acidity')
    plt.title('Общая кислотность по категориям качества')
    plt.xlabel('Категория качества')
    plt.ylabel('Общая кислотность')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # 3. Анализ связи алкоголя и качества
    print("\n3. Анализ связи алкоголя и качества:")
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    sns.scatterplot(data=wine_data, x='alcohol', y='quality')
    plt.title('Алкоголь vs Качество')
    plt.xlabel('Алкоголь (%)')
    plt.ylabel('Качество')

    plt.subplot(1, 2, 2)
    sns.boxplot(data=wine_data, x='quality_category', y='alcohol')
    plt.title('Алкоголь по категориям качества')
    plt.xlabel('Категория качества')
    plt.ylabel('Алкоголь (%)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
    # 2. Влияние кислотности на общую оценку
    print("\n2. Влияние кислотности на общую оценку:")
    # Общая кислотность = fixed acidity + volatile acidity
    wine_data['total_acidity'] = wine_data['fixed acidity'] + wine_data['volatile acidity']
    
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    sns.scatterplot(data=wine_data, x='total_acidity', y='quality')
    plt.title('Общая кислотность vs Качество')
    plt.xlabel('Общая кислотность')
    plt.ylabel('Качество')
    
    plt.subplot(1, 2, 2)
    sns.boxplot(data=wine_data, x='quality_category', y='total_acidity')
    plt.title('Общая кислотность по категориям качества')
    plt.xlabel('Категория качества')
    plt.ylabel('Общая кислотность')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
    # 3. Анализ связи алкоголя и качества
    print("\n3. Анализ связи алкоголя и качества:")
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    sns.scatterplot(data=wine_data, x='alcohol', y='quality')
    plt.title('Алкоголь vs Качество')
    plt.xlabel('Алкоголь (%)')
    plt.ylabel('Качество')
    
    plt.subplot(1, 2, 2)
    sns.boxplot(data=wine_data, x='quality_category', y='alcohol')
    plt.title('Алкоголь по категориям качества')
    plt.xlabel('Категория качества')
    plt.ylabel('Алкоголь (%)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# --- ЧАСТЬ 3: ГИПОТЕЗЫ И ПРОВЕРКИ ---

def test_hypotheses(wine_data):
    """
    Проверяет гипотезы о влиянии различных факторов на качество вина.
    """
    print("\n=== ГИПОТЕЗЫ И ПРОВЕРКИ ===\n")
    
    # 1. Влияние уровня сахара на воспринимаемое качество
    print("1. Влияние уровня сахара на воспринимаемое качество:")
    # Сахар — это 'residual sugar'
    # Разделим вина на две группы: низкий сахар (< медианы) и высокий сахар (>= медианы)
    median_sugar = wine_data['residual sugar'].median()
    low_sugar = wine_data[wine_data['residual sugar'] < median_sugar]['quality']
    high_sugar = wine_data[wine_data['residual sugar'] >= median_sugar]['quality']
    
    # Проверяем гипотезу с помощью t-теста
    t_stat, p_value = stats.ttest_ind(low_sugar, high_sugar, equal_var=False)
    print(f"  t-статистика: {t_stat:.4f}, p-значение: {p_value:.4f}")
    if p_value < 0.05:
        print("Статистически значимое различие: уровень сахара влияет на качество.")
    else:
        print("Нет статистически значимого различия: уровень сахара не влияет на качество.")
    
    # Визуализация
    plt.figure(figsize=(10, 5))
    sns.boxplot(data=wine_data, x='quality_category', y='residual sugar')
    plt.title('Уровень сахара по категориям качества')
    plt.xlabel('Категория качества')
    plt.ylabel('Остаточный сахар')
    plt.xticks(rotation=45)
    plt.show()
    
    # 2. Связь между pH и кислотностью
    print("\n2. Связь между pH и кислотностью:")
    # Корреляция между pH и общей кислотностью
    correlation = wine_data['pH'].corr(wine_data['total_acidity'])
    print(f"  Коэффициент корреляции: {correlation:.4f}")
    if abs(correlation) > 0.5:
        print("Сильная связь между pH и кислотностью.")
    else:
        print("Слабая или умеренная связь между pH и кислотностью.")
    
    # Визуализация
    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=wine_data, x='pH', y='total_acidity')
    plt.title('pH vs Общая кислотность')
    plt.xlabel('pH')
    plt.ylabel('Общая кислотность')
    plt.grid(True)
    plt.show()
    
    # 3. Статистическая проверка различий между группами качества (алкоголь)
    print("\n3. Статистическая проверка различий по содержанию алкоголя в винах разного качества:")
    # Разделяем данные по категориям качества
    low_quality = wine_data[wine_data['quality_category'] == 'Низкое']['alcohol']
    medium_quality = wine_data[wine_data['quality_category'] == 'Среднее']['alcohol']
    high_quality = wine_data[wine_data['quality_category'] == 'Высокое']['alcohol']
    
    # ANOVA тест — проверяет, есть ли различия между средними трёх групп
    f_stat, p_value = stats.f_oneway(low_quality, medium_quality, high_quality)
    print(f"  F-статистика: {f_stat:.4f}, p-значение: {p_value:.4f}")
    if p_value < 0.05:
        print("Есть статистически значимые различия в содержании алкоголя между группами качества.")
    else:
        print("Нет статистически значимых различий в содержании алкоголя между группами качества.")
    
    # Визуализация
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=wine_data, x='quality_category', y='alcohol')
    plt.title('Алкоголь по категориям качества')
    plt.xlabel('Категория качества')
    plt.ylabel('Алкоголь (%)')
    plt.xticks(rotation=45)
    plt.show()

# Главная функция
def main():
    """Главная функция — загружает данные и выполняет все анализы."""
    print("Начинаем анализ набора данных качества вина...")
    
    # Загружаем данные
    wine_data = load_wine_data()
    print(f"Размер датасета: {wine_data.shape}")
    print("\nПервые 5 строк:")
    print(wine_data.head())
    
    # Исследование характеристик
    analyze_characteristics(wine_data)
    
    # Сравнительный анализ
    comparative_analysis(wine_data)
    
    # Проверка гипотез
    test_hypotheses(wine_data)
    
    print("\nВсе задачи выполнены успешно.")


# Запуск программы
if __name__ == "__main__":
    main()