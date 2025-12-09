import os
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# Определяем пути относительно расположения скрипта
SCRIPT_DIR = Path(__file__).parent.resolve()
ARTICLES_DIR = SCRIPT_DIR / "articles"
CHROMA_DIR = SCRIPT_DIR / "chroma_db"


def ensure_articles_exist():
    """Проверяет, что папка articles существует и содержит .txt файлы."""
    if not ARTICLES_DIR.exists():
        raise FileNotFoundError(
            f"Папка 'articles' не найдена рядом с программой.\n"
            f"Ожидаемый путь: {ARTICLES_DIR}\n"
            "Поместите текстовые файлы (.txt) о Пермском периоде в эту папку."
        )
    txt_files = list(ARTICLES_DIR.glob("*.txt"))
    if not txt_files:
        raise ValueError(
            f"Папка 'articles' существует, но не содержит .txt файлов.\n"
            f"Добавьте хотя бы один текстовый файл в: {ARTICLES_DIR}"
        )


def load_and_chunk_documents(chunk_size=1000, chunk_overlap=200):
    """Загружает документы из папки articles и разбивает на чанки."""
    loader = DirectoryLoader(
        str(ARTICLES_DIR),
        glob="*.txt",
        show_progress=True,
        loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(documents)

    print(f"Загружено документов: {len(documents)}")
    print(f"Создано чанков: {len(chunks)}")
    return chunks


def create_vectorstore(chunks, model_name="nomic-embed-text"):
    """Создаёт или загружает векторную базу данных в chroma_db."""
    embeddings = OllamaEmbeddings(model=model_name)

    if CHROMA_DIR.exists():
        print("Загружается существующая векторная база данных...")
        vectorstore = Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=embeddings
        )
    else:
        print("Создаётся новая векторная база данных...")
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(CHROMA_DIR)
        )

    print(f"Векторная база данных сохранена в: {CHROMA_DIR}")
    return vectorstore


def main():
    print("=== Задание 2: Обработка документов и создание эмбеддингов ===")

    # Шаг 1: Проверка наличия статей
    ensure_articles_exist()

    # Шаг 2: Загрузка и разбиение на чанки
    chunks = load_and_chunk_documents(chunk_size=1000, chunk_overlap=200)

    # Шаг 3: Создание векторной базы
    vectorstore = create_vectorstore(chunks, model_name="nomic-embed-text")

    # Шаг 4: Вывод статистики
    total_chars = sum(len(chunk.page_content) for chunk in chunks)
    avg_len = total_chars / len(chunks) if chunks else 0

    print("\n--- СТАТИСТИКА ---")
    print(f"Количество чанков: {len(chunks)}")
    print(f"Общее количество символов: {total_chars}")
    print(f"Средняя длина чанка: {avg_len:.0f} символов")

        # Шаг 5: Проверка работоспособности поиска
    if chunks:
        test_query = "Пермский период"
        results = vectorstore.similarity_search(test_query, k=1)
        print(f"\nТестовый поисковый запрос: '{test_query}'")
        if results:
            print("Пример найденного фрагмента:")
            print(results[0].page_content[:250].strip() + "...")
        else:
            print("Нет результатов поиска. Возможные причины:")
            print("- Статьи не содержат релевантного текста")
            print("- Эмбеддинги не были корректно сохранены")
            print("- Используется другая модель эмбеддингов при загрузке и сохранении")
    else:
        print("Предупреждение: нет чанков для индексации.")

    print("\nОбработка завершена. Векторная база данных готова к использованию.")


if __name__ == "__main__":
    main()