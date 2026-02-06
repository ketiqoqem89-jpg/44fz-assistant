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
    initial_sidebar_state="collapsed"
)

# Инициализация темы
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# Функция смены темы
def change_theme(theme_name):
    st.session_state.theme = theme_name
    st.rerun()

# --- СТИЛИ ДЛЯ РАЗНЫХ ТЕМ ---
themes = {
    "dark": {
        "background": "#0A0A0A",
        "text": "#FFFFFF",
        "input_bg": "#1A1A1A",
        "border": "#2A2A2A",
        "primary": "#4081FF",
        "sidebar_bg": "#111111",
        "message_user": "#4081FF",
        "message_assistant": "#1A1A1A"
    },
    "light": {
        "background": "#FFFFFF",
        "text": "#000000", 
        "input_bg": "#F5F5F5",
        "border": "#DDDDDD",
        "primary": "#4081FF",
        "sidebar_bg": "#F8F9FA",
        "message_user": "#4081FF",
        "message_assistant": "#F0F0F0"
    },
    "blue": {
        "background": "#0F172A",
        "text": "#E2E8F0",
        "input_bg": "#1E293B",
        "border": "#334155",
        "primary": "#3B82F6",
        "sidebar_bg": "#1E293B",
        "message_user": "#3B82F6",
        "message_assistant": "#1E293B"
    },
    "green": {
        "background": "#0A1F0A",
        "text": "#F0FFF0",
        "input_bg": "#1A2A1A",
        "border": "#2A3A2A",
        "primary": "#10B981",
        "sidebar_bg": "#1A2A1A",
        "message_user": "#10B981",
        "message_assistant": "#1A2A1A"
    }
}

current_theme = themes[st.session_state.theme]

# --- АДАПТИВНЫЕ СТИЛИ ---
st.markdown(f"""
<style>
    /* ОСНОВНЫЕ СТИЛИ */
    .stApp {{
        background-color: {current_theme["background"]} !important;
        color: {current_theme["text"]} !important;
    }}
    
    /* СОХРАНЯЕМ ВЕРХНЮЮ ПЛАНКУ */
    header[data-testid="stHeader"] {{
        background-color: {current_theme["background"]} !important;
        border-bottom: 1px solid {current_theme["border"]} !important;
    }}
    
    /* ИКОНКИ В ШАПКЕ */
    header[data-testid="stHeader"] button {{
        color: {current_theme["text"]} !important;
    }}
    
    /* СКРЫВАЕМ НЕНУЖНЫЕ ЭЛЕМЕНТЫ */
    .stAppDeployButton, footer, [data-testid="stDecoration"] {{
        display: none !important;
    }}
    
    /* ГЛАВНЫЙ КОНТЕЙНЕР */
    .main .block-container {{
        padding-top: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }}
    
    /* ЦЕНТРАЛЬНЫЙ ЛОГОТИП */
    .hero-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 50vh;
        text-align: center;
        padding: 20px;
    }}
    
    .whale-logo {{
        width: 60px;
        height: 60px;
        background: url('https://chat.deepseek.com/favicon.svg') no-repeat center;
        background-size: contain;
        margin-bottom: 15px;
        filter: drop-shadow(0 0 10px {current_theme["primary"]});
    }}
    
    .hero-title {{
        font-size: 18px !important;
        font-weight: 600 !important;
        color: {current_theme["text"]} !important;
        margin-bottom: 10px !important;
    }}
    
    /* ПОЛЕ ВВОДА */
    .stChatInput {{
        position: fixed !important;
        bottom: 20px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 90% !important;
        max-width: 600px !important;
        background: transparent !important;
        border: none !important;
    }}
    
    .stChatInput textarea {{
        background-color: {current_theme["input_bg"]} !important;
        border: 1px solid {current_theme["border"]} !important;
        border-radius: 20px !important;
        color: {current_theme["text"]} !important;
        font-size: 14px !important;
        min-height: 50px !important;
        padding: 12px 20px !important;
    }}
    
    /* СООБЩЕНИЯ ЧАТА */
    .stChatMessage {{
        max-width: 80% !important;
        margin: 8px 0 !important;
    }}
    
    /* Сообщения пользователя */
    [data-testid="stChatMessage"][data-message-author="user"] {{
        margin-left: auto !important;
        margin-right: 0 !important;
        background-color: {current_theme["message_user"]} !important;
        border-radius: 18px 18px 4px 18px !important;
        padding: 12px 16px !important;
    }}
    
    [data-testid="stChatMessage"][data-message-author="user"] p {{
        color: white !important;
        font-weight: 500 !important;
    }}
    
    /* Сообщения ассистента */
    [data-testid="stChatMessage"][data-message-author="assistant"] {{
        margin-right: auto !important;
        margin-left: 0 !important;
        background-color: {current_theme["message_assistant"]} !important;
        border-radius: 18px 18px 18px 4px !important;
        padding: 12px 16px !important;
        border: 1px solid {current_theme["border"]} !important;
    }}
    
    [data-testid="stChatMessage"][data-message-author="assistant"] p {{
        color: {current_theme["text"]} !important;
        font-weight: 400 !important;
        line-height: 1.5 !important;
    }}
    
    .stMarkdown p {{
        font-size: 14px !important;
        line-height: 1.4 !important;
        margin: 0 !important;
    }}
    
    /* КНОПКИ СКАЧИВАНИЯ */
    .stDownloadButton button {{
        font-size: 12px !important;
        padding: 6px 12px !important;
        border-radius: 10px !important;
        background-color: transparent !important;
        border: 1px solid {current_theme["primary"]} !important;
        color: {current_theme["primary"]} !important;
        margin-top: 8px !important;
    }}
    
    /* ЭКРАН АВТОРИЗАЦИИ */
    .stTextInput input {{
        background-color: {current_theme["input_bg"]} !important;
        border: 1px solid {current_theme["border"]} !important;
        color: {current_theme["text"]} !important;
        border-radius: 12px !important;
        font-size: 14px !important;
    }}
    
    .stButton button {{
        background-color: {current_theme["primary"]} !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }}
    
    /* БОКОВАЯ ПАНЕЛЬ */
    section[data-testid="stSidebar"] {{
        background-color: {current_theme["sidebar_bg"]} !important;
    }}
    
    .stSidebar .stButton button {{
        background-color: {current_theme["input_bg"]} !important;
        color: {current_theme["text"]} !important;
        border: 1px solid {current_theme["border"]} !important;
    }}
    
    /* КНОПКА МЕНЮ ДЛЯ МОБИЛЬНЫХ */
    .mobile-menu-btn {{
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 1000 !important;
        background-color: {current_theme["input_bg"]} !important;
        border: 1px solid {current_theme["border"]} !important;
        border-radius: 8px !important;
        color: {current_theme["text"]} !important;
        padding: 8px 12px !important;
        font-size: 14px !important;
    }}
    
    /* АДАПТИВНОСТЬ ДЛЯ МОБИЛЬНЫХ */
    @media (max-width: 430px) {{
        .stChatInput {{
            width: 95% !important;
            bottom: 10px !important;
        }}
        
        .stChatInput textarea {{
            font-size: 16px !important;
        }}
        
        .stChatMessage {{
            max-width: 85% !important;
        }}
        
        .stMarkdown p {{
            font-size: 15px !important;
        }}
        
        .hero-container {{
            min-height: 40vh;
        }}
    }}
    
    /* ПЕРЕКЛЮЧАТЕЛИ ТЕМ */
    .theme-btn {{
        display: inline-block;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        margin: 2px;
        cursor: pointer;
        border: 2px solid transparent;
    }}
    
    .theme-btn.active {{
        border: 2px solid white;
    }}
    
    .theme-btn.dark {{ background-color: #0A0A0A; }}
    .theme-btn.light {{ background-color: #FFFFFF; }}
    .theme-btn.blue {{ background-color: #0F172A; }}
    .theme-btn.green {{ background-color: #0A1F0A; }}
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

# Кнопка мобильного меню
st.markdown("""
<button class="mobile-menu-btn" onclick="document.querySelector('[data-testid=\"stSidebar\"]').style.display = 'block'">☰ Меню</button>
""", unsafe_allow_html=True)

# 2. БОКОВАЯ ПАНЕЛЬ
with st.sidebar:
    # Кнопка закрытия для мобильных
    st.markdown("""
    <div style="text-align: right; margin-bottom: 10px;">
        <button onclick="document.querySelector('[data-testid=\"stSidebar\"]').style.display = 'none'" 
                style="background: none; border: none; color: inherit; font-size: 20px; cursor: pointer;">✕</button>
    </div>
    """, unsafe_allow_html=True)
    
    # Профиль пользователя
    st.markdown(f"### 👤 {user_id}")
    st.markdown("---")
    
    # Переключатель тем
    st.subheader("🎨 Тема")
    cols = st.columns(4)
    themes_list = list(themes.keys())
    for idx, theme_name in enumerate(themes_list):
        with cols[idx]:
            is_active = "active" if st.session_state.theme == theme_name else ""
            st.markdown(f"""
            <div class="theme-btn {theme_name} {is_active}" 
                 onclick="window.location.href='?theme={theme_name}'"
                 title="{theme_name.capitalize()} тема"></div>
            """, unsafe_allow_html=True)
            st.caption(theme_name.capitalize())
    
    st.markdown("---")
    
    # Кнопки управления профилем
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📱 Профиль", use_container_width=True):
            st.info("Раздел в разработке")
    with col2:
        if st.button("🚪 Выйти", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    st.markdown("---")
    
    # Загрузка файлов
    st.subheader("📁 Анализ документа")
    pdf_file = st.file_uploader("Загрузить PDF", type="pdf", label_visibility="collapsed")
    extra_context = None
    if pdf_file:
        try:
            import pypdf
            reader = pypdf.PdfReader(pdf_file)
            extra_context = "".join([p.extract_text() + "\n" for p in reader.pages])
            st.success("✅ Документ загружен")
        except Exception as e:
            st.error(f"❌ Ошибка: {str(e)}")
    
    st.markdown("---")
    
    # Управление чатами
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
        
        col_del, col_rename = st.columns(2)
        with col_del:
            if st.button("🗑️ Удалить", use_container_width=True):
                db.delete_chat(st.session_state.chat_id)
                del st.session_state.chat_id
                st.rerun()
        with col_rename:
            if st.button("✏️ Переименовать", use_container_width=True):
                st.info("Функция в разработке")
    
    new_chat = st.text_input("Новый чат:", placeholder="Введите название...", 
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
    st.markdown(f"""
        <div class="hero-container">
            <div class="whale-logo"></div>
            <div class="hero-title">Чем могу помочь?</div>
            <p style="color: {current_theme['text']}80; font-size: 14px; margin-top: 10px; text-align: center;">
                Задайте вопрос по 44-ФЗ или загрузите документ для анализа
            </p>
        </div>
    """, unsafe_allow_html=True)
else:
    # Отображаем историю сообщений
    for i, msg in enumerate(messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                st.download_button(
                    label="📥 Скачать ответ",
                    data=msg["content"],
                    file_name=f"ответ_{i+1}.txt",
                    key=f"dl_{i}",
                    use_container_width=True
                )

# 4. ПОЛЕ ВВОДА
if prompt := st.chat_input(f"Ваш вопрос по 44-ФЗ..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    db.save_message(chat_id, "user", prompt)
    
    with st.spinner("🤔 Анализирую..."):
        try:
            from rag_engine import RAGEngine
            engine = RAGEngine()
            response = engine.query(prompt, extra_context=extra_context)
        except Exception as e:
            response = f"⚠️ Ошибка при обработке запроса: {str(e)}\n\nПроверьте подключение к интернету и API ключ."
    
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

# JavaScript для работы темы и мобильного меню
st.markdown("""
<script>
    // Обработка переключения тем
    const urlParams = new URLSearchParams(window.location.search);
    const themeParam = urlParams.get('theme');
    if (themeParam) {
        fetch(window.location.pathname + '?theme=' + themeParam, {method: 'GET'});
    }
    
    // Закрытие боковой панели при клике вне её на мобильных
    document.addEventListener('click', function(event) {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        const menuBtn = document.querySelector('.mobile-menu-btn');
        
        if (window.innerWidth <= 430 && sidebar && sidebar.style.display === 'block') {
            if (!sidebar.contains(event.target) && event.target !== menuBtn) {
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
    
    // Плавная прокрутка к новым сообщениям
    setTimeout(() => {
        const chatMessages = document.querySelectorAll('[data-testid="stChatMessage"]');
        if (chatMessages.length > 0) {
            chatMessages[chatMessages.length - 1].scrollIntoView({ behavior: 'smooth' });
        }
    }, 100);
</script>
""", unsafe_allow_html=True)
