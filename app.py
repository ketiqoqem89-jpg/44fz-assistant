import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Key for cloud
if "DEEPSEEK_API_KEY" in st.secrets:
    os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]

st.set_page_config(page_title="Ассистент 44-ФЗ", page_icon="⚖️", layout="centered")

# Hide Streamlit UI branding
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stChatMessage { font-size: 16px !important; }
    .stButton button { width: 100%; border-radius: 10px; height: 3em; }
    </style>
""", unsafe_allow_html=True)

st.title("⚖️ Ассистент 44-ФЗ")

# Sidebar
with st.sidebar:
    st.header("Настройки")
    
    # Permanent storage
    uploaded_file = st.file_uploader("Добавить в базу (PDF)", type="pdf")
    if uploaded_file is not None:
        if st.button("Загрузить навсегда"):
            with st.spinner("Загрузка..."):
                try:
                    save_path = os.path.join("data", uploaded_file.name)
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    from data_ingest import ingest_data
                    ingest_data(save_path)
                    st.success("Файл добавлен.")
                except Exception as e:
                    st.error(f"Ошибка: {e}")

    st.markdown("---")
    
    # Temporary analysis
    analysis_file = st.file_uploader("Анализ документа (PDF)", type="pdf")
    temp_content = None
    if analysis_file is not None:
        try:
            import pypdf
            reader = pypdf.PdfReader(analysis_file)
            temp_content = "".join([p.extract_text() + "\n" for p in reader.pages])
            st.info("Документ готов к анализу.")
        except Exception as e:
            st.error(f"Ошибка чтения: {e}")

    if st.button("Очистить историю"):
        st.session_state.messages = []

# Engine loading
@st.cache_resource
def get_rag_engine():
    from rag_engine import RAGEngine
    return RAGEngine()

# Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Вопрос..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Анализ..."):
        try:
            engine = get_rag_engine()
            response = engine.query(prompt, extra_context=temp_content)
        except Exception as e:
            response = f"Ошибка: {e}"

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
