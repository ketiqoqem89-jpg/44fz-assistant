import os
import streamlit as st
from dotenv import load_dotenv
import database as db

# Загрузка настроек и БД
load_dotenv()
db.init_db()

if "DEEPSEEK_API_KEY" in st.secrets:
    os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]

st.set_page_config(page_title="Юрист 44-ФЗ", page_icon="⚖️", layout="centered")

# CSS для скрытия брендинга (оставили только самое важное)
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

# 1. АВТОРИЗАЦИЯ
if "user_id" not in st.session_state:
    st.title("⚖️ Вход в систему")
    tg_id = st.text_input("Введите ваш ID:", placeholder="@username")
    if st.button("ВОЙТИ"):
        if tg_id:
            st.session_state.user_id = tg_id
            st.rerun()
        else:
            st.warning("Введите логин")
    st.stop()

user_id = st.session_state.user_id

# 2. ПОДГОТОВКА ДАННЫХ В SIDEBAR
with st.sidebar:
    st.header(f"👤 {user_id}")
    if st.button("ВЫЙТИ"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
    
    st.markdown("---")
    st.subheader("Мои чаты")
    
    user_chats = db.get_user_chats(user_id)
    
    # Поле создания чата всегда активно
    new_name = st.text_input("Название чата:", placeholder="Напр: Контракт 1", key="new_chat_input")
    if st.button("СОЗДАТЬ ЧАТ"):
        if new_name:
            res = db.create_chat(user_id, new_name)
            if res:
                st.session_state.chat_id = res
                st.rerun()
    
    st.markdown("---")
    
    selected_chat_id = None
    if user_chats:
        chat_names = [c[1] for c in user_chats]
        chat_ids = [c[0] for c in user_chats]
        
        # Запоминаем текущий выбор
        if "chat_id" not in st.session_state:
            st.session_state.chat_id = chat_ids[0]
            
        try:
            current_index = chat_ids.index(st.session_state.chat_id)
        except:
            current_index = 0
            
        pick = st.selectbox("Переключить чат:", options=chat_names, index=current_index)
        st.session_state.chat_id = chat_ids[chat_names.index(pick)]
        selected_chat_id = st.session_state.chat_id
        
        if st.button("УДАЛИТЬ ТЕКУЩИЙ ЧАТ"):
            db.delete_chat(st.session_state.chat_id)
            del st.session_state.chat_id
            st.rerun()

# 3. ОСНОВНОЙ ЭКРАН
if not selected_chat_id:
    st.title("👋 Добро пожаловать!")
    st.info("У вас пока нет активных чатов. Создайте новый чат в меню слева (кнопка `>`), чтобы начать работу.")
    st.stop()

# Если чат выбран, показываем интерфейс
current_chat_name = [c[1] for c in user_chats if c[0] == selected_chat_id][0]
st.title(f"💬 {current_chat_name}")

with st.sidebar:
    st.markdown("---")
    st.subheader("Файлы для анализа")
    temp_file = st.file_uploader("Загрузить PDF", type="pdf", key=f"f_{selected_chat_id}")
    temp_content = None
    if temp_file:
        import pypdf
        reader = pypdf.PdfReader(temp_file)
        temp_content = "".join([p.extract_text() + "\n" for p in reader.pages])

@st.cache_resource
def get_engine():
    try:
        from rag_engine import RAGEngine
        return RAGEngine()
    except: return None

# История сообщений
messages = db.get_chat_history(selected_chat_id)
for i, msg in enumerate(messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            st.download_button("📥 TXT", msg["content"], f"msg_{i}.txt", key=f"dl_{selected_chat_id}_{i}")

if prompt := st.chat_input("Спросите что-нибудь по 44-ФЗ..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    db.save_message(selected_chat_id, "user", prompt)
    
    with st.spinner("Думаю..."):
        engine = get_engine()
        response = engine.query(prompt, extra_context=temp_content) if engine else "Ошибка БД"
    
    with st.chat_message("assistant"):
        st.markdown(response)
    db.save_message(selected_chat_id, "assistant", response)
    st.rerun()
