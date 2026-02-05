import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Key for cloud
if "DEEPSEEK_API_KEY" in st.secrets:
    os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]

st.set_page_config(page_title="Ассистент 44-ФЗ", page_icon="⚖️", layout="centered")

# Ensure data dir exists
if not os.path.exists("data"):
    os.makedirs("data")

# Агрессивное скрытие брендинга Streamlit
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    .reportview-container .main footer {display:none;}
    .stChatMessage { font-size: 16px !important; }
    .stButton button { width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("⚖️ Ассистент 44-ФЗ")

# Sidebar - Кнопки загрузки файлов (на телефоне нажать на > слева вверху)
with st.sidebar:
    st.header("🗂 Работа с файлами")
    
    # 1. Постоянная база
    st.subheader("База знаний")
    uploaded_file = st.file_uploader("Добавить закон навсегда (PDF)", type="pdf", key="perm")
    if uploaded_file is not None:
        if st.button("СОХРАНИТЬ В БАЗУ"):
            with st.spinner("Загрузка..."):
                try:
                    save_path = os.path.join("data", uploaded_file.name)
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    from data_ingest import ingest_data
                    ingest_data(save_path)
                    st.success("Готово! Файл в базе.")
                except Exception as e:
                    st.error(f"Ошибка: {e}")

    st.markdown("---")
    
    # 2. Временный анализ
    st.subheader("Анализ документа")
    analysis_file = st.file_uploader("Проверить текущий проект (PDF)", type="pdf", key="temp")
    temp_content = None
    if analysis_file is not None:
        try:
            import pypdf
            reader = pypdf.PdfReader(analysis_file)
            temp_content = "".join([p.extract_text() + "\n" for p in reader.pages])
            st.info("✅ Документ подгружен. Задайте вопрос в чате.")
        except Exception as e:
            st.error(f"Ошибка: {e}")

    st.markdown("---")
    if st.button("ОЧИСТИТЬ ЧАТ"):
        st.session_state.messages = []
        st.rerun()

# Engine loading
@st.cache_resource
def get_rag_engine():
    import rag_engine
    return rag_engine.RAGEngine()

# Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Напишите ваш вопрос..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Анализирую..."):
        try:
            engine = get_rag_engine()
            response = engine.query(prompt, extra_context=temp_content)
        except Exception as e:
            response = f"Ошибка связи с базой: {e}"

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
