# Импортируем необходимые библиотеки
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Устанавливаем стиль визуализации
sns.set_style("whitegrid")

# Шаг 1: Загрузка датасета Titanic
print("=== Загрузка датасета Titanic ===")
df = sns.load_dataset('titanic')
print(f"Размер датасета: {df.shape}")
print("\nПервые 5 строк:")
print(df.head())

# Шаг 2: Анализ структуры данных
print("\n=== Анализ структуры данных ===")
print("\nТипы столбцов:")
print(df.dtypes)

print("\nПропущенные значения:")
print(df.isnull().sum())

# Шаг 3: Статистическое описание числовых признаков
print("\n=== Статистическое описание числовых признаков ===")
print(df.describe(include='number'))

# Шаг 4: Группировка по полу и классу каюты с расчётом выживаемости
print("\n=== Группировка по полу и классу каюты ===")
survival_by_sex_class = df.groupby(['sex', 'class'])['survived'].mean().reset_index()
print(survival_by_sex_class)

# Шаг 5: Создание новых признаков (feature engineering)
def create_features(df):
    """
    Добавляет новые признаки в датафрейм:
    - age_group — возрастные группы
    - family_size — размер семьи (sibsp + parch)
    """
    # Создаём возрастные группы с помощью pd.cut
    df['age_group'] = pd.cut(
        df['age'], 
        bins=[0, 18, 30, 50, 100], 
        labels=['child', 'young', 'adult', 'senior']
    )

    # Размер семьи = количество братьев/сестёр + родителей/детей
    df['family_size'] = df['sibsp'] + df['parch']

    return df

# Применяем функцию
df = create_features(df)
print("\n=== Новые признаки добавлены ===")
print(df[['age', 'age_group', 'sibsp', 'parch', 'family_size']].head())

# Шаг 6: Сравнение производительности операций с разными типами данных

# 1. Стандартные типы (object, int64, float64)
print("\n=== Производительность: стандартные типы ===")
# Время выполнения операции groupby на исходном датафрейме
start_time = pd.Timestamp.now()
result1 = df.groupby('sex')['age'].mean()
end_time = pd.Timestamp.now()
print(f"Время groupby (стандартные типы): {(end_time - start_time).total_seconds():.4f} сек.")

# 2. Категориальные типы (category)
print("\n=== Производительность: категориальные типы ===")
# Преобразуем некоторые столбцы в category
df_cat = df.copy()
df_cat['sex'] = df_cat['sex'].astype('category')
df_cat['class'] = df_cat['class'].astype('category')
df_cat['embarked'] = df_cat['embarked'].astype('category')

start_time = pd.Timestamp.now()
result2 = df_cat.groupby('sex')['age'].mean()
end_time = pd.Timestamp.now()
print(f"Время groupby (категории): {(end_time - start_time).total_seconds():.4f} сек.")

# 3. Типы PyArrow (string[pyarrow], int64[pyarrow])
print("\n=== Производительность: PyArrow типы ===")
# Проверяем, поддерживается ли PyArrow
try:
    df_pyarrow = df.copy()
    # Преобразуем строки в PyArrow-строки
    for col in df_pyarrow.select_dtypes(include=['object']).columns:
        df_pyarrow[col] = df_pyarrow[col].astype('string[pyarrow]')
    # Преобразуем целые числа
    for col in df_pyarrow.select_dtypes(include=['int64']).columns:
        df_pyarrow[col] = df_pyarrow[col].astype('int64[pyarrow]')

    start_time = pd.Timestamp.now()
    result3 = df_pyarrow.groupby('sex')['age'].mean()
    end_time = pd.Timestamp.now()
    print(f"Время groupby (PyArrow): {(end_time - start_time).total_seconds():.4f} сек.")
except Exception as e:
    print(f"Ошибка при использовании PyArrow: {e}")
    print("PyArrow может не быть установлен или не поддерживаться вашей версией pandas.")

# Шаг 7: Визуализация с seaborn

print("\n=== Визуализация данных ===")

# 1. Матрица корреляций (тепловая карта)
plt.figure(figsize=(10, 8))
sns.heatmap(df.corr(numeric_only=True), annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Матрица корреляций числовых признаков')
plt.show()

# 2. Распределение возрастов с разбивкой по полу и выживаемости
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
sns.histplot(data=df, x='age', hue='sex', multiple='stack', kde=True)
plt.title('Распределение возрастов по полу')

plt.subplot(1, 2, 2)
sns.histplot(data=df, x='age', hue='survived', multiple='stack', kde=True)
plt.title('Распределение возрастов по выживаемости')

plt.tight_layout()
plt.show()

# 3. Количество выживших в разрезе класса каюты и порта посадки
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
sns.countplot(data=df, x='class', hue='survived')
plt.title('Выживаемость по классу каюты')

plt.subplot(1, 2, 2)
sns.countplot(data=df, x='embarked', hue='survived')
plt.title('Выживаемость по порту посадки')

plt.tight_layout()
plt.show()

# 4. Ящики с усами (boxplot) стоимости билета по классам
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='class', y='fare')
plt.title('Стоимость билета по классам каюты')
plt.show()

# Шаг 8: Интерактивная визуализация с фильтрацией

def create_interactive_dashboard(df):
    """
    Создаёт интерактивную панель с фильтрами по возрасту и классу.
    """
    # Удаляем строки, где возраст неизвестен (NaN), чтобы избежать пустых результатов
    df_clean = df.dropna(subset=['age']).copy()
    
    # Фильтры по умолчанию
    age_min, age_max = 18, 60
    class_filter = [1, 2, 3]

    # Фильтруем данные
    filtered_df = df_clean[
        (df_clean['age'] >= age_min) & 
        (df_clean['age'] <= age_max) &
        (df_clean['pclass'].isin(class_filter))  # Обратите внимание: столбец называется 'pclass', не 'class'!
    ]

    # Проверяем, что после фильтрации остались данные
    if filtered_df.empty:
        print("После фильтрации не осталось данных. Попробуйте другие параметры.")
        return None

    # Создаём фигуру с несколькими графиками
    fig = plt.figure(figsize=(15, 10))

    # График 1: Распределение возраста в отфильтрованных данных
    ax1 = fig.add_subplot(2, 2, 1)
    sns.histplot(data=filtered_df, x='age', hue='survived', ax=ax1)
    ax1.set_title('Распределение возраста (фильтр: возраст и класс)')

    # График 2: Выживаемость по полу
    ax2 = fig.add_subplot(2, 2, 2)
    sns.countplot(data=filtered_df, x='sex', hue='survived', ax=ax2)
    ax2.set_title('Выживаемость по полу')

    # График 3: Выживаемость по классу
    ax3 = fig.add_subplot(2, 2, 3)
    sns.countplot(data=filtered_df, x='pclass', hue='survived', ax=ax3)  # Используем 'pclass'
    ax3.set_title('Выживаемость по классу')

    # График 4: Стоимость билета по классу
    ax4 = fig.add_subplot(2, 2, 4)
    sns.boxplot(data=filtered_df, x='pclass', y='fare', ax=ax4)  # Используем 'pclass'
    ax4.set_title('Стоимость билета по классу')

    plt.tight_layout()
    plt.show()

    return fig

# Запускаем интерактивную панель
print("\n=== Интерактивная визуализация с фильтрацией ===")
create_interactive_dashboard(df)

print("\nВсе шаги выполнены успешно.")