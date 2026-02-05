import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Key check
if "DEEPSEEK_API_KEY" in st.secrets:
    os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]

st.set_page_config(page_title="Ассистент 44-ФЗ", page_icon="⚖️", layout="centered")

# Ensure data dir exists
if not os.path.exists("data"):
    os.makedirs("data")

# Скрытие брендинга и установка сверхкомпактного шрифта 12px
st.markdown("""
    <style>
    /* Скрываем лишее */
    header, footer, #MainMenu {visibility: hidden !important; display: none !important;}
    .stAppDeployButton {display:none !important;}
    [data-testid="stStatusWidget"] {display:none !important;}
    .stAppToolbar {display:none !important;}
    
    /* Ультра-компактные шрифты */
    .stChatMessage { font-size: 12px !important; }
    .stButton button { width: 100%; border-radius: 6px; height: 2.5em; font-size: 12px !important; }
    .stMarkdown p, .stMarkdown li { font-size: 12px !important; }
    
    /* Компактный отступ сверху */
    .block-container {padding-top: 1rem !important;}
    </style>
""", unsafe_allow_html=True)

st.title("⚖️ Ассистент 44-ФЗ")

# --- БОКОВОЕ МЕНЮ (SIDEBAR) ---
with st.sidebar:
    st.header("🗂 Файлы и настройки")
    
    # Режим базы
    st.subheader("База знаний")
    perm_file = st.file_uploader("Добавить закон (PDF)", type="pdf", key="perm")
    if perm_file and st.button("СОХРАНИТЬ В БАЗУ"):
        with st.spinner("Загрузка..."):
            try:
                save_path = os.path.join("data", perm_file.name)
                with open(save_path, "wb") as f:
                    f.write(perm_file.getbuffer())
                import data_ingest
                data_ingest.ingest_data(save_path)
                st.success("Готово.")
            except Exception as e:
                st.error(f"Ошибка: {e}")

    st.markdown("---")
    
    # Режим анализа
    st.subheader("Анализ проекта")
    temp_file = st.file_uploader("Проверить документ (PDF)", type="pdf", key="temp")
    temp_content = None
    if temp_file:
        try:
            import pypdf
            reader = pypdf.PdfReader(temp_file)
            temp_content = "".join([p.extract_text() + "\n" for p in reader.pages])
            st.info("✅ Документ подгружен.")
        except Exception as e:
            st.error(f"Ошибка: {e}")

    st.markdown("---")
    if st.button("ОЧИСТИТЬ ЧАТ"):
        st.session_state.messages = []
        st.rerun()

# --- ЛОГИКА ЧАТА ---
@st.cache_resource
def get_rag_engine():
    try:
        from rag_engine import RAGEngine
        return RAGEngine()
    except Exception as e:
        st.error(f"Ошибка системы: {e}")
        return None

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
            if engine:
                response = engine.query(prompt, extra_context=temp_content)
            else:
                response = "Ошибка инициализации."
        except Exception as e:
            response = f"Ошибка: {e}"

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
