import os
import streamlit as st
from dotenv import load_dotenv
import database as db
load_dotenv()
db.init_db()
if "DEEPSEEK_API_KEY" in st.secrets:
    os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]
st.set_page_config(page_title="Юрист 44-ФЗ", page_icon="⚖️", layout="centered")
# --- СТИЛИЗАЦИЯ: DEEPSEEK + РАБОЧАЯ ВЕРХНЯЯ ПЛАНКА ---
st.markdown("""
<style>
    /* ГЛАВНЫЙ ФОН И ТЕКСТ */
    .stApp {
        background-color: #0A0A0A !important;
        color: #FFFFFF !important;
    }
    
    /* СКРЫВАЕМ ТОЛЬКО МУСОР, ОСТАВЛЯЕМ HEADER */
    .stAppDeployButton, footer, [data-testid="stStatusWidget"], [data-testid="stDecoration"] {
        display: none !important;
    }
    /* Настройка стандартной плашки (Header) */
    header[data-testid="stHeader"] {
        background-color: #0A0A0A !important;
        border-bottom: 1px solid #1A1A1A !important;
        visibility: visible !important;
    }
    
    /* Делаем иконки в шапке белыми */
    header[data-testid="stHeader"] button {
        color: white !important;
    }
    /* ЦЕНТРАЛЬНЫЙ ЛОГОТИП (как в DeepSeek) */
    .hero-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 55vh;
        text-align: center;
    }
    .whale-logo {
        width: 70px;
        height: 70px;
        background: url('https://chat.deepseek.com/favicon.svg') no-repeat center;
        background-size: contain;
        margin-bottom: 15px;
        filter: drop-shadow(0 0 10px #4081FF);
    }
    .hero-title { font-size: 18px; font-weight: 600; color: #FFFFFF; }
    /* ПОЛЕ ВВОДА */
    .stChatInput {
        bottom: 30px !important;
    }
    .stChatInput textarea {
        background-color: #1A1A1A !important;
        border: 1px solid #2A2A2A !important;
        border-radius: 12px !important;
        color: #FFFFFF !important;
    }
    /* КНОПКИ ИНСТРУМЕНТОВ */
    .input-tools {
        display: flex;
        gap: 8px;
        margin-bottom: 10px;
    }
    .tool-btn {
        background: #131A2A;
        border: 1px solid #1E2D4A;
        color: #4081FF;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 10px;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .tool-btn.search { background: #1A1A1A; border: 1px solid #2A2A2A; color: #FFFFFF; }
    /* ОБЛАЧКА ЧАТА */
    [data-testid="stChatMessage"] { background-color: transparent !important; }
    .stMarkdown p { font-size: 13px !important; line-height: 1.4 !important; }
    /* ОТСТУПЫ */
    .block-container { padding-top: 4rem !important; max-width: 650px !important; }
</style>
""", unsafe_allow_html=True)
# 1. АВТОРИЗАЦИЯ
if "user_id" not in st.session_state:
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
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
# 2. SIDEBAR
with st.sidebar:
    st.markdown(f"👤 **{user_id}**")
    if st.button("ВЫЙТИ"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
    st.markdown("---")
    
    # Файлы для анализа
    st.subheader("📁 Анализ документа")
    pdf_file = st.file_uploader("Загрузить проект договора", type="pdf")
    extra_context = None
    if pdf_file:
        import pypdf
        reader = pypdf.PdfReader(pdf_file)
        extra_context = "".join([p.extract_text() + "\n" for p in reader.pages])
        st.success("Готов")
    st.markdown("---")
    st.subheader("📚 Мои чаты")
    user_chats = db.get_user_chats(user_id)
    if user_chats:
        c_names = [c[1] for c in user_chats]
        c_ids = [c[0] for c in user_chats]
        if "chat_id" not in st.session_state or st.session_state.chat_id not in c_ids:
            st.session_state.chat_id = c_ids[0]
        
        pick = st.selectbox("Список чатов:", options=c_names, index=c_ids.index(st.session_state.chat_id))
        st.session_state.chat_id = c_ids[c_names.index(pick)]
        
        if st.button("УДАЛИТЬ ЧАТ"):
            db.delete_chat(st.session_state.chat_id)
            del st.session_state.chat_id
            st.rerun()
    
    new_chat = st.text_input("Создать новый:", placeholder="Название...")
    if st.button("СОЗДАТЬ"):
        if new_chat:
            nid = db.create_chat(user_id, new_chat)
            if nid:
                st.session_state.chat_id = nid
                st.rerun()
# 3. ОСНОВНОЙ ЭКРАН
chat_id = st.session_state.get("chat_id")
if not chat_id:
    chat_id = db.create_chat(user_id, "Основной чат")
    st.session_state.chat_id = chat_id
messages = db.get_chat_history(chat_id)
if not messages:
    st.markdown("""
        <div class="hero-container">
            <div class="whale-logo"></div>
            <div class="hero-title">Чем могу помочь?</div>
        </div>
    """, unsafe_allow_html=True)
else:
    for i, msg in enumerate(messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                st.download_button("📥 Скачать TXT", msg["content"], f"m_{i}.txt", key=f"dl_{i}")
# 4. ВВОД
st.markdown('<div class="input-tools"><div class="tool-btn">⚛ Рассуждение</div><div class="tool-btn search">🌐 Поиск</div></div>', unsafe_allow_html=True)
if prompt := st.chat_input("Напишите или удерживайте..."):
    with st.chat_message("user"): st.markdown(prompt)
    db.save_message(chat_id, "user", prompt)
    
    with st.spinner(""):
        try:
            from rag_engine import RAGEngine
            engine = RAGEngine()
            response = engine.query(prompt, extra_context=extra_context)
        except: response = "Ошибка анализа."
    
    with st.chat_message("assistant"): st.markdown(response)
    db.save_message(chat_id, "assistant", response)
    st.rerun()

