import os
import streamlit as st
from dotenv import load_dotenv
import database as db

# Load environment variables and initialize database
load_dotenv()
db.init_db()

# API Key for cloud/local
if "DEEPSEEK_API_KEY" in st.secrets:
    os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]

st.set_page_config(page_title="Юрист 44-ФЗ", page_icon="⚖️", layout="centered")

# --- ЛОГИКА ТЕМ ОФОРМЛЕНИЯ ---
if "theme" not in st.session_state:
    st.session_state.theme = "Темная"

themes = {
    "Темная": {"bg": "#0E1117", "text": "#FFFFFF", "chat_bg": "#161B22"},
    "Светлая": {"bg": "#FFFFFF", "text": "#000000", "chat_bg": "#F0F2F6"},
    "Синяя": {"bg": "#0A192F", "text": "#E6F1FF", "chat_bg": "#172A45"}
}
t = themes[st.session_state.theme]

# ОБНОВЛЕННЫЙ CSS С КОМПАКТНОСТЬЮ И ТЕМАМИ
st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']} !important; color: {t['text']} !important; }}
    .block-container {{ max-width: 690px !important; padding-top: 1rem !important; }}
    
    /* Шрифты и заголовки */
    h1, h2, h3, .login-title {{ 
        font-size: 14px !important; 
        font-weight: bold !important; 
        color: {t['text']} !important;
        margin-bottom: 5px !important;
    }}
    .stChatMessage {{ background-color: {t['chat_bg']} !important; font-size: 12px !important; border-radius: 10px !important; }}
    .stMarkdown p, .stMarkdown td, .stMarkdown li {{ font-size: 12px !important; color: {t['text']} !important; }}
    
    /* ФОРМА ВХОДА (Поднята вверх) */
    .login-container {{
        display: flex; flex-direction: column; align-items: center;
        margin-top: 5vh; text-align: center;
    }}
    .login-box {{ width: 100%; max-width: 300px; }}
    
    /* Кнопки и инпуты */
    .stButton button {{ width: 100%; border-radius: 6px; height: 2.2em; font-size: 11px !important; font-weight: bold !important; }}
    .stTextInput input {{ font-size: 12px !important; height: 2.2em !important; }}
    
    /* Уплотнение отступов */
    [data-testid="stVerticalBlock"] {{ gap: 0.3rem !important; }}
    div[data-testid="stVerticalBlock"] > div {{ margin-bottom: -3px !important; }}
    
    /* Скрытие лишнего */
    .stAppDeployButton {{ display: none !important; }}
    footer {{ visibility: hidden !important; }}
    </style>
""", unsafe_allow_html=True)

# 1. АВТОРИЗАЦИЯ
if "user_id" not in st.session_state:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="login-title">⚖️ Вход в систему</div>', unsafe_allow_html=True)
    tg_id = st.text_input("ID:", placeholder="@username", label_visibility="collapsed")
    if st.button("ВОЙТИ"):
        if tg_id:
            st.session_state.user_id = tg_id
            st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

user_id = st.session_state.user_id

# 2. SIDEBAR (Навигация и Настройки)
with st.sidebar:
    st.markdown(f"**👤 {user_id}**")
    
    # Смена фона
    st.session_state.theme = st.selectbox("Тема оформления:", options=list(themes.keys()), 
                                          index=list(themes.keys()).index(st.session_state.theme))
    
    if st.button("ВЫЙТИ"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
    
    st.markdown("---")
    st.markdown("**Мои чаты**")
    user_chats = db.get_user_chats(user_id)
    
    # Создание чата
    new_name = st.text_input("Название чата:", key="side_in", label_visibility="collapsed", placeholder="Название...")
    if st.button("СОЗДАТЬ ЧАТ"):
        if new_name:
            nid = db.create_chat(user_id, new_name)
            if nid:
                st.session_state.chat_id = nid
                st.rerun()
    
    # Список чатов
    if user_chats:
        st.markdown("---")
        c_names = [c[1] for c in user_chats]
        c_ids = [c[0] for c in user_chats]
        
        if "chat_id" not in st.session_state or st.session_state.chat_id not in c_ids:
            st.session_state.chat_id = c_ids[0]
        
        cur_idx = c_ids.index(st.session_state.chat_id)
        pick = st.selectbox("Переключить чат:", options=c_names, index=cur_idx, label_visibility="collapsed")
        st.session_state.chat_id = c_ids[c_names.index(pick)]
        selected_chat_id = st.session_state.chat_id
        
        if st.button("УДАЛИТЬ ТЕКУЩИЙ ЧАТ"):
            db.delete_chat(selected_chat_id)
            del st.session_state.chat_id
            st.rerun()
    else: selected_chat_id = None

# 3. ЭКРАН ПРИВЕТСТВИЯ (если нет чатов)
if not selected_chat_id:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("### 👋 Начнем?")
    w_name = st.text_input("Назовите первый чат:", placeholder="Напр: Общий чат", key="welcome_in")
    if st.button("СОЗДАТЬ И НАЧАТЬ"):
        if w_name:
            res = db.create_chat(user_id, w_name)
            if res:
                st.session_state.chat_id = res
                st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# 4. ОСНОВНОЙ РАБОЧИЙ ЭКРАН
current_chat_name = [c[1] for c in user_chats if c[0] == selected_chat_id][0]
st.markdown(f"### 💬 {current_chat_name}")

with st.sidebar:
    st.markdown("---")
    st.markdown("**Анализ PDF (Проект)**")
    temp_file = st.file_uploader("Загрузить файл:", type="pdf", key=f"f_{selected_chat_id}", label_visibility="collapsed")
    temp_content = None
    if temp_file:
        try:
            import pypdf
            reader = pypdf.PdfReader(temp_file)
            temp_content = "".join([p.extract_text() + "\n" for p in reader.pages])
            st.success("Документ загружен")
        except: st.error("Ошибка чтения PDF")

# ENGINE LOADING
@st.cache_resource
def get_engine():
    try:
        from rag_engine import RAGEngine
        return RAGEngine()
    except: return None

# ОТОБРАЖЕНИЕ СООБЩЕНИЙ
messages = db.get_chat_history(selected_chat_id)
for i, msg in enumerate(messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            st.download_button("📥 Скачать ответ", msg["content"], f"otvet_{selected_chat_id}_{i}.txt", key=f"dl_{i}")

# ВВОД ВОПРОСА
if prompt := st.chat_input("Спросите эксперта по 44-ФЗ..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    db.save_message(selected_chat_id, "user", prompt)
    
    with st.spinner("Анализирую..."):
        engine = get_engine()
        if engine:
            response = engine.query(prompt, extra_context=temp_content)
        else:
            response = "Загрузка системы... Пожалуйста, подождите или проверьте DEEPSEEK_API_KEY."
    
    with st.chat_message("assistant"):
        st.markdown(response)
    db.save_message(selected_chat_id, "assistant", response)
    st.rerun()

