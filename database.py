import sqlite3
import os

DB_PATH = os.path.join("data", "users_history.db")

def init_db():
    if not os.path.exists("data"):
        os.makedirs("data")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Таблица чатов
    c.execute('''CREATE TABLE IF NOT EXISTS chats 
                 (chat_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_id TEXT, 
                  chat_name TEXT, 
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    # Таблица сообщений, привязанная к chat_id
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (chat_id INTEGER, role TEXT, content TEXT, 
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def create_chat(user_id, chat_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Проверка лимита в 10 чатов
    c.execute("SELECT COUNT(*) FROM chats WHERE user_id = ?", (user_id,))
    if c.fetchone()[0] >= 10:
        conn.close()
        return False
    c.execute("INSERT INTO chats (user_id, chat_name) VALUES (?, ?)", (user_id, chat_name))
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_user_chats(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT chat_id, chat_name FROM chats WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    chats = c.fetchall()
    conn.close()
    return chats

def save_message(chat_id, role, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO history (chat_id, role, content) VALUES (?, ?, ?)", (chat_id, role, content))
    conn.commit()
    conn.close()

def get_chat_history(chat_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT role, content FROM history WHERE chat_id = ? ORDER BY timestamp ASC", (chat_id,))
    rows = c.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in rows]

def delete_chat(chat_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM chats WHERE chat_id = ?", (chat_id,))
    c.execute("DELETE FROM history WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()
