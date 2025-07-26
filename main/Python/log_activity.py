# log_activity.py
import os
import sqlite3
import datetime
import logging
from flask import request

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'class_site.db')

def log_user_activity(action, user_id=None, username=None):
    try:
        # 获取真实的 IP 地址
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        browser = request.headers.get('User-Agent')
        device_type = 'PC' if 'Windows' in browser or 'Macintosh' in browser else 'Mobile'
        access_time = datetime.datetime.now().isoformat()

        # 如果用户未登录，user_id 和 username 为 None
        if not user_id:
            user_id = 'Guest'
        if not username:
            username = 'Guest'

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO access_logs (user_id, username, action, ip_address, browser, device_type, access_time, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, action, ip_address, browser, device_type, access_time, 'Unknown'))

        conn.commit()
        conn.close()

        # 写入服务器日志
        logging.basicConfig(filename='server.log', level=logging.INFO)
        logging.info(f'[{access_time}] - {user_id} ({username}) - {ip_address} - {action} - Device: {device_type}')
    except Exception as e:
        logging.error(f'Error logging activity: {str(e)}')
def init_logging():
    logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(message)s')