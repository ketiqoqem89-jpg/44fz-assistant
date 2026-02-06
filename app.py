import React, { useState, useEffect, useRef } from 'react';

const App = () => {
  const themes = {
    dark: {
      background: "#0A0A0A",
      text: "#FFFFFF",
      input_bg: "#1A1A1A",
      border: "#2A2A2A",
      primary: "#4081FF",
      sidebar_bg: "#111111",
      message_user: "#4081FF",
      message_assistant: "#1A1A1A"
    },
    light: {
      background: "#FFFFFF",
      text: "#000000", 
      input_bg: "#F5F5F5",
      border: "#DDDDDD",
      primary: "#4081FF",
      sidebar_bg: "#F8F9FA",
      message_user: "#4081FF",
      message_assistant: "#F0F0F0"
    },
    blue: {
      background: "#0F172A",
      text: "#E2E8F0",
      input_bg: "#1E293B",
      border: "#334155",
      primary: "#3B82F6",
      sidebar_bg: "#1E293B",
      message_user: "#3B82F6",
      message_assistant: "#1E293B"
    },
    green: {
      background: "#0A1F0A",
      text: "#F0FFF0",
      input_bg: "#1A2A1A",
      border: "#2A3A2A",
      primary: "#10B981",
      sidebar_bg: "#1A2A1A",
      message_user: "#10B981",
      message_assistant: "#1A2A1A"
    }
  };

  const [theme, setTheme] = useState('dark');
  const [user, setUser] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [chats, setChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [pdfContext, setPdfContext] = useState(null);
  const [newChatName, setNewChatName] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (chats.length === 0) {
      const initialChat = {
        id: Date.now(),
        name: 'Основной чат',
        messages: []
      };
      setChats([initialChat]);
      setCurrentChatId(initialChat.id);
    }
  }, [chats]);

  useEffect(() => {
    const root = document.documentElement;
    const currentTheme = themes[theme];
    Object.entries(currentTheme).forEach(([key, value]) => {
      root.style.setProperty(`--${key.replace('_', '-')}`, value);
    });
    
    const urlParams = new URLSearchParams(window.location.search);
    const themeParam = urlParams.get('theme');
    if (themeParam && themes[themeParam]) {
      setTheme(themeParam);
    }
  }, [theme]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chats, currentChatId]);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 768) {
        setIsSidebarOpen(true);
      } else {
        setIsSidebarOpen(false);
      }
    };
    
    window.addEventListener('resize', handleResize);
    handleResize();
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleLogin = (userId) => {
    if (userId.trim()) {
      setUser(userId.trim());
      if (chats.length === 0) {
        const initialChat = {
          id: Date.now(),
          name: 'Основной чат',
          messages: []
        };
        setChats([initialChat]);
        setCurrentChatId(initialChat.id);
      }
    }
  };

  const handleLogout = () => {
    setUser(null);
    setChats([]);
    setCurrentChatId(null);
    setPdfContext(null);
  };

  const createChat = () => {
    if (newChatName.trim()) {
      const newChat = {
        id: Date.now(),
        name: newChatName.trim(),
        messages: []
      };
      setChats([...chats, newChat]);
      setCurrentChatId(newChat.id);
      setNewChatName('');
    }
  };

  const deleteChat = (chatId) => {
    const updatedChats = chats.filter(chat => chat.id !== chatId);
    setChats(updatedChats);
    
    if (currentChatId === chatId) {
      setCurrentChatId(updatedChats.length > 0 ? updatedChats[0].id : null);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setPdfContext(`Документ "${file.name}" успешно загружен и готов к анализу.`);
      e.target.value = null;
    }
  };

  const handleSendMessage = () => {
    if (!inputMessage.trim() || !currentChatId) return;
    
    const userMessage = {
      role: 'user',
      content: inputMessage.trim()
    };
    
    setChats(prevChats => 
      prevChats.map(chat => 
        chat.id === currentChatId 
          ? { ...chat, messages: [...chat.messages, userMessage] }
          : chat
      )
    );
    
    setInputMessage('');
    setIsLoading(true);
    
    setTimeout(() => {
      let response = '';
      
      if (pdfContext && inputMessage.toLowerCase().includes('документ')) {
        response = `На основе загруженного документа: ${pdfContext}\n\n${generateResponse(inputMessage)}`;
      } else {
        response = generateResponse(inputMessage);
      }
      
      const assistantMessage = {
        role: 'assistant',
        content: response
      };
      
      setChats(prevChats => 
        prevChats.map(chat => 
          chat.id === currentChatId 
            ? { ...chat, messages: [...chat.messages, assistantMessage] }
            : chat
        )
      );
      
      setIsLoading(false);
    }, 1000);
  };

  const generateResponse = (query) => {
    if (query.toLowerCase().includes('44-фз')) {
      return `Статья 44-ФЗ регулирует вопросы контрактной системы в сфере закупок товаров, работ, услуг для обеспечения государственных и муниципальных нужд. Основные положения включают:\n\n• Порядок планирования закупок\n• Требования к участникам закупок\n• Процедуры проведения торгов\n• Контроль в сфере закупок\n\nДля получения конкретной информации уточните ваш вопрос.`;
    }
    
    if (query.toLowerCase().includes('тендер')) {
      return `Тендер (конкурс) согласно 44-ФЗ - это способ определения поставщика, при котором победителем признается участник, предложивший лучшие условия исполнения контракта. Основные этапы:\n\n1. Размещение извещения о проведении конкурса\n2. Подача заявок участниками\n3. Рассмотрение и оценка заявок\n4. Подведение итогов и заключение контракта\n\nСроки проведения конкурса составляют не менее 20 дней с даты размещения извещения.`;
    }
    
    return `Ваш вопрос: "${query}"\n\nСогласно Федеральному закону №44-ФЗ "О контрактной системе в сфере закупок товаров, работ, услуг для обеспечения государственных и муниципальных нужд", я могу предоставить следующую информацию:\n\n• Для уточнения нормативных требований обратитесь к конкретной статье закона\n• При анализе тендерной документации проверяйте соответствие требованиям 44-ФЗ\n• Сроки подачи заявок зависят от типа закупки и начальной цены контракта\n\nРекомендую уточнить ваш вопрос для получения более детальной информации.`;
  };

  const downloadMessage = (content, filename) => {
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(content));
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const currentMessages = currentChatId 
    ? chats.find(chat => chat.id === currentChatId)?.messages || []
    : [];

  if (!user) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center" style={{ backgroundColor: themes[theme].background, color: themes[theme].text }}>
        <style>{`
          :root {
            ${Object.entries(themes[theme]).map(([key, value]) => `--${key.replace('_', '-')}: ${value};`).join('\n')}
          }
        `}</style>
        
        <div className="hero-container text-center px-4">
          <div 
            className="whale-logo mx-auto mb-4"
            style={{
              width: '60px',
              height: '60px',
              backgroundImage: "url('https://chat.deepseek.com/favicon.svg')",
              backgroundRepeat: 'no-repeat',
              backgroundPosition: 'center',
              backgroundSize: 'contain',
              filter: `drop-shadow(0 0 10px ${themes[theme].primary})`
            }}
          ></div>
          <h1 className="hero-title text-xl font-semibold mb-2">Вход в систему</h1>
          <p className="text-sm opacity-80 mb-6">Пожалуйста, авторизуйтесь для продолжения</p>
          
          <div className="w-full max-w-xs">
            <input
              type="text"
              placeholder="@username или номер телефона"
              className="w-full px-4 py-3 rounded-xl mb-4"
              style={{ 
                backgroundColor: themes[theme].input_bg,
                border: `1px solid ${themes[theme].border}`,
                color: themes[theme].text
              }}
              onKeyPress={(e) => e.key === 'Enter' && handleLogin(e.target.value)}
            />
            <button
              className="w-full py-3 rounded-xl font-medium text-white"
              style={{ backgroundColor: themes[theme].primary }}
              onClick={() => handleLogin(document.querySelector('input[type="text"]').value)}
            >
              ВОЙТИ
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex" style={{ backgroundColor: themes[theme].background, color: themes[theme].text }}>
      <style>{`
        :root {
          ${Object.entries(themes[theme]).map(([key, value]) => `--${key.replace('_', '-')}: ${value};`).join('\n')}
        }
        
        .sidebar {
          background-color: var(--sidebar-bg);
          border-right: 1px solid var(--border);
          transition: transform 0.3s ease;
        }
        
        .sidebar.mobile {
          position: fixed;
          left: 0;
          top: 0;
          height: 100vh;
          width: 280px;
          z-index: 1000;
          transform: translateX(-100%);
        }
        
        .sidebar.mobile.open {
          transform: translateX(0);
        }
        
        .chat-container {
          flex: 1;
          display: flex;
          flex-direction: column;
          max-width: 100%;
          padding: 1.5rem;
          padding-bottom: 100px;
        }
        
        .message {
          max-width: 80%;
          margin: 8px 0;
          padding: 12px 16px;
          border-radius: 18px;
          line-height: 1.5;
          font-size: 14px;
        }
        
        .message.user {
          margin-left: auto;
          background-color: var(--message-user);
          border-radius: 18px 18px 4px 18px;
          color: white;
          font-weight: 500;
        }
        
        .message.assistant {
          margin-right: auto;
          background-color: var(--message-assistant);
          border: 1px solid var(--border);
          border-radius: 18px 18px 18px 4px;
          color: var(--text);
        }
        
        .chat-input-container {
          position: fixed;
          bottom: 20px;
          left: 50%;
          transform: translateX(-50%);
          width: 90%;
          max-width: 600px;
          z-index: 100;
        }
        
        .chat-input {
          width: 100%;
          min-height: 50px;
          padding: 12px 20px;
          border-radius: 20px;
          font-size: 14px;
          resize: none;
          background-color: var(--input-bg);
          border: 1px solid var(--border);
          color: var(--text);
        }
        
        .chat-input:focus {
          outline: none;
          border-color: var(--primary);
        }
        
        .theme-btn {
          display: inline-block;
          width: 30px;
          height: 30px;
          border-radius: 50%;
          margin: 2px;
          cursor: pointer;
          border: 2px solid transparent;
        }
        
        .theme-btn.active {
          border: 2px solid white;
        }
        
        .theme-btn.dark { background-color: #0A0A0A; }
        .theme-btn.light { background-color: #FFFFFF; border-color: #DDD; }
        .theme-btn.blue { background-color: #0F172A; }
        .theme-btn.green { background-color: #0A1F0A; }
        
        .mobile-menu-btn {
          position: fixed;
          top: 10px;
          left: 10px;
          z-index: 1001;
          background-color: var(--input-bg);
          border: 1px solid var(--border);
          border-radius: 8px;
          color: var(--text);
          padding: 8px 12px;
          font-size: 14px;
          display: none;
        }
        
        @media (max-width: 768px) {
          .sidebar.desktop {
            display: none;
          }
          
          .sidebar.mobile {
            display: block;
          }
          
          .mobile-menu-btn {
            display: block;
          }
          
          .chat-container {
            padding: 1rem;
            padding-bottom: 90px;
          }
          
          .chat-input-container {
            width: 95%;
            bottom: 10px;
          }
          
          .message {
            max-width: 85%;
            font-size: 15px;
          }
        }
      `}</style>
      
      <button 
        className="mobile-menu-btn"
        onClick={() => setIsSidebarOpen(true)}
      >
        ☰ Меню
      </button>
      
      <div className="sidebar desktop hidden md:block w-64">
        <SidebarContent 
          user={user}
          theme={theme}
          themes={themes}
          chats={chats}
          currentChatId={currentChatId}
          pdfContext={pdfContext}
          newChatName={newChatName}
          onThemeChange={setTheme}
          onChatSelect={setCurrentChatId}
          onChatDelete={deleteChat}
          onNewChatNameChange={setNewChatName}
          onCreateChat={createChat}
          onFileUpload={handleFileUpload}
          onLogout={handleLogout}
        />
      </div>
      
      <div className={`sidebar mobile ${isSidebarOpen ? 'open' : ''}`}>
        <div className="p-4 text-right">
          <button 
            onClick={() => setIsSidebarOpen(false)}
            className="text-2xl"
            style={{ color: themes[theme].text }}
          >
            ✕
          </button>
        </div>
        <SidebarContent 
          user={user}
          theme={theme}
          themes={themes}
          chats={chats}
          currentChatId={currentChatId}
          pdfContext={pdfContext}
          newChatName={newChatName}
          onThemeChange={(newTheme) => {
            setTheme(newTheme);
            setIsSidebarOpen(false);
          }}
          onChatSelect={(chatId) => {
            setCurrentChatId(chatId);
            setIsSidebarOpen(false);
          }}
          onChatDelete={deleteChat}
          onNewChatNameChange={setNewChatName}
          onCreateChat={createChat}
          onFileUpload={handleFileUpload}
          onLogout={handleLogout}
        />
      </div>
      
      <div className="chat-container">
        {currentMessages.length === 0 ? (
          <div className="hero-container text-center flex flex-col items-center justify-center h-full">
            <div 
              className="whale-logo mb-4"
              style={{
                width: '60px',
                height: '60px',
                backgroundImage: "url('https://chat.deepseek.com/favicon.svg')",
                backgroundRepeat: 'no-repeat',
                backgroundPosition: 'center',
                backgroundSize: 'contain',
                filter: `drop-shadow(0 0 10px ${themes[theme].primary})`
              }}
            ></div>
            <h1 className="hero-title text-xl font-semibold mb-2">Чем могу помочь?</h1>
            <p className="opacity-80 text-sm">
              Задайте вопрос по 44-ФЗ или загрузите документ для анализа
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {currentMessages.map((message, index) => (
              <div 
                key={index} 
                className={`message ${message.role}`}
              >
                {message.content}
                {message.role === 'assistant' && (
                  <button
                    className="mt-2 px-3 py-1 rounded-lg text-xs flex items-center justify-center w-full"
                    style={{ 
                      border: `1px solid ${themes[theme].primary}`,
                      color: themes[theme].primary,
                      backgroundColor: 'transparent'
                    }}
                    onClick={() => downloadMessage(message.content, `ответ_${index + 1}.txt`)}
                  >
                    📥 Скачать ответ
                  </button>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
        
        {isLoading && (
          <div className="message assistant">
            🤔 Анализирую...
          </div>
        )}
      </div>
      
      <div className="chat-input-container">
        <textarea
          className="chat-input"
          placeholder="Ваш вопрос по 44-ФЗ..."
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSendMessage())}
        />
      </div>
    </div>
  );
};

const SidebarContent = ({
  user,
  theme,
  themes,
  chats,
  currentChatId,
  pdfContext,
  newChatName,
  onThemeChange,
  onChatSelect,
  onChatDelete,
  onNewChatNameChange,
  onCreateChat,
  onFileUpload,
  onLogout
}) => {
  return (
    <div className="h-full flex flex-col p-4">
      <div className="mb-4 pb-4 border-b" style={{ borderColor: themes[theme].border }}>
        <div className="font-bold text-lg flex items-center">
          <span className="mr-2">👤</span>
          {user}
        </div>
      </div>
      
      <div className="mb-6">
        <h3 className="font-semibold mb-3 flex items-center">
          <span className="mr-2">🎨</span>
          Тема
        </h3>
        <div className="grid grid-cols-4 gap-2">
          {Object.keys(themes).map((themeName) => (
            <div key={themeName} className="text-center">
              <div
                className={`theme-btn ${themeName} ${theme === themeName ? 'active' : ''}`}
                onClick={() => onThemeChange(themeName)}
                title={`${themeName.charAt(0).toUpperCase() + themeName.slice(1)} тема`}
              />
              <div className="text-xs mt-1">
                {themeName.charAt(0).toUpperCase() + themeName.slice(1)}
              </div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="mb-6 grid grid-cols-2 gap-3">
        <button
          className="py-2 rounded-lg font-medium flex items-center justify-center"
          style={{ 
            backgroundColor: themes[theme].input_bg,
            border: `1px solid ${themes[theme].border}`,
            color: themes[theme].text
          }}
        >
          <span className="mr-1">📱</span>
          Профиль
        </button>
        <button
          className="py-2 rounded-lg font-medium flex items-center justify-center"
          style={{ 
            backgroundColor: themes[theme].input_bg,
            border: `1px solid ${themes[theme].border}`,
            color: themes[theme].text
          }}
          onClick={onLogout}
        >
          <span className="mr-1">🚪</span>
          Выйти
        </button>
      </div>
      
      <div className="mb-6 pb-4 border-b" style={{ borderColor: themes[theme].border }}>
        <h3 className="font-semibold mb-3 flex items-center">
          <span className="mr-2">📁</span>
          Анализ документа
        </h3>
        <label className="block">
          <input
            type="file"
            accept=".pdf"
            onChange={onFileUpload}
            className="hidden"
          />
          <div
            className="border-2 border-dashed rounded-lg p-4 text-center cursor-pointer hover:opacity-80 transition-opacity"
            style={{ 
              borderColor: themes[theme].border,
              backgroundColor: themes[theme].input_bg
            }}
          >
            {pdfContext ? (
              <div className="text-green-500">✅ Документ загружен</div>
            ) : (
              <div>
                <div className="text-2xl mb-2">📄</div>
                <div>Загрузить PDF</div>
              </div>
            )}
          </div>
        </label>
        {pdfContext && (
          <div className="mt-2 text-xs opacity-80">
            {pdfContext}
          </div>
        )}
      </div>
      
      <div className="mb-4">
        <h3 className="font-semibold mb-3 flex items-center">
          <span className="mr-2">📚</span>
          Мои чаты
        </h3>
        
        <div className="space-y-2 mb-4 max-h-60 overflow-y-auto pr-2">
          {chats.map((chat) => (
            <div
              key={chat.id}
              className={`p-3 rounded-lg cursor-pointer transition-colors ${
                currentChatId === chat.id ? 'opacity-100' : 'opacity-70 hover:opacity-90'
              }`}
              style={{ 
                backgroundColor: currentChatId === chat.id ? themes[theme].primary : themes[theme].input_bg,
                color: currentChatId === chat.id ? 'white' : themes[theme].text
              }}
              onClick={() => onChatSelect(chat.id)}
            >
              {chat.name}
            </div>
          ))}
        </div>
        
        <div className="grid grid-cols-2 gap-2 mb-4">
          <button
            className="py-2 rounded-lg font-medium flex items-center justify-center"
            style={{ 
              backgroundColor: themes[theme].input_bg,
              border: `1px solid ${themes[theme].border}`,
              color: themes[theme].text
            }}
            onClick={() => currentChatId && onChatDelete(currentChatId)}
          >
            <span className="mr-1">🗑️</span>
            Удалить
          </button>
          <button
            className="py-2 rounded-lg font-medium flex items-center justify-center"
            style={{ 
              backgroundColor: themes[theme].input_bg,
              border: `1px solid ${themes[theme].border}`,
              color: themes[theme].text
            }}
          >
            <span className="mr-1">✏️</span>
            Переименовать
          </button>
        </div>
        
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Новый чат..."
            className="flex-1 px-3 py-2 rounded-lg"
            style={{ 
              backgroundColor: themes[theme].input_bg,
              border: `1px solid ${themes[theme].border}`,
              color: themes[theme].text
            }}
            value={newChatName}
            onChange={(e) => onNewChatNameChange(e.target.value)}
          />
          <button
            className="px-4 rounded-lg font-medium flex items-center justify-center"
            style={{ 
              backgroundColor: themes[theme].primary,
              color: 'white'
            }}
            onClick={onCreateChat}
          >
            ➕
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;
