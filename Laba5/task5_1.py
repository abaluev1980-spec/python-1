import os
import re
import requests
from pathlib import Path

# Определяем директорию, где находится текущий скрипт
SCRIPT_DIR = Path(__file__).parent.resolve()
ARTICLES_DIR = SCRIPT_DIR / "articles"


def sanitize_filename(filename: str) -> str:
    """Удаляет или заменяет недопустимые символы в имени файла."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename).strip()[:100]


def load_articles_from_folder(folder_path: Path) -> list:
    articles = []
    if not folder_path.exists():
        return articles
    for file_path in folder_path.glob("*.txt"):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            title = file_path.stem  # Имя файла без расширения
            articles.append({'title': title, 'content': content})
    return articles


def download_wikipedia_articles(topic: str, count: int = 5, folder_path: Path = None) -> list:
    if folder_path is None:
        folder_path = ARTICLES_DIR
    folder_path.mkdir(exist_ok=True)

    base_url = "https://ru.wikipedia.org/w/api.php"
    headers = {
        "User-Agent": "PermianRAG/1.0 (https://github.com/yourname/permian-rag; contact@example.com)"
    }
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'search',
        'srsearch': topic,
        'srlimit': str(count),
        'srprop': 'size|wordcount'
    }

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        articles = []
        search_results = data.get('query', {}).get('search', [])
        for i, result in enumerate(search_results, 1):
            title = result['title']
            pageid = result['pageid']

            content_params = {
                'action': 'query',
                'format': 'json',
                'prop': 'extracts',
                'exintro': False,
                'explaintext': True,
                'pageids': pageid
            }
            content_response = requests.get(base_url, params=content_params, headers=headers, timeout=10)
            content_response.raise_for_status()
            extract = content_response.json()['query']['pages'][str(pageid)]['extract']

            article = {'title': title, 'content': extract}
            articles.append(article)

            # Сохраняем файл рядом с кодом — в папке articles
            safe_title = sanitize_filename(title)
            filename = f"{i:02d}_{safe_title}.txt"
            filepath = folder_path / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(extract)
            print(f"Сохранена статья: {filename}")

        return articles

    except Exception as e:
        raise RuntimeError(f"Ошибка загрузки статей из Википедии: {str(e)}")


def calculate_statistics(articles: list) -> dict:
    total_docs = len(articles)
    total_symbols = sum(len(article['content']) for article in articles)
    total_words = sum(len(article['content'].split()) for article in articles)
    avg_length = total_symbols / total_docs if total_docs > 0 else 0
    return {
        'total_documents': total_docs,
        'total_symbols': total_symbols,
        'total_words': total_words,
        'average_length': round(avg_length, 2)
    }


def main():
    print("Загрузка статей на тему 'Пермский период'...")
    print(f"Папка для статей: {ARTICLES_DIR}")

    all_articles = []

    # Загрузка из Википедии с сохранением в articles рядом с кодом
    try:
        wiki_articles = download_wikipedia_articles("Пермский период", count=5, folder_path=ARTICLES_DIR)
        all_articles.extend(wiki_articles)
        print(f"Загружено {len(wiki_articles)} статей из Википедии.")
    except Exception as e:
        print(f"Не удалось загрузить статьи из Википедии: {e}")

    # Загрузка всех .txt файлов из папки articles (включая только что сохранённые)
    local_articles = load_articles_from_folder(ARTICLES_DIR)
    all_articles = local_articles  # Используем именно то, что лежит в папке

    if not all_articles:
        print("Нет статей для обработки.")
        return

    stats = calculate_statistics(all_articles)
    print("\n--- СТАТИСТИКА ---")
    print(f"Количество документов: {stats['total_documents']}")
    print(f"Общее количество символов: {stats['total_symbols']}")
    print(f"Общее количество слов: {stats['total_words']}")
    print(f"Средняя длина статьи (символов): {stats['average_length']}")


if __name__ == "__main__":
    main()