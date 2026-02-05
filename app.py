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

# ОБНОВЛЕННЫЙ CSS: Чистка интерфейса и центрирование
st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']} !important; color: {t['text']} !important; }}
    .block-container {{ max-width: 690px !important; padding-top: 2rem !important; }}
    
    /* Скрываем ВЕСЬ мусор (Deploy, Footer, Status Bar) */
    .stAppDeployButton, footer, .stAppToolbar, [data-testid="stStatusWidget"], [data-testid="stDecoration"] {{ 
        display: none !important; 
        visibility: hidden !important; 
    }}
    
    /* Шрифты и заголовки */
    h1, h2, h3 {{ 
        font-size: 14px !important; 
        font-weight: bold !important; 
        color: {t['text']} !important;
        margin-bottom: 10px !important;
    }}
    .stChatMessage {{ background-color: {t['chat_bg']} !important; font-size: 12px !important; border-radius: 10px !important; }}
    .stMarkdown p, .stMarkdown td, .stMarkdown li {{ font-size: 12px !important; color: {t['text']} !important; }}
    
    /* ФОРМА ВХОДА */
    .login-container {{
        display: flex; flex-direction: column; align-items: center;
        margin-top: 10vh; text-align: center;
    }}
    .login-box {{ width: 100%; max-width: 300px; }}
    
    /* Кнопки и инпуты */
    .stButton button {{ width: 100%; border-radius: 6px; height: 2.2em; font-size: 11px !important; font-weight: bold !important; }}
    .stTextInput input {{ font-size: 12px !important; height: 2.2em !important; }}
    
    /* Уплотнение отступов */
    [data-testid="stVerticalBlock"] {{ gap: 0.4rem !important; }}
    </style>
""", unsafe_allow_html=True)

# 1. АВТОРИЗАЦИЯ
if "user_id" not in st.session_state:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("### ⚖️ Вход в систему")
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
    selected_theme = st.selectbox("Тема оформления:", options=list(themes.keys()), 
                                          index=list(themes.keys()).index(st.session_state.theme))
    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.rerun()
    
    if st.button("ВЫЙТИ"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
    
    st.markdown("---")
    st.markdown("**Мои чаты**")
    user_chats = db.get_user_chats(user_id)
    
    new_name = st.text_input("Название чата:", key="side_in", label_visibility="collapsed", placeholder="Новый чат...")
    if st.button("СОЗДАТЬ ЧАТ"):
        if new_name:
            nid = db.create_chat(user_id, new_name)
            if nid:
                st.session_state.chat_id = nid
                st.rerun()
    
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
        
        if st.button("УДАЛИТЬ ЧАТ"):
            db.delete_chat(selected_chat_id)
            del st.session_state.chat_id
            st.rerun()
    else: selected_chat_id = None

# ... (ОСТАЛЬНОЙ КОД ЧАТА БЕЗ ИЗМЕНЕНИЙ) ...
# (Скопируйте блоки чата и выгрузки файлов из прошлой версии)
if selected_chat_id:
    current_chat_name = [c[1] for c in user_chats if c[0] == selected_chat_id][0]
    st.markdown(f"### 💬 {current_chat_name}")
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("**Анализ PDF**")
        temp_file = st.file_uploader("Загрузить:", type="pdf", key=f"f_{selected_chat_id}", label_visibility="collapsed")
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

    messages = db.get_chat_history(selected_chat_id)
    for i, msg in enumerate(messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                st.download_button("📥 TXT", msg["content"], f"msg_{i}.txt", key=f"dl_{i}")

    if prompt := st.chat_input("Вопрос по 44-ФЗ..."):
        with st.chat_message("user"): st.markdown(prompt)
        db.save_message(selected_chat_id, "user", prompt)
        with st.spinner("..."):
            engine = get_engine()
            response = engine.query(prompt, extra_context=temp_content) if engine else "Ошибка"
        with st.chat_message("assistant"): st.markdown(response)
        db.save_message(selected_chat_id, "assistant", response)
        st.rerun()
else:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("### 👋 Начнем?")
    w_name = st.text_input("Имя первого чата:", placeholder="Напр: Общий", key="w_in")
    if st.button("НАЧАТЬ"):
        if w_name:
            res = db.create_chat(user_id, w_name)
            if res:
                st.session_state.chat_id = res
                st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

