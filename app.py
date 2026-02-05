import os
import streamlit as st
from dotenv import load_dotenv
import database as db

load_dotenv()
db.init_db()

if "DEEPSEEK_API_KEY" in st.secrets:
    os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]

st.set_page_config(page_title="Юрист 44-ФЗ", page_icon="⚖️", layout="centered")

# УЛЬТРА-КОМПАКТНЫЙ CSS: Заголовки 14px, Текст 12px
st.markdown("""
    <style>
    /* 1. Настройка кнопки МЕНЮ (три полоски) */
    [data-testid="stHeader"] {
        top: 20px !important;
        background: transparent !important;
    }
    
    /* 2. Скрываем лишнее */
    .stAppDeployButton {display:none !important;}
    .stAppToolbar {display:none !important;}
    [data-testid="stStatusWidget"] {display:none !important;}
    footer {visibility: hidden !important;}

    /* 3. Уменьшаем ЗАГОЛОВКИ до 14px */
    h1 { font-size: 14px !important; font-weight: bold !important; margin-top: 0px !important; }
    h2 { font-size: 13px !important; font-weight: bold !important; }
    h3 { font-size: 12px !important; font-weight: bold !important; }
    
    /* 4. Текст и чат 12px */
    .stChatMessage, .stMarkdown p, .stMarkdown td, .stMarkdown li { font-size: 12px !important; }
    
    /* 5. Компактные кнопки */
    .stButton button { width: 100%; border-radius: 6px; height: 2.2em; font-size: 11px !important; }
    
    /* 6. Отступ сверху */
    .block-container { padding-top: 4rem !important; }
    </style>
""", unsafe_allow_html=True)

# 1. АВТОРИЗАЦИЯ
if "user_id" not in st.session_state:
    st.markdown("### ⚖️ Вход")
    tg_id = st.text_input("Ваш ID:", placeholder="@username", key="login_id")
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
    st.markdown("**Мои чаты**")
    
    user_chats = db.get_user_chats(user_id)
    new_name = st.text_input("Название чата:", key="side_input", label_visibility="collapsed")
    if st.button("СОЗДАТЬ", key="side_btn"):
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
        
        idx = c_ids.index(st.session_state.chat_id)
        pick = st.selectbox("Переключить:", options=c_names, index=idx, label_visibility="collapsed")
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
    w_name = st.text_input("Назовите первый чат:", placeholder="Напр: Общий", key="w_in")
    if st.button("СОЗДАТЬ ЧАТ", key="w_bt"):
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
    temp_file = st.file_uploader("Загрузить", type="pdf", key=f"f_{selected_chat_id}", label_visibility="collapsed")
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
