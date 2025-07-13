# database_utils.py
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

def load_user_data(db_path, filter_level=None, filter_status=None, search_query=None, sort_by='id', sort_order='asc', last_login_start=None, last_login_end=None, created_start=None, created_end=None, page=1, page_size=30):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = '''
            SELECT * FROM users
            WHERE 1=1
        '''

        params = []

        # 等级筛选
        if filter_level:
            query += ' AND level = ?'
            params.append(filter_level)

        # 状态筛选
        if filter_status:
            if filter_status == 'online':
                query += ' AND is_online = 1'
            elif filter_status == 'offline':
                query += ' AND is_online = 0'
            elif filter_status == 'banned':
                query += ' AND is_banned = 1'
            elif filter_status == 'unbanned':
                query += ' AND is_banned = 0'

        # 关键字搜索
        if search_query:
            query += ' AND (username LIKE ? OR display_name LIKE ? OR id LIKE ?)'
            search_param = f'%{search_query}%'
            params.extend([search_param, search_param, search_param])

        # 日期筛选
        if last_login_start:
            start_date = datetime.datetime.strptime(last_login_start, "%Y-%m-%d").isoformat()
            query += ' AND last_login >= ?'
            params.append(start_date)
        if last_login_end:
            end_date = datetime.datetime.strptime(last_login_end, "%Y-%m-%d") + datetime.timedelta(days=1)
            end_date = end_date.isoformat()
            query += ' AND last_login < ?'
            params.append(end_date)
        if created_start:
            start_date = datetime.datetime.strptime(created_start, "%Y-%m-%d").isoformat()
            query += ' AND created_at >= ?'
            params.append(start_date)
        if created_end:
            end_date = datetime.datetime.strptime(created_end, "%Y-%m-%d") + datetime.timedelta(days=1)
            end_date = end_date.isoformat()
            query += ' AND created_at < ?'
            params.append(end_date)

        # 分页
        query += f' ORDER BY {sort_by} {sort_order}'
        query += ' LIMIT ? OFFSET ?'
        params.extend([page_size, (page - 1) * page_size])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        users = []
        for row in rows:
            users.append({
                'id': row[0],
                'username': row[1],
                'display_name': row[2],
                'password': row[3],
                'level': row[4],
                'phone': row[5],
                'email': row[6],
                'is_banned': row[7],
                'last_login': row[8],
                'created_at': row[9],
                'is_online': row[10]
            })

        # 获取总记录数用于分页
        count_query = '''
            SELECT COUNT(*) FROM users
            WHERE 1=1
        '''
        count_params = params[:-2]  # 排除分页参数
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()[0]

        conn.close()
        return {
            'users': users,
            'total': total,
            'page': page,
            'page_size': page_size
        }
    except Exception as e:
        logging.error(f"加载用户数据失败: {e}")
        return {'users': [], 'total': 0, 'page': 1, 'page_size': 30}

def save_user_data(db_path, users):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        for user in users:
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (id, username, display_name, password, level, phone, email, is_banned, last_login, created_at, is_online)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user['id'], user['username'], user['display_name'], user['password'], user['level'],
                user['phone'], user['email'], user['is_banned'], user['last_login'], user['created_at'], user['is_online']
            ))
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"保存用户数据失败: {e}")

def get_system_setting(db_path, setting_name):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT setting_value FROM system_settings WHERE setting_name = ?', (setting_name,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        logging.error(f"获取系统设置失败: {e}")
        return None

def update_system_setting(db_path, setting_name, setting_value):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO system_settings 
            (id, setting_name, setting_value)
            VALUES ((SELECT id FROM system_settings WHERE setting_name = ?), ?, ?)
        ''', (setting_name, setting_name, setting_value))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logging.error(f"更新系统设置失败: {e}")
        return False

def log_access(db_path, user_id, username, ip_address, accessed_page, device_info):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO access_logs 
            (user_id, username, ip_address, accessed_page, access_time, device_info)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_id, username, ip_address, accessed_page, datetime.datetime.now().isoformat(), device_info
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logging.error(f"记录访问日志失败: {e}")
        return False

def get_access_logs(db_path, start_date=None, end_date=None, page=1, page_size=30):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = '''
            SELECT * FROM access_logs
            WHERE 1=1
        '''

        params = []

        if start_date:
            query += ' AND access_time >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND access_time < ?'
            params.append(end_date)

        query += ' ORDER BY access_time DESC LIMIT ? OFFSET ?'
        params.extend([page_size, (page - 1) * page_size])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        logs = []
        for row in rows:
            logs.append({
                'id': row[0],
                'user_id': row[1],
                'username': row[2],
                'ip_address': row[3],
                'accessed_page': row[4],
                'access_time': row[5],
                'device_info': row[6]
            })

        # 获取总记录数用于分页
        count_query = '''
            SELECT COUNT(*) FROM access_logs
            WHERE 1=1
        '''
        count_params = params[:-2]  # 排除分页参数
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()[0]

        conn.close()
        return {
            'logs': logs,
            'total': total,
            'page': page,
            'page_size': page_size
        }
    except Exception as e:
        logging.error(f"加载访问日志失败: {e}")
        return {'logs': [], 'total': 0, 'page': 1, 'page_size': 30}

def get_article(db_path, id):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM articles WHERE id = ?', (id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'author_id': row[3],
                'author_name': row[4],
                'created_at': row[5],
                'updated_at': row[6],
                'status': row[7]
            }
        return None
    except Exception as e:
        logging.error(f"获取文章失败: {e}")
        return None

def get_articles(db_path, title=None, author_id=None, status=None, page=1, page_size=10):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = '''
            SELECT * FROM articles
            WHERE 1=1
        '''

        params = []

        if title:
            query += ' AND title LIKE ?'
            params.append(f'%{title}%')
        if author_id:
            query += ' AND author_id = ?'
            params.append(author_id)
        if status:
            query += ' AND status = ?'
            params.append(status)

        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([page_size, (page - 1) * page_size])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        articles = []
        for row in rows:
            articles.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'author_id': row[3],
                'author_name': row[4],
                'created_at': row[5],
                'updated_at': row[6],
                'status': row[7]
            })

        # 获取总记录数用于分页
        count_query = '''
            SELECT COUNT(*) FROM articles
            WHERE 1=1
        '''
        count_params = params[:-2]  # 排除分页参数
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()[0]

        conn.close()
        return {
            'articles': articles,
            'total': total,
            'page': page,
            'page_size': page_size
        }
    except Exception as e:
        logging.error(f"加载文章失败: {e}")
        return {'articles': [], 'total': 0, 'page': 1, 'page_size': 10}

def create_article(db_path, title, content, author_id, author_name):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO articles 
            (title, content, author_id, author_name, created_at, updated_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            title, content, author_id, author_name, datetime.datetime.now().isoformat(), datetime.datetime.now().isoformat(), 'draft'
        ))
        conn.commit()
        conn.close()
        return cursor.lastrowid
    except Exception as e:
        logging.error(f"创建文章失败: {e}")
        return None

def update_article(db_path, id, title, content, status):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE articles 
            SET title = ?, content = ?, updated_at = ?, status = ?
            WHERE id = ?
        ''', (
            title, content, datetime.datetime.now().isoformat(), status, id
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logging.error(f"更新文章失败: {e}")
        return False

def delete_article(db_path, id):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM articles WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logging.error(f"删除文章失败: {e}")
        return False