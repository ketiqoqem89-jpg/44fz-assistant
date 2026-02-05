import os
import streamlit as st
from dotenv import load_dotenv
import database as db

load_dotenv()
db.init_db()

if "DEEPSEEK_API_KEY" in st.secrets:
    os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]

st.set_page_config(page_title="Юрист 44-ФЗ", page_icon="⚖️", layout="centered")

# --- СТИЛИЗАЦИЯ ПОД DEEPSEEK MOBILE ---
st.markdown("""
<style>
    /* Главный фон и шрифт */
    .stApp {
        background-color: #0A0A0A !important;
        color: #FFFFFF !important;
    }
    
    /* Скрываем всё лишнее */
    header, footer, .stAppDeployButton, [data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* Верхняя панель навигации */
    .custom-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 20px;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: #0A0A0A;
        z-index: 1000;
        border-bottom: 1px solid #1A1A1A;
    }
    .header-text { font-size: 14px; font-weight: 500; }

    /* Центральный логотип и текст */
    .hero-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 60vh;
        text-align: center;
    }
    .whale-logo {
        width: 80px;
        height: 80px;
        background: url('https://chat.deepseek.com/favicon.svg') no-repeat center;
        background-size: contain;
        margin-bottom: 20px;
        filter: drop-shadow(0 0 10px #4081FF);
    }
    .hero-title { font-size: 20px; font-weight: 600; color: #FFFFFF; }

    /* Поле ввода (плавающее снизу) */
    .stChatInput {
        bottom: 30px !important;
        max-width: 90% !important;
    }
    .stChatInput textarea {
        background-color: #1A1A1A !important;
        border: 1px solid #2A2A2A !important;
        border-radius: 20px !important;
        color: #FFFFFF !important;
        padding: 15px !important;
    }

    /* Кнопки "Рассуждение" и "Поиск" */
    .input-tools {
        display: flex;
        gap: 8px;
        position: fixed;
        bottom: 95px;
        left: 25px;
        z-index: 1001;
    }
    .tool-btn {
        background: #131A2A;
        border: 1px solid #1E2D4A;
        color: #4081FF;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 11px;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .tool-btn.search {
        background: #1A1A1A;
        border: 1px solid #2A2A2A;
        color: #FFFFFF;
    }

    /* Облачка чата */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 10px 0 !important;
    }
    .stChatMessage.user { text-align: right; }
    
    /* Контейнер для контента */
    .block-container { padding-top: 4rem !important; max-width: 650px !important; }
</style>
""", unsafe_allow_html=True)

# 1. АВТОРИЗАЦИЯ
if "user_id" not in st.session_state:
    st.markdown('<div style="display:flex; flex-direction:column; align-items:center; margin-top:10vh;">', unsafe_allow_html=True)
    st.markdown("<div class='whale-logo'></div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-title'>Вход в систему</div><br>", unsafe_allow_html=True)
    tg_id = st.text_input("ID:", placeholder="@username", label_visibility="collapsed")
    if st.button("ВОЙТИ"):
        if tg_id:
            st.session_state.user_id = tg_id
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

user_id = st.session_state.user_id

# 2. ШАПКА В СТИЛЕ DEEPSEEK
st.markdown(f"""
    <div class="custom-header">
        <div style="font-size: 20px;">☰</div>
        <div class="header-text">Новый чат</div>
        <div style="font-size: 20px;" onclick="window.location.reload();">⊕</div>
    </div>
""", unsafe_allow_html=True)

# 3. SIDEBAR (Скрытый, вызывается через меню)
with st.sidebar:
    st.markdown(f"**👤 {user_id}**")
    if st.button("ВЫЙТИ"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
    st.markdown("---")
    user_chats = db.get_user_chats(user_id)
    if user_chats:
        c_names = [c[1] for c in user_chats]
        c_ids = [c[0] for c in user_chats]
        if "chat_id" not in st.session_state or st.session_state.chat_id not in c_ids:
            st.session_state.chat_id = c_ids[0]
        pick = st.selectbox("Ваши чаты:", options=c_names, index=c_ids.index(st.session_state.chat_id))
        st.session_state.chat_id = c_ids[c_names.index(pick)]
        selected_chat_id = st.session_state.chat_id
    else: selected_chat_id = None

# Инициализируем выбранный чат
if not selected_chat_id:
    # Автосоздание первого чата как в DeepSeek
    selected_chat_id = db.create_chat(user_id, "Новый чат")
    st.session_state.chat_id = selected_chat_id

# 4. ОСНОВНОЙ ЭКРАН
messages = db.get_chat_history(selected_chat_id)

if not messages:
    # Состояние "Пустой чат" (как на скриншоте)
    st.markdown("""
        <div class="hero-container">
            <div class="whale-logo"></div>
            <div class="hero-title">Чем могу помочь?</div>
        </div>
    """, unsafe_allow_html=True)
else:
    # Вывод истории
    for i, msg in enumerate(messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 5. ИНСТРУМЕНТЫ ВВОДА (Рассуждение, Поиск)
st.markdown("""
    <div class="input-tools">
        <div class="tool-btn">⚛ Рассуждение</div>
        <div class="tool-btn search">🌐 Поиск</div>
    </div>
""", unsafe_allow_html=True)

# 6. ВВОД
if prompt := st.chat_input("Напишите или удерживайте, чтобы говорить"):
    with st.chat_message("user"): st.markdown(prompt)
    db.save_message(selected_chat_id, "user", prompt)
    
    with st.spinner(""):
        try:
            from rag_engine import RAGEngine
            engine = RAGEngine()
            response = engine.query(prompt)
        except: response = "Ошибка анализа."
    
    with st.chat_message("assistant"): st.markdown(response)
    db.save_message(selected_chat_id, "assistant", response)
    st.rerun()


