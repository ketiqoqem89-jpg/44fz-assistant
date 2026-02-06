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

st.set_page_config(
    page_title="Юрист 44-ФЗ", 
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="collapsed"  # На мобильных боковая панель скрыта
)

# --- МОБИЛЬНАЯ ОПТИМИЗАЦИЯ ДЛЯ IPHONE 13 PRO MAX ---
st.markdown("""
<style>
    /* БАЗОВЫЕ НАСТРОЙКИ ДЛЯ МОБИЛЬНЫХ */
    @media (max-width: 430px) {
        /* Основные настройки контейнера */
        .stApp {
            background-color: #0A0A0A !important;
            color: #FFFFFF !important;
            min-height: 100vh;
            padding-bottom: 80px !important; /* Для поля ввода */
        }
        
        /* Скрываем лишние элементы */
        .stAppDeployButton, 
        footer, 
        [data-testid="stStatusWidget"], 
        [data-testid="stDecoration"],
        [data-testid="stHeader"] {
            display: none !important;
        }
        
        /* Основной контейнер контента */
        .main .block-container {
            padding-top: 20px !important;
            padding-left: 15px !important;
            padding-right: 15px !important;
            padding-bottom: 20px !important;
            max-width: 100% !important;
        }
        
        /* ЦЕНТРАЛЬНЫЙ ЛОГОТИП (оптимизирован для мобильных) */
        .hero-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 60vh;
            text-align: center;
            padding: 20px;
        }
        .whale-logo {
            width: 60px;
            height: 60px;
            background: url('https://chat.deepseek.com/favicon.svg') no-repeat center;
            background-size: contain;
            margin-bottom: 15px;
            filter: drop-shadow(0 0 10px #4081FF);
        }
        .hero-title { 
            font-size: 18px !important; 
            font-weight: 600; 
            color: #FFFFFF; 
            margin-bottom: 20px;
        }
        
        /* ПОЛЕ ВВОДА - фиксированное внизу */
        .stChatInput {
            position: fixed !important;
            bottom: 0 !important;
            left: 0 !important;
            right: 0 !important;
            width: 100% !important;
            background-color: #0A0A0A !important;
            padding: 10px 15px !important;
            z-index: 999;
            border-top: 1px solid #2A2A2A !important;
        }
        
        .stChatInput > div {
            max-width: 100% !important;
            margin: 0 !important;
        }
        
        .stChatInput textarea {
            background-color: #1A1A1A !important;
            border: 1px solid #2A2A2A !important;
            border-radius: 20px !important;
            color: #FFFFFF !important;
            font-size: 16px !important; /* Больше для мобильных */
            min-height: 50px !important;
            padding: 12px 45px 12px 15px !important;
        }
        
        /* Кнопка отправки в поле ввода */
        .stChatInput button {
            position: absolute !important;
            right: 20px !important;
            bottom: 10px !important;
            background: transparent !important;
            border: none !important;
            color: #4081FF !important;
            font-size: 24px !important;
        }
        
        /* ОБЛАЧКА ЧАТА */
        .stChatMessage {
            max-width: 85% !important;
            margin: 8px 0 !important;
        }
        
        /* Сообщения пользователя - справа */
        [data-testid="stChatMessage"][data-message-author="user"] {
            margin-left: auto !important;
            margin-right: 0 !important;
            background-color: #4081FF !important;
            border-radius: 18px 18px 4px 18px !important;
            padding: 12px 15px !important;
        }
        
        /* Сообщения ассистента - слева */
        [data-testid="stChatMessage"][data-message-author="assistant"] {
            margin-right: auto !important;
            margin-left: 0 !important;
            background-color: #1A1A1A !important;
            border-radius: 18px 18px 18px 4px !important;
            padding: 12px 15px !important;
        }
        
        .stMarkdown p {
            font-size: 15px !important; /* Увеличиваем шрифт */
            line-height: 1.4 !important;
            margin: 0 !important;
        }
        
        /* Кнопки скачивания в сообщениях */
        .stDownloadButton {
            margin-top: 8px !important;
        }
        
        .stDownloadButton button {
            font-size: 12px !important;
            padding: 5px 10px !important;
            border-radius: 10px !important;
            background-color: transparent !important;
            border: 1px solid #4081FF !important;
            color: #4081FF !important;
        }
        
        /* ЭКРАН АВТОРИЗАЦИИ */
        .stTextInput input {
            font-size: 16px !important;
            height: 50px !important;
            border-radius: 12px !important;
            background-color: #1A1A1A !important;
            border: 1px solid #2A2A2A !important;
            color: #FFFFFF !important;
        }
        
        .stButton button {
            width: 100% !important;
            height: 50px !important;
            border-radius: 12px !important;
            background-color: #4081FF !important;
            color: white !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            border: none !important;
        }
        
        /* БОКОВАЯ ПАНЕЛЬ (мобильное меню) */
        .stSidebar {
            width: 85% !important;
            min-width: 0 !important;
        }
        
        /* Кнопка открытия боковой панели */
        .sidebar-toggle {
            position: fixed !important;
            top: 15px !important;
            left: 15px !important;
            z-index: 1000 !important;
            background-color: #1A1A1A !important;
            border-radius: 50% !important;
            width: 40px !important;
            height: 40px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            border: none !important;
            color: white !important;
            font-size: 20px !important;
        }
    }
    
    /* Для десктопов - сохраняем старый дизайн */
    @media (min-width: 431px) {
        .stApp {
            background-color: #0A0A0A !important;
            color: #FFFFFF !important;
        }
        
        .stAppDeployButton, footer, [data-testid="stStatusWidget"], [data-testid="stDecoration"] {
            display: none !important;
        }
        
        header[data-testid="stHeader"] {
            background-color: #0A0A0A !important;
            border-bottom: 1px solid #1A1A1A !important;
        }
        
        .hero-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 60vh;
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
        
        .hero-title { 
            font-size: 18px; 
            font-weight: 600; 
            color: #FFFFFF; 
        }
        
        .stChatInput textarea {
            background-color: #1A1A1A !important;
            border: 1px solid #2A2A2A !important;
            border-radius: 12px !important;
            color: #FFFFFF !important;
        }
        
        [data-testid="stChatMessage"] { 
            background-color: transparent !important; 
        }
        
        .stMarkdown p { 
            font-size: 13px !important; 
            line-height: 1.4 !important; 
        }
        
        .block-container { 
            padding-top: 4rem !important; 
            max-width: 650px !important; 
        }
        
        .sidebar-toggle {
            display: none !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# 1. АВТОРИЗАЦИЯ
if "user_id" not in st.session_state:
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    st.markdown("<div class='whale-logo'></div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-title'>Вход в систему</div><br>", unsafe_allow_html=True)
    tg_id = st.text_input("ID:", placeholder="@username или номер телефона", label_visibility="collapsed")
    if st.button("ВОЙТИ", use_container_width=True):
        if tg_id:
            st.session_state.user_id = tg_id
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

user_id = st.session_state.user_id

# Мобильная кнопка меню (только на мобильных)
st.markdown("""
<button class="sidebar-toggle" onclick="document.querySelector('[data-testid=\"stSidebar\"]').style.display = 'block'">☰</button>
""", unsafe_allow_html=True)

# 2. SIDEBAR
with st.sidebar:
    # Кнопка закрытия на мобильных
    st.markdown("""
    <div style="text-align: right; margin-bottom: 20px;">
        <button onclick="document.querySelector('[data-testid=\"stSidebar\"]').style.display = 'none'" 
                style="background: none; border: none; color: white; font-size: 20px; cursor: pointer;">✕</button>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"**👤 {user_id}**")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("📱 Профиль", use_container_width=True):
            st.info("Раздел в разработке")
    with col2:
        if st.button("🚪 Выйти", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    st.markdown("---")
    
    # Файлы для анализа
    st.subheader("📁 Анализ документа")
    pdf_file = st.file_uploader("Загрузить PDF", type="pdf", label_visibility="collapsed")
    extra_context = None
    if pdf_file:
        try:
            import pypdf
            reader = pypdf.PdfReader(pdf_file)
            extra_context = "".join([p.extract_text() + "\n" for p in reader.pages])
            st.success("✅ Документ загружен")
        except:
            st.error("❌ Ошибка загрузки PDF")
    
    st.markdown("---")
    st.subheader("📚 Мои чаты")
    
    user_chats = db.get_user_chats(user_id)
    if user_chats:
        c_names = [c[1] for c in user_chats]
        c_ids = [c[0] for c in user_chats]
        
        if "chat_id" not in st.session_state or st.session_state.chat_id not in c_ids:
            st.session_state.chat_id = c_ids[0]
        
        pick = st.selectbox("Выбрать чат:", options=c_names, 
                          index=c_ids.index(st.session_state.chat_id),
                          label_visibility="collapsed")
        st.session_state.chat_id = c_ids[c_names.index(pick)]
        
        col_del, col_new = st.columns([1, 1])
        with col_del:
            if st.button("🗑️ Удалить", use_container_width=True):
                db.delete_chat(st.session_state.chat_id)
                del st.session_state.chat_id
                st.rerun()
    
    new_chat = st.text_input("Название нового чата:", placeholder="Введите название...", 
                           label_visibility="collapsed")
    if st.button("➕ Создать чат", use_container_width=True):
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
            <p style="color: #888; font-size: 14px; margin-top: 10px;">
                Задайте вопрос по 44-ФЗ или загрузите документ для анализа
            </p>
        </div>
    """, unsafe_allow_html=True)
else:
    for i, msg in enumerate(messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                st.download_button(
                    label="📥 Скачать",
                    data=msg["content"],
                    file_name=f"ответ_{i+1}.txt",
                    key=f"dl_{i}",
                    use_container_width=True
                )

# 4. ВВОД СООБЩЕНИЯ
if prompt := st.chat_input("Ваш вопрос по 44-ФЗ..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    db.save_message(chat_id, "user", prompt)
    
    with st.spinner("🤔 Анализирую..."):
        try:
            from rag_engine import RAGEngine
            engine = RAGEngine()
            response = engine.query(prompt, extra_context=extra_context)
        except Exception as e:
            response = f"⚠️ Ошибка: {str(e)}. Проверьте подключение к API."
    
    with st.chat_message("assistant"):
        st.markdown(response)
        st.download_button(
            label="📥 Скачать ответ",
            data=response,
            file_name="ответ_юриста.txt",
            use_container_width=True
        )
    
    db.save_message(chat_id, "assistant", response)
    st.rerun()

# Скрываем боковую панель при клике вне её на мобильных
st.markdown("""
<script>
    // Закрытие боковой панели при клике вне её
    document.addEventListener('click', function(event) {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        const toggleBtn = document.querySelector('.sidebar-toggle');
        
        if (window.innerWidth <= 430 && sidebar && sidebar.style.display === 'block') {
            if (!sidebar.contains(event.target) && event.target !== toggleBtn) {
                sidebar.style.display = 'none';
            }
        }
    });
    
    // Адаптация при изменении размера экрана
    window.addEventListener('resize', function() {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (window.innerWidth > 430 && sidebar) {
            sidebar.style.display = '';
        }
    });
</script>
""", unsafe_allow_html=True)
