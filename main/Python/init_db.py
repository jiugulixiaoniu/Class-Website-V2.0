# init_db.py
import sqlite3
import os
import logging
import datetime

DB_DIR = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(DB_DIR, exist_ok=True)

# 定义三个数据库文件路径
DB_PATH1 = os.path.join(DB_DIR, 'class_site.db')
DB_PATH2 = os.path.join(DB_DIR, 'register.db')
DB_PATH3 = os.path.join(DB_DIR, 'system_setting.db')

def init_db(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 创建 users 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE,
                display_name TEXT,
                password TEXT,
                level INTEGER,
                phone TEXT,
                email TEXT,
                is_banned BOOLEAN DEFAULT FALSE,
                last_login TEXT,
                created_at TEXT,
                is_online BOOLEAN DEFAULT FALSE
            )
        ''')

        # 创建 registration_requests 表存储注册申请
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registration_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                display_name TEXT,
                password TEXT,
                phone TEXT,
                email TEXT,
                created_at TEXT,
                status TEXT DEFAULT 'pending',
                reviewed_by TEXT,
                reviewed_at TEXT
            )
        ''')

        # 创建 system_settings 表存储系统设置
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_name TEXT UNIQUE,
                setting_value TEXT
            )
        ''')

        # 创建 access_logs 表存储访问日志
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                username TEXT,
                ip_address TEXT,
                accessed_page TEXT,
                access_time TEXT,
                device_info TEXT
            )
        ''')

        # 创建 articles 表存储文章
        cursor.execute('''
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

        # 插入初始系统设置
        try:
            cursor.execute('''
                INSERT INTO system_settings (setting_name, setting_value)
                VALUES ('registration_status', 'open')
            ''')
        except sqlite3.IntegrityError:
            pass

        # 插入初始用户
        initial_users = [
            {
                'id': '1',
                'username': 'admin',
                'display_name': '管理员',
                'password': '111111',
                'level': 6,
                'phone': '12345678901',
                'email': 'admin@example.com',
                'is_banned': False,
                'last_login': None,
                'created_at': datetime.datetime.now().isoformat(),
                'is_online': False
            }
        ]
        for user in initial_users:
            try:
                cursor.execute('''
                    INSERT INTO users (id, username, display_name, password, level, phone, email, is_banned, last_login, created_at, is_online)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user['id'], user['username'], user['display_name'], user['password'], user['level'],
                    user['phone'], user['email'], user['is_banned'], user['last_login'], user['created_at'], user['is_online']
                ))
            except sqlite3.IntegrityError:
                pass

        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"数据库初始化失败: {e}")

# 初始化三个数据库
init_db(DB_PATH1)
init_db(DB_PATH2)
init_db(DB_PATH3)