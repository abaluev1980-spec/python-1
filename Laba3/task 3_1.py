import json
from functools import reduce
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()


def load_json_file(filename):
    filepath = SCRIPT_DIR / filename
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл не найден: {filepath}")
    except json.JSONDecodeError:
        raise ValueError(f"Некорректный JSON в файле: {filepath}")


# ===== 1. Обработка простого списка стран =====

def to_upper(names):
    return list(map(str.upper, names))


def filter_by_substring(pattern, names):
    return list(filter(lambda name: pattern in name, names))


def filter_by_exact_length(length, names):
    return list(filter(lambda name: len(name) == length, names))


def filter_by_min_length(min_len, names):
    return list(filter(lambda name: len(name) >= min_len, names))


def filter_by_startswith(letter, names):
    return list(filter(lambda name: name.startswith(letter), names))


def join_nordic_countries(countries):
    nordic_names = {"Finland", "Sweden", "Denmark", "Norway", "Iceland"}
    filtered_names = [c["name"] for c in countries if c["name"] in nordic_names]
    if not filtered_names:
        return ""
    def combine(acc, name):
        parts = acc.split(", ")
        if len(parts) == len(filtered_names) - 1:
            return acc + " and " + name
        else:
            return acc + ", " + name
    result = reduce(combine, filtered_names[1:], filtered_names[0])
    return result + " are countries of North Europe"


# ===== 2. Через генераторы =====

def to_upper_gen(names):
    return [name.upper() for name in names]

def filter_by_substring_gen(pattern, names):
    return [name for name in names if pattern in name]

def filter_by_exact_length_gen(length, names):
    return [name for name in names if len(name) == length]

def filter_by_min_length_gen(min_len, names):
    return [name for name in names if len(name) >= min_len]

def filter_by_startswith_gen(letter, names):
    return [name for name in names if name.startswith(letter)]

def join_nordic_countries_gen(countries):
    nordic = {"Finland", "Sweden", "Denmark", "Norway", "Iceland"}
    names = [c["name"] for c in countries if c["name"] in nordic]
    if not names:
        return ""
    if len(names) == 1:
        return f"{names[0]} is a country of North Europe"
    return ", ".join(names[:-1]) + " and " + names[-1] + " are countries of North Europe"


# ===== 3. Каррирование и замыкания =====

categorize_curried = lambda pattern: lambda countries: [c for c in countries if pattern in c]

def make_categorizer(pattern):
    def categorize(countries):
        return [c for c in countries if pattern in c]
    return categorize


# ===== 4. Работа с полными данными =====

def sort_countries_by(data, key):
    if key not in {"name", "capital", "population"}:
        raise ValueError("Ключ должен быть 'name', 'capital' или 'population'")
    return sorted(data, key=lambda x: x.get(key, ""))


def get_top_languages(data, top_n=10):
    from collections import defaultdict
    lang_to_countries = defaultdict(list)
    for country in data:  # ← ИСПРАВЛЕНО: было "for country in "
        for lang in country.get("languages", []):
            lang_to_countries[lang].append(country["name"])
    sorted_langs = sorted(
        lang_to_countries.items(),
        key=lambda item: len(item[1]),
        reverse=True
    )
    return [(lang, countries) for lang, countries in sorted_langs[:top_n]]


def get_top_populated_countries(data, top_n=10):
    return sorted(
        data,
        key=lambda x: x.get("population", 0),
        reverse=True
    )[:top_n]


# ===== 5. Главная функция =====

def main():
    try:
        countries_simple = load_json_file("countries.json")
        countries_full = load_json_file("countries-data.json")

        print("=== 1. ВЕРХНИЙ РЕГИСТР ===")
        print(to_upper(countries_simple)[:5])

        print("\n=== 2. Фильтрация ===")
        print("Содержат 'land':", filter_by_substring('land', countries_simple))
        print("Ровно 6 символов:", filter_by_exact_length(6, countries_simple))
        print("6+ символов:", len(filter_by_min_length(6, countries_simple)))
        print("Начинаются на 'E':", filter_by_startswith('E', countries_simple))

        print("\n=== 3. Страны Северной Европы (reduce) ===")
        print(join_nordic_countries(countries_full))

        print("\n=== 4. Генераторы ===")
        print("Содержат 'ia':", filter_by_substring_gen('ia', countries_simple))

        print("\n=== 5. Каррирование и замыкания ===")
        print("land:", categorize_curried('land')(countries_simple)[:3])
        print("ia:", make_categorizer('ia')(countries_simple)[:3])

        print("\n=== 6. Полные данные ===")
        print("Сортировка по названию:")
        for c in sort_countries_by(countries_full, "name")[:3]:
            print(f"  - {c['name']}")

        print("\nТоп-5 языков:")
        for lang, countries in get_top_languages(countries_full, 5):
            print(f"  - {lang}: {len(countries)} стран")

        print("\nТоп-5 самых населённых стран:")
        for c in get_top_populated_countries(countries_full, 5):
            pop = f"{c['population']:,}"
            print(f"  - {c['name']}: {pop}")

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()