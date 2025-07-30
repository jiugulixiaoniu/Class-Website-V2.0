# init_db.py
import sqlite3
import os
import datetime

DB_DIR = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'class_site.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. 用户表
    c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                display_name TEXT,
                password TEXT,
                level INTEGER DEFAULT 1,
                bio TEXT,
                real_name TEXT,
                gender TEXT,
                grade TEXT,
                class_info TEXT,
                email TEXT,
                registration_date TEXT,
                learning_hours INTEGER DEFAULT 0,
                completed_projects INTEGER DEFAULT 0,
                awards_won INTEGER DEFAULT 0
            )
        ''')

    # 2. 注册申请表
    c.execute('''
        CREATE TABLE IF NOT EXISTS registration_requests (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT UNIQUE,
            display_name TEXT,
            password    TEXT,
            phone       TEXT,
            email       TEXT,
            created_at  TEXT,
            status      TEXT DEFAULT 'pending',
            reviewed_by TEXT,
            reviewed_at TEXT
        )
    ''')

    # 3. 系统设置表
    c.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            setting_name TEXT UNIQUE,
            setting_value TEXT
        )
    ''')

    # 4. 访问日志表
    c.execute('''
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            username TEXT,
            operator_user_id TEXT,
            operator_username TEXT,
            action TEXT,
            ip_address TEXT,
            browser TEXT,
            device_type TEXT,
            access_time TEXT,
            location TEXT
        )
    ''')

    # 5. 文章表
    c.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            author_id TEXT,
            author_name TEXT,
            created_at TEXT,
            updated_at TEXT,
            status TEXT DEFAULT 'draft'
        )
    ''')

    # 默认系统设置：开放注册
    c.execute('''INSERT OR IGNORE INTO system_settings (setting_name, setting_value)
                 VALUES ('registration_status', 'open')''')

    # 默认管理员
    c.execute('''INSERT OR IGNORE INTO users
                 (id, username, display_name, password, level, phone, email, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              ('1', 'admin', '管理员', '111111', 6, '12345678901', 'admin@example.com', datetime.datetime.now().isoformat()))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()