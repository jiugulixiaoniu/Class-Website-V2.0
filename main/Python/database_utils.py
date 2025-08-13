# database_utils.py
import sqlite3
import os
import datetime

DB_DIR = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'class_site.db')

# ---------- 初始化 ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. 用户表
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            display_name TEXT,
            password TEXT,
            level INTEGER,
            phone TEXT,
            email TEXT,
            is_banned INTEGER DEFAULT 0,
            last_login TEXT,
            created_at TEXT,
            is_online INTEGER DEFAULT 0
        )
    ''')

    # 2. 注册申请表
    c.execute('''
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
            id INTEGER PRIMARY KEY,
            title TEXT,
            content TEXT,
            author_id TEXT,
            author_name TEXT,
            status TEXT DEFAULT 'draft',
            created_at TEXT,
            updated_at TEXT,
            html_path TEXT,
            md_path TEXT
        )
    ''')

    # 默认系统设置：开放注册
    c.execute('''INSERT OR IGNORE INTO system_settings (setting_name, setting_value)
                 VALUES ('registration_status', 'open')''')

    # 默认管理员
    c.execute('''INSERT OR IGNORE INTO users
                 (id, username, display_name, password, level, phone, email, created_at, is_online)
                 VALUES ('1', 'admin', '管理员', '111111', 6, '12345678901', 'admin@example.com', ?, 0)''',
              (datetime.datetime.now().isoformat(),))

    conn.commit()
    conn.close()

# ---------- 分页 + 搜索建议者筛选 + 排序 ----------
def load_user_data(filter_level=None, filter_status=None, search_query=None, sort_by='id', sort_order='asc', last_login_start=None, last_login_end=None, created_start=None, created_end=None, page=1, page_size=30):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    sql = 'SELECT * FROM users WHERE 1=1'
    params = []

    # 等级筛选
    if filter_level is not None and str(filter_level).strip() != '':
        sql += ' AND level = ?'
        params.append(str(filter_level))

    # 状态筛选
    if filter_status:
        if filter_status == 'online':
            sql += ' AND is_online = 1'
        elif filter_status == 'offline':
            sql += ' AND is_online = 0'
        elif filter_status == 'banned':
            sql += ' AND is_banned = 1'

    # 关键字搜索
    if search_query and search_query.strip() != '':
        search_term = f'%{search_query.strip()}%'
        sql += ' AND (id LIKE ? OR username LIKE ? OR display_name LIKE ?)'
        params.extend([search_term, search_term, search_term])

    # 日期筛选 - 最后登录时间
    if last_login_start:
        try:
            datetime.datetime.strptime(last_login_start, '%Y-%m-%d')
            sql += ' AND last_login >= ?'
            params.append(last_login_start + ' 00:00:00')
        except ValueError:
            pass  # 无效日期格式，忽略该条件

    if last_login_end:
        try:
            datetime.datetime.strptime(last_login_end, '%Y-%m-%d')
            sql += ' AND last_login < ?'
            params.append(last_login_end + ' 23:59:59')
        except ValueError:
            pass  # 无效日期格式，忽略该条件

    # 日期筛选 - 创建时间
    if created_start:
        try:
            datetime.datetime.strptime(created_start, '%Y-%m-%d')
            sql += ' AND created_at >= ?'
            params.append(created_start + ' 00:00:00')
        except ValueError:
            pass  # 无效日期格式，忽略该条件

    if created_end:
        try:
            datetime.datetime.strptime(created_end, '%Y-%m-%d')
            sql += ' AND created_at < ?'
            params.append(created_end + ' 23:59:59')
        except ValueError:
            pass  # 无效日期格式，忽略该条件

    # 验证排序字段是否合法，防止SQL注入
    valid_sort_fields = ['id', 'username', 'display_name', 'level', 'last_login', 'created_at']
    if sort_by not in valid_sort_fields:
        sort_by = 'id'  # 默认按ID排序

    # 验证排序顺序是否合法
    sort_order = sort_order.lower()
    if sort_order not in ['asc', 'desc']:
        sort_order = 'asc'  # 默认升序

    # 分页
    sql += f' ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?'
    params.extend([page_size, (page - 1) * page_size])

    try:
        cur.execute(sql, params)
        rows = cur.fetchall()
        users = [dict(zip([d[0] for d in cur.description], row)) for row in rows]
    except Exception as e:
        print(f"SQL执行错误: {e}")
        print(f"SQL: {sql}")
        print(f"参数: {params}")
        users = []

    # 计算总记录数
    count_sql = 'SELECT COUNT(*) FROM users WHERE 1=1'
    count_params = []

    if filter_level is not None and str(filter_level).strip() != '':
        count_sql += ' AND level = ?'
        count_params.append(str(filter_level))

    if filter_status:
        if filter_status == 'online':
            count_sql += ' AND is_online = 1'
        elif filter_status == 'offline':
            count_sql += ' AND is_online = 0'
        elif filter_status == 'banned':
            count_sql += ' AND is_banned = 1'

    if search_query and search_query.strip() != '':
        search_term = f'%{search_query.strip()}%'
        count_sql += ' AND (id LIKE ? OR username LIKE ? OR display_name LIKE ?)'
        count_params.extend([search_term, search_term, search_term])

    if last_login_start:
        try:
            datetime.datetime.strptime(last_login_start, '%Y-%m-%d')
            count_sql += ' AND last_login >= ?'
            count_params.append(last_login_start + ' 00:00:00')
        except ValueError:
            pass

    if last_login_end:
        try:
            datetime.datetime.strptime(last_login_end, '%Y-%m-%d')
            count_sql += ' AND last_login < ?'
            count_params.append(last_login_end + ' 23:59:59')
        except ValueError:
            pass

    if created_start:
        try:
            datetime.datetime.strptime(created_start, '%Y-%m-%d')
            count_sql += ' AND created_at >= ?'
            count_params.append(created_start + ' 00:00:00')
        except ValueError:
            pass

    if created_end:
        try:
            datetime.datetime.strptime(created_end, '%Y-%m-%d')
            count_sql += ' AND created_at < ?'
            count_params.append(created_end + ' 23:59:59')
        except ValueError:
            pass

    try:
        cur.execute(count_sql, count_params)
        total = cur.fetchone()[0]
    except Exception as e:
        print(f"SQL计数错误: {e}")
        total = 0

    conn.close()
    return {'users': users, 'total': total, 'page': page, 'page_size': page_size}

# ---------- 工具 ----------
def save_user_data(users):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 先清空表
    cur.execute('DELETE FROM users')

    # 批量插入新数据
    cur.executemany('''
        INSERT INTO users 
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    ''', [(u['id'], u['username'], u['display_name'], u['password'], u['level'],
           u['phone'], u['email'], u['is_banned'], u['last_login'],
           u['created_at'], u['is_online']) for u in users])

    conn.commit()
    conn.close()

def get_system_setting(key, default=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT setting_value FROM system_settings WHERE setting_name = ?', (key,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else default

def update_system_setting(key, value):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('INSERT OR REPLACE INTO system_settings (setting_name, setting_value) VALUES (?,?)', (key, value))
    conn.commit()
    conn.close()