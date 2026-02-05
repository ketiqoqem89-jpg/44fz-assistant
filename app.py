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
    .stApp { background-color: #0A0A0A !important; color: #FFFFFF !important; }
    header, footer, .stAppDeployButton, [data-testid="stStatusWidget"] { display: none !important; visibility: hidden !important; }

    /* Верхняя панель */
    .custom-header {
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 20px; position: fixed; top: 0; left: 0; right: 0;
        background: #0A0A0A; z-index: 1000; border-bottom: 1px solid #1A1A1A;
    }
    .header-text { font-size: 14px; font-weight: 500; }

    /* Центральный логотип */
    .hero-container {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        height: 60vh; text-align: center;
    }
    .whale-logo {
        width: 80px; height: 80px;
        background: url('https://chat.deepseek.com/favicon.svg') no-repeat center;
        background-size: contain; margin-bottom: 20px;
        filter: drop-shadow(0 0 10px #4081FF);
    }
    .hero-title { font-size: 20px; font-weight: 600; color: #FFFFFF; }

    /* Поле ввода */
    .stChatInput { bottom: 30px !important; max-width: 90% !important; }
    .stChatInput textarea {
        background-color: #1A1A1A !important; border: 1px solid #2A2A2A !important;
        border-radius: 20px !important; color: #FFFFFF !important; padding: 15px !important;
    }

    /* Инструменты (Рассуждение, Поиск) */
    .input-tools {
        display: flex; gap: 8px; position: fixed; bottom: 100px; left: 25px; z-index: 1001;
    }
    .tool-btn {
        background: #131A2A; border: 1px solid #1E2D4A; color: #4081FF;
        padding: 5px 12px; border-radius: 15px; font-size: 11px;
        display: flex; align-items: center; gap: 5px;
        cursor: pointer;
    }
    .tool-btn.search { background: #1A1A1A; border: 1px solid #2A2A2A; color: #FFFFFF; }

    /* Облачка чата */
    [data-testid="stChatMessage"] { background-color: transparent !important; border: none !important; padding: 10px 0 !important; }
    .stMarkdown p, .stMarkdown td { font-size: 14px !important; color: #E0E0E0 !important; }
    
    /* Кнопки экспорта */
    .export-btn button { font-size: 10px !important; color: #888 !important; border: none !important; background: transparent !important; }
    
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

# 2. ШАПКА
st.markdown(f"""
    <div class="custom-header">
        <div style="font-size: 20px; cursor: pointer;">☰</div>
        <div class="header-text">Чат: {st.session_state.get('chat_name', 'Новый чат')}</div>
        <div style="font-size: 20px; cursor: pointer;">⊕</div>
    </div>
""", unsafe_allow_html=True)

# 3. SIDEBAR
with st.sidebar:
    st.markdown(f"👤 **{user_id}**")
    if st.button("ВЫЙТИ"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
    st.markdown("---")
    
    # Файлы для анализа (Проект контракта)
    st.subheader("Проверка проекта")
    pdf_file = st.file_uploader("Загрузить PDF", type="pdf", key="pdf_analyser")
    extra_context = None
    if pdf_file:
        import pypdf
        reader = pypdf.PdfReader(pdf_file)
        extra_context = "".join([p.extract_text() + "\n" for p in reader.pages])
        st.success("Документ готов")

    st.markdown("---")
    st.subheader("Мои чаты")
    user_chats = db.get_user_chats(user_id)
    if user_chats:
        c_names = [c[1] for c in user_chats]
        c_ids = [c[0] for c in user_chats]
        if "chat_id" not in st.session_state or st.session_state.chat_id not in c_ids:
            st.session_state.chat_id = c_ids[0]
        
        pick = st.selectbox("Переключить:", options=c_names, index=c_ids.index(st.session_state.chat_id))
        st.session_state.chat_id = c_ids[c_names.index(pick)]
        st.session_state.chat_name = pick
        
        if st.button("УДАЛИТЬ ЧАТ"):
            db.delete_chat(st.session_state.chat_id)
            del st.session_state.chat_id
            st.rerun()
    
    new_chat = st.text_input("Создать новый чат:", placeholder="Название...")
    if st.button("СОЗДАТЬ"):
        if new_chat:
            nid = db.create_chat(user_id, new_chat)
            if nid:
                st.session_state.chat_id = nid
                st.session_state.chat_name = new_chat
                st.rerun()

# 4. ЛОГИКА ЧАТА
chat_id = st.session_state.get("chat_id")
if not chat_id:
    chat_id = db.create_chat(user_id, "Новый чат")
    st.session_state.chat_id = chat_id
    st.session_state.chat_name = "Новый чат"

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
                st.download_button(label="📥 Скачать TXT", data=msg["content"], 
                                 file_name=f"otvet_{i}.txt", key=f"dl_{i}")

# 5. ИНСТРУМЕНТЫ
st.markdown("""
    <div class="input-tools">
        <div class="tool-btn">⚛ Рассуждение</div>
        <div class="tool-btn search">🌐 Поиск</div>
    </div>
""", unsafe_allow_html=True)

# 6. ВВОД
if prompt := st.chat_input("Напишите или удерживайте, чтобы говорить"):
    with st.chat_message("user"): st.markdown(prompt)
    db.save_message(chat_id, "user", prompt)
    
    with st.spinner(""):
        try:
            from rag_engine import RAGEngine
            engine = RAGEngine()
            response = engine.query(prompt, extra_context=extra_context)
        except Exception as e:
            response = f"Ошибка: {e}"
    
    with st.chat_message("assistant"): st.markdown(response)
    db.save_message(chat_id, "assistant", response)
    st.rerun()
