import os
import streamlit as st
from dotenv import load_dotenv
import database as db

load_dotenv()
db.init_db()

if "DEEPSEEK_API_KEY" in st.secrets:
    os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]

st.set_page_config(page_title="Юрист 44-ФЗ", page_icon="⚖️", layout="centered")

# НОВЫЙ CSS: Оставляем МЕНЮ, уменьшаем ЗАГОЛОВКИ
st.markdown("""
    <style>
    /* Скрываем только кнопку Deploy и лишнее меню справа, оставляем левую часть для бургера */
    .stAppDeployButton {display:none !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    
    /* Скрываем плашки внизу экрана (корону и тд) */
    .stAppToolbar {display:none !important;}
    [data-testid="stStatusWidget"] {display:none !important;}

    /* Компактные шрифты заголовков */
    h1 { font-size: 18px !important; margin-bottom: 0.5rem !important; }
    h2 { font-size: 16px !important; }
    h3 { font-size: 14px !important; }
    
    /* Общий шрифт текста 12px */
    .stChatMessage, .stMarkdown p, .stMarkdown td, .stMarkdown li { font-size: 12px !important; }
    
    /* Кнопки */
    .stButton button { width: 100%; border-radius: 6px; height: 2.8em; font-size: 12px !important; font-weight: bold; }
    
    /* Коррекция шапки для видимости меню */
    header { background: transparent !important; height: 3rem !important; }
    .block-container { padding-top: 1rem !important; }
    </style>
""", unsafe_allow_html=True)

# 1. АВТОРИЗАЦИЯ
if "user_id" not in st.session_state:
    st.title("⚖️ Вход")
    tg_id = st.text_input("Ваш ID:", placeholder="@username", key="login_id")
    if st.button("ВОЙТИ"):
        if tg_id:
            st.session_state.user_id = tg_id
            st.rerun()
    st.stop()

user_id = st.session_state.user_id

# 2. ПОДГОТОВКА ДАННЫХ В SIDEBAR (Три полоски будут вызывать это меню)
with st.sidebar:
    st.title(f"👤 {user_id}")
    if st.button("ВЫЙТИ"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
    
    st.markdown("---")
    st.subheader("Управление чатами")
    
    user_chats = db.get_user_chats(user_id)
    
    # Создание чата
    new_name = st.text_input("Название чата:", key="side_chat_input")
    if st.button("СОЗДАТЬ ЧАТ", key="side_create_btn"):
        if new_name:
            new_id = db.create_chat(user_id, new_name)
            if new_id:
                st.session_state.chat_id = new_id
                st.rerun()
    
    st.markdown("---")
    
    # ПЕРЕКЛЮЧЕНИЕ ЧАТОВ
    selected_chat_id = None
    if user_chats:
        chat_names = [c[1] for c in user_chats]
        chat_ids = [c[0] for c in user_chats]
        
        # Если чат еще не выбран, берем первый
        if "chat_id" not in st.session_state or st.session_state.chat_id not in chat_ids:
            st.session_state.chat_id = chat_ids[0]
            
        current_index = chat_ids.index(st.session_state.chat_id)
        pick = st.selectbox("Переключить чат:", options=chat_names, index=current_index)
        
        # Обновляем ID чата при выборе
        new_selected_id = chat_ids[chat_names.index(pick)]
        if new_selected_id != st.session_state.chat_id:
            st.session_state.chat_id = new_selected_id
            st.rerun()
            
        selected_chat_id = st.session_state.chat_id
        
        if st.button("УДАЛИТЬ ЧАТ"):
            db.delete_chat(st.session_state.chat_id)
            del st.session_state.chat_id
            st.rerun()

# 3. ЭКРАН ПРИВЕТСТВИЯ
if not selected_chat_id:
    st.title("👋 Привет!")
    st.write("Создайте первый чат, чтобы начать:")
    w_name = st.text_input("Название:", placeholder="Напр: Основной", key="w_input")
    if st.button("НАЧАТЬ", key="w_btn"):
        if w_name:
            res = db.create_chat(user_id, w_name)
            if res:
                st.session_state.chat_id = res
                st.rerun()
    st.stop()

# 4. РАБОЧИЙ ЭКРАН
current_chat_name = [c[1] for c in user_chats if c[0] == selected_chat_id][0]
st.title(f"💬 Чат: {current_chat_name}")

with st.sidebar:
    st.markdown("---")
    st.subheader("Документ (PDF)")
    temp_file = st.file_uploader("Загрузить для анализа", type="pdf", key=f"f_{selected_chat_id}")
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

# История
messages = db.get_chat_history(selected_chat_id)
for i, msg in enumerate(messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            st.download_button("📥 TXT", msg["content"], f"m_{i}.txt", key=f"dl_{selected_chat_id}_{i}")

if prompt := st.chat_input("Напишите ваш вопрос..."):
    with st.chat_message("user"): st.markdown(prompt)
    db.save_message(selected_chat_id, "user", prompt)
    
    with st.spinner("..."):
        engine = get_engine()
        response = engine.query(prompt, extra_context=temp_content) if engine else "Ошибка БД"
    
    with st.chat_message("assistant"): st.markdown(response)
    db.save_message(selected_chat_id, "assistant", response)
    st.rerun()
