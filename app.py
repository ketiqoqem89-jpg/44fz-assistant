import os
import streamlit as st
from dotenv import load_dotenv
import database as db

load_dotenv()
db.init_db()

if "DEEPSEEK_API_KEY" in st.secrets:
    os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]

st.set_page_config(page_title="Юрист 44-ФЗ", page_icon="⚖️", layout="centered")

# СВЕРХКОМПАКТНЫЙ CSS: Минимальные шрифты и отступы
st.markdown("""
    <style>
    /* 1. Заголовки (12px) */
    h1, h2, h3, [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 { 
        font-size: 12px !important; 
        font-weight: bold !important; 
        margin: 0 !important; 
        padding: 2px 0 !important;
    }
    
    /* 2. Текст чата и основной текст (11px) */
    .stChatMessage, .stMarkdown p, .stMarkdown td, .stMarkdown li, label { 
        font-size: 11px !important; 
        line-height: 1.1 !important;
    }
    
    /* 3. Кнопки: Минимальный шрифт и высота */
    .stButton button { 
        font-size: 10px !important; 
        height: 1.8em !important; 
        min-height: 1.8em !important;
        padding: 0px 5px !important;
        margin-bottom: 2px !important;
    }
    
    /* 4. Убираем расстояния между элементами (виджетами) */
    [data-testid="stVerticalBlock"] {
        gap: 0.2rem !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: -5px !important;
    }
    
    /* 5. Компактный Sidebar */
    [data-testid="stSidebar"] .block-container {
        padding-top: 1rem !important;
    }
    
    /* 6. Инпуты (поля ввода) */
    .stTextInput input {
        font-size: 11px !important;
        height: 2em !important;
    }
    </style>
""", unsafe_allow_html=True)

# 1. АВТОРИЗАЦИЯ
if "user_id" not in st.session_state:
    st.markdown("### ⚖️ Вход")
    tg_id = st.text_input("Ваш ID:", placeholder="@username")
    if st.button("ВОЙТИ"):
        if tg_id:
            st.session_state.user_id = tg_id
            st.rerun()
    st.stop()

user_id = st.session_state.user_id

# 2. SIDEBAR
with st.sidebar:
    st.markdown(f"**👤 {user_id}**")
    if st.button("ВЫЙТИ"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
    
    st.markdown("---")
    st.markdown("**Чаты**")
    
    user_chats = db.get_user_chats(user_id)
    new_name = st.text_input("Название:", label_visibility="collapsed")
    if st.button("СОЗДАТЬ"):
        if new_name:
            nid = db.create_chat(user_id, new_name)
            if nid:
                st.session_state.chat_id = nid
                st.rerun()
    
    if user_chats:
        c_names = [c[1] for c in user_chats]
        c_ids = [c[0] for c in user_chats]
        if "chat_id" not in st.session_state or st.session_state.chat_id not in c_ids:
            st.session_state.chat_id = c_ids[0]
        
        idx = c_ids.index(st.session_state.chat_id)
        pick = st.selectbox("Смена:", options=c_names, index=idx, label_visibility="collapsed")
        st.session_state.chat_id = c_ids[c_names.index(pick)]
        
        if st.button("УДАЛИТЬ ЧАТ"):
            db.delete_chat(st.session_state.chat_id)
            del st.session_state.chat_id
            st.rerun()
        selected_chat_id = st.session_state.chat_id
    else: selected_chat_id = None

# 3. ПРИВЕТСТВИЕ
if not selected_chat_id:
    st.markdown("### 👋 Начнем?")
    w_name = st.text_input("Первый чат:")
    if st.button("СОЗДАТЬ И НАЧАТЬ"):
        if w_name:
            res = db.create_chat(user_id, w_name)
            if res:
                st.session_state.chat_id = res
                st.rerun()
    st.stop()

# 4. ЧАТ
current_chat_name = [c[1] for c in user_chats if c[0] == selected_chat_id][0]
st.markdown(f"### 💬 {current_chat_name}")

with st.sidebar:
    st.markdown("---")
    st.markdown("**Анализ PDF**")
    temp_file = st.file_uploader("Файл:", type="pdf", key=f"f_{selected_chat_id}", label_visibility="collapsed")
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
            st.download_button("📥 TXT", msg["content"], f"m_{i}.txt", key=f"dl_{i}")

if prompt := st.chat_input("Вопрос..."):
    with st.chat_message("user"): st.markdown(prompt)
    db.save_message(selected_chat_id, "user", prompt)
    with st.spinner("..."):
        engine = get_engine()
        response = engine.query(prompt, extra_context=temp_content) if engine else "Ошибка"
    with st.chat_message("assistant"): st.markdown(response)
    db.save_message(selected_chat_id, "assistant", response)
    st.rerun()

