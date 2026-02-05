import os
print("Importing streamlit...")
import streamlit as st
print("Importing dotenv...")
from dotenv import load_dotenv
print("Imports complete.")

# Load environment variables
load_dotenv()

# DeepSeek API Key from env or st.secrets (for cloud)
if "DEEPSEEK_API_KEY" in st.secrets:
    os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]

st.set_page_config(page_title="Ассистент Юриста 44-ФЗ", page_icon="⚖️", layout="centered")

# Мобильная оптимизация стилей
st.markdown("""
    <style>
    .stChatMessage { font-size: 16px !important; }
    .stButton button { width: 100%; border-radius: 10px; height: 3em; }
    [data-testid="stSidebar"] { width: 300px !important; }
    </style>
""", unsafe_allow_html=True)

st.title("⚖️ Ассистент Юриста 44-ФЗ")

st.markdown("""
Этот ассистент помогает отвечать на вопросы по 44-ФЗ и искать судебную практику.
""")

# Sidebar
with st.sidebar:
    st.header("Настройки")
    
    # File Uploader (Permanent)
    uploaded_file = st.file_uploader("Добавить в базу законов (PDF)", type="pdf")
    if uploaded_file is not None:
        if st.button("Загрузить навсегда"):
            with st.spinner("Обработка..."):
                try:
                    save_path = os.path.join("data", uploaded_file.name)
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    from data_ingest import ingest_data
                    ingest_data(save_path)
                    st.success(f"Файл {uploaded_file.name} добавлен в базу!")
                except Exception as e:
                    st.error(f"Ошибка: {e}")

    st.markdown("---")
    
    # File Uploader (Temporary Analysis)
    analysis_file = st.file_uploader("Анализ документа (без сохранения)", type="pdf")
    temp_content = None
    if analysis_file is not None:
        try:
            import pypdf
            reader = pypdf.PdfReader(analysis_file)
            temp_content = ""
            for page in reader.pages:
                temp_content += page.extract_text() + "\n"
            st.info("Документ для анализа подгружен. Теперь задайте вопрос.")
        except Exception as e:
            st.error(f"Не удалось прочитать PDF: {e}")

    if st.button("Очистить историю"):
        st.session_state.messages = []

# Chat Interface placeholder
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Оптимизированная загрузка движка
@st.cache_resource
def get_rag_engine():
    from rag_engine import RAGEngine
    return RAGEngine()

# Response logic
if prompt := st.chat_input("Ваш вопрос по 44-ФЗ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Думаю..."):
        try:
            engine = get_rag_engine()
            # Передаем temp_content (если он есть) в запрос
            response = engine.query(prompt, extra_context=temp_content)
            
            # Поиск практики, если нужно
            if any(word in prompt.lower() for word in ["практика", "суд", "решение", "поиск"]):
                st.info("Ищу судебную практику в Google и Yandex...")
                from search_tool import SearchTool
                searcher = SearchTool()
                practice_results = searcher.search_practice(prompt)
                response += f"\n\n---\n### Найдено в сети:\n{practice_results}"
                
        except Exception as e:
            response = f"Ошибка: {e}"

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
