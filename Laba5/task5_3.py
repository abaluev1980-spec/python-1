import os
from pathlib import Path
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# === Пути относительно скрипта ===
SCRIPT_DIR = Path(__file__).parent.resolve()
CHROMA_DIR = SCRIPT_DIR / "chroma_db"


class PermiaRAGSystem:
    def __init__(self, llm_model: str = "llama3.2", vectorstore_dir: str = None):
        if vectorstore_dir is None:
            vectorstore_dir = CHROMA_DIR

        self.llm = Ollama(model=llm_model)
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.vectorstore = Chroma(
            persist_directory=str(vectorstore_dir),
            embedding_function=self.embeddings
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})

        # Промпт с инструкцией использовать ТОЛЬКО контекст
        template = """
Вы — эксперт по истории Земли. Используйте ТОЛЬКО информацию из предоставленного контекста, чтобы ответить на вопрос.
Если ответ не содержится в контексте, напишите: «Эта информация не доступна в предоставленных документах».

Контекст:
{context}

Вопрос:
{question}

Ответ:
"""
        self.prompt = PromptTemplate.from_template(template)

        # RAG-цепочка без сложных компонентов
        self.rag_chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def answer_question(self, question: str) -> dict:
        try:
            answer_text = self.rag_chain.invoke(question)

            # Получаем источники (документы, использованные в контексте)
            docs = self.retriever.invoke(question)
            sources = []
            for doc in docs:
                sources.append({
                    "source": doc.metadata.get("source", "Неизвестно"),
                    "content_preview": doc.page_content[:400] + "..."
                })

            return {
                "question": question,
                "answer": answer_text,
                "sources": sources
            }
        except Exception as e:
            return {
                "question": question,
                "answer": f"Ошибка: {str(e)}",
                "sources": []
            }


def main():
    print("=== Задание 3: RAG-система для вопросов о Пермском периоде ===")

    # Проверка существования векторной базы
    if not (CHROMA_DIR / "chroma.sqlite3").exists():
        print(f"Ошибка: векторная база не найдена в {CHROMA_DIR}")
        print("Сначала выполните Задание 2 (task5_2.py), чтобы создать chroma_db.")
        return

    rag = PermiaRAGSystem(llm_model="llama3.2")

    questions = [
        "Что такое Пермский период?",
        "Какие животные жили в Пермском периоде?",
        "Почему произошло Пермское вымирание?",
        "Какие климатические условия были в Пермском периоде?"
    ]

    results = []
    for i, q in enumerate(questions, 1):
        print(f"\n--- Вопрос {i}: {q} ---")
        res = rag.answer_question(q)
        results.append(res)

        print("Ответ:")
        print(res["answer"])
        print("\nИсточники:")
        for j, src in enumerate(res["sources"], 1):
            print(f"  {j}. {src['source']}")
            print(f"     {src['content_preview']}")

    # Сохранение в файл
    output_file = SCRIPT_DIR / "rag_results.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        for r in results:
            f.write(f"Вопрос: {r['question']}\n")
            f.write(f"Ответ: {r['answer']}\n")
            f.write("Источники:\n")
            for src in r["sources"]:
                f.write(f"  - {src['source']}\n")
            f.write("\n" + "="*60 + "\n")

    print(f"\n✅ Результаты сохранены в: {output_file}")


if __name__ == "__main__":
    main()