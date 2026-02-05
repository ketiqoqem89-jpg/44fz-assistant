import os
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class RAGEngine:
    def __init__(self):
        self.db_path = "./data/chroma_db"
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        
        if os.path.exists(self.db_path):
            self.vector_db = Chroma(persist_directory=self.db_path, embedding_function=self.embeddings)
            # Берем еще больше фрагментов - 20 штук
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
            print(f"--- Поиск: {question} ---")
            
            search_query = question
            if "приемк" in question.lower():
                search_query = f"{question} Статья 94 приемка сроки"
            
            docs = self.retriever.invoke(search_query)
            
            context_parts = []
            for i, doc in enumerate(docs, 1):
                context_parts.append(f"Закон (Источник: {doc.metadata.get('source', 'unknown')}):\n{doc.page_content}")
            
            laws_context = "\n\n".join(context_parts)
            
            # Если есть рабочий документ - добавляем его отдельно
            work_doc_section = ""
            if extra_context:
                work_doc_section = f"\n=== РАБОЧИЙ ДОКУМЕНТ ПОЛЬЗОВАТЕЛЯ (для анализа) ===\n{extra_context}\n"

            print("--- Анализ в DeepSeek (Absolute Mode) ---")
            template = """Вы — эксперт-юрист по 44-ФЗ. 
            РЕЖИМ: Absolute Mode. Исключить эмодзи, вводные слова, вежливость, предложения помощи и любые переходные фразы. 
            Стиль: предельно сухой, директивный, фактический. Никаких вопросов в конце. Завершать ответ немедленно после изложения сути.
            Ответ на русском языке.

            ТЕКУЩИЙ КОНТЕКСТ ЗАКОНОДАТЕЛЬСТВА:
            {laws_context}
            {work_doc_section}
            
            ЗАДАЧА: Ответь на вопрос на основе контекста. Если прислан 'РАБОЧИЙ ДОКУМЕНТ', проанализируй его на соответствие 'КОНТЕКСТУ ЗАКОНОДАТЕЛЬСТВА'.
            
            Вопрос: {question}
            Ответ:"""
            
            chain = ChatPromptTemplate.from_template(template) | self.llm | StrOutputParser()
            return chain.invoke({
                "laws_context": laws_context, 
                "work_doc_section": work_doc_section,
                "question": question
            })
        except Exception as e:
            print(f"ОШИБКА: {e}")
            return f"Ошибка: {e}"
