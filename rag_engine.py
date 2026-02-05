import os
from datetime import datetime
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class RAGEngine:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(self.base_dir, "data", "chroma_db")
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        
        if os.path.exists(self.db_path):
            self.vector_db = Chroma(persist_directory=self.db_path, embedding_function=self.embeddings)
            self.retriever = self.vector_db.as_retriever(search_kwargs={"k": 20})
        else:
            self.vector_db = None
            self.retriever = None

        api_key = os.getenv("DEEPSEEK_API_KEY")
        self.llm = ChatOpenAI(
            model="deepseek-chat", 
            temperature=0,
            base_url="https://api.deepseek.com",
            api_key=api_key
        )

    def query(self, question, extra_context=None):
        if not self.vector_db:
            return "База знаний не найдена."
        
        try:
            today = datetime.now().strftime("%d.%m.%Y")
            search_query = question
            if "приемк" in question.lower():
                search_query = f"{question} Статья 94 приемка сроки"
            
            docs = self.retriever.invoke(search_query)
            
            context_parts = []
            for doc in docs:
                context_parts.append(f"Закон (Источник: {doc.metadata.get('source', 'unknown')}):\n{doc.page_content}")
            
            laws_context = "\n\n".join(context_parts)
            
            work_doc_section = ""
            if extra_context:
                work_doc_section = f"\n=== РАБОЧИЙ ДОКУМЕНТ ПОЛЬЗОВАТЕЛЯ ДЛЯ АНАЛИЗА ===\n{extra_context}\n"

            template = """Вы — эксперт-юрист по 44-ФЗ. Сегодня: {today}.
            РЕЖИМ: Absolute Mode. Исключить эмодзи и вежливость.
            
            ДОПОЛНИТЕЛЬНЫЕ ИНСТРУКЦИИ:
            1. ТАБЛИЦА РИСКОВ: Если прислан 'РАБОЧИЙ ДОКУМЕНТ', начни ответ с Markdown-таблицы: 
               | Пункт договора | Статья 44-ФЗ | Оценка (ОК/Нарушение/Риск) | Комментарий |
            2. КАЛЬКУЛЯТОР СРОКОВ: Если в законе указан срок (напр. 5 дней), рассчитай дату от сегодня ({today}) и укажи её в скобках. Различай рабочие и календарные дни.
            3. ЦИТИРОВАНИЕ: Ссылка на статью обязательна.

            ТЕКУЩИЙ КОНТЕКСТ ЗАКОНОДАТЕЛЬСТВА:
            {laws_context}
            {work_doc_section}
            
            Вопрос: {question}
            Ответ:"""
            
            chain = ChatPromptTemplate.from_template(template) | self.llm | StrOutputParser()
            return chain.invoke({
                "today": today,
                "laws_context": laws_context, 
                "work_doc_section": work_doc_section,
                "question": question
            })
        except Exception as e:
            return f"Ошибка: {e}"
