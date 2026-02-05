import os
import streamlit as st
from dotenv import load_dotenv
import database as db

# Load environment variables
load_dotenv()
db.init_db()

# API Key check
if "DEEPSEEK_API_KEY" in st.secrets:
    os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]

st.set_page_config(page_title="Юрист 44-ФЗ", page_icon="⚖️", layout="centered")

# CSS для скрытия брендинга и настройки шрифтов
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden !important; display: none !important;}
    .stAppDeployButton {display:none !important;}
    .stChatMessage { font-size: 12px !important; }
    .stButton button { width: 100%; border-radius: 6px; height: 2.5em; font-size: 12px !important; }
    .stMarkdown p, .stMarkdown td { font-size: 11px !important; }
    .block-container {padding-top: 1rem !important;}
    </style>
""", unsafe_allow_html=True)

# --- АВТОРИЗАЦИЯ ---
if "user_id" not in st.session_state:
    st.title("⚖️ Вход в систему")
    tg_id = st.text_input("Введите ваш Telegram ID или Никнейм:", placeholder="@username")
    if st.button("ВОЙТИ"):
        if tg_id:
            st.session_state.user_id = tg_id
            st.rerun()
        else:
            st.warning("Введите ID")
    st.stop()

user_id = st.session_state.user_id

# --- УПРАВЛЕНИЕ ЧАТАМИ В SIDEBAR ---
with st.sidebar:
    st.header(f"� {user_id}")
    if st.button("СМЕНИТЬ АККАУНТ"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
    
    st.markdown("---")
    st.subheader("Мои чаты (до 10)")
    
    # Загрузка списка чатов
    user_chats = db.get_user_chats(user_id)
    
    # Создание нового чата
    new_chat_name = st.text_input("Новый чат:", placeholder="Напр: Приемка работ", key="new_chat_name")
    if st.button("СОЗДАТЬ ЧАТ"):
        if new_chat_name:
            res = db.create_chat(user_id, new_chat_name)
            if res:
                st.session_state.chat_id = res
                st.success("Чат создан")
                st.rerun()
            else:
                st.error("Лимит 10 чатов")
    
    st.markdown("---")
    
    # Выбор чата
    if user_chats:
        chat_options = {name: cid for cid, name in user_chats}
        selected_chat_name = st.selectbox("Выберите чат:", options=list(chat_options.keys()), index=0)
        st.session_state.chat_id = chat_options[selected_chat_name]
        
        if st.button("УДАЛИТЬ ТЕКУЩИЙ ЧАТ"):
            db.delete_chat(st.session_state.chat_id)
            del st.session_state.chat_id
            st.rerun()
    else:
        st.info("Создайте первый чат")
        st.stop()

# --- ОСНОВНОЙ ИНТЕРФЕЙС ТЕКУЩЕГО ЧАТА ---
chat_id = st.session_state.chat_id
st.title(f"💬 Чат: {selected_chat_name}")

# Боковая панель - Файлы (в контексте текущего чата)
with st.sidebar:
    st.markdown("---")
    st.subheader("Файлы для чата")
    temp_file = st.file_uploader("Документ (PDF)", type="pdf", key=f"file_{chat_id}")
    temp_content = None
    if temp_file:
        try:
            import pypdf
            reader = pypdf.PdfReader(temp_file)
            temp_content = "".join([p.extract_text() + "\n" for p in reader.pages])
            st.info("✅ Документ готов")
        except: st.error("Ошибка PDF")

# --- ЛОГИКА ЧАТА ---
@st.cache_resource
def get_rag_engine():
    try:
        from rag_engine import RAGEngine
        return RAGEngine()
    except: return None

# Загрузка истории конкретного чата
messages = db.get_chat_history(chat_id)

for i, msg in enumerate(messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            st.download_button("📥 TXT", msg["content"], f"chat_{chat_id}_msg_{i}.txt", key=f"dl_{chat_id}_{i}")

if prompt := st.chat_input("Вопрос..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    db.save_message(chat_id, "user", prompt)
    
    with st.spinner("Анализ..."):
        engine = get_rag_engine()
        response = engine.query(prompt, extra_context=temp_content) if engine else "Ошибка ОИ"
    
    with st.chat_message("assistant"):
        st.markdown(response)
    db.save_message(chat_id, "assistant", response)
    st.rerun()
