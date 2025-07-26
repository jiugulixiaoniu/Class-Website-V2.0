# app.py
import sqlite3

from flask import Flask, request, jsonify, render_template
import jwt
import datetime
import logging
from flask_cors import CORS
from log_activity import log_user_activity, init_logging
from register import registration_bp  # 更新为新的蓝图名称
from database_utils import init_db, load_user_data, save_user_data, DB_PATH

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'dev_secret_key_here'  # 请确保设置一个安全的密钥

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 注册蓝图时使用新的蓝图名称
app.register_blueprint(registration_bp)  # 更新为新的蓝图名称

# 初始化数据库
init_db()

init_logging()  # 新增初始化日志

# 登录
@app.route('/api/login', methods=['POST'])
def handle_login():
    try:
        data = request.get_json()
        login_id = data.get('login_id')  # 可以是用户名或ID
        password = data.get('password')
        users = load_user_data()
        user = None

        # 尝试按ID登录
        if login_id.isdigit():
            user = next((user for user in users['users'] if user['id'] == login_id and user['password'] == password and not user['is_banned']), None)
        else:
            # 尝试按用户名登录
            user = next((user for user in users['users'] if user['username'] == login_id and user['password'] == password and not user['is_banned']), None)

        if not user:
            log_user_activity('Failed login attempt', username=login_id)  # 新增日志记录
            return jsonify({"error": "用户名或密码错误，或用户已被封禁"}), 401

        payload = {
            'username': user['username'],
            'level': user['level'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=168)
        }
        token = jwt.encode(payload, app.secret_key, algorithm='HS256')

        user['last_login'] = datetime.datetime.now().isoformat()
        user['is_online'] = True
        updated_users = [u for u in users['users'] if u['id'] != user['id']]
        updated_users.append(user)
        save_user_data(updated_users)

        log_user_activity('Successful login', user['id'], user['username'])  # 新增日志记录

        return jsonify({
            "token": token,
            "level": user['level'],
            "display_name": user['display_name'],
            "last_login": user['last_login'],
            "is_online": user['is_online']
        })
    except Exception as e:
        logging.error(f"登录错误: {e}")
        log_user_activity('Login error', username=login_id)  # 新增日志记录
        return jsonify({"error": "登录失败，请检查网络连接"}), 500

# 登出
@app.route('/api/logout', methods=['POST'])
def handle_logout():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        users = load_user_data()
        username = payload.get('username')
        user = next((user for user in users['users'] if user['username'] == username), None)
        user_id = user['id'] if user else None
        username_val = user['username'] if user else None
        if not user:
            return jsonify({"error": "User not found"}), 404
        user['is_online'] = False
        updated_users = [u for u in users['users'] if u['id'] != user['id']]
        updated_users.append(user)
        save_user_data(updated_users)
        log_user_activity('Logout', user_id, username_val)  # 添加日志记录
        return jsonify({"message": "Logout successful"})
    except jwt.ExpiredSignatureError:
        log_user_activity('Logout attempt with expired token', username=username_val)  # 添加日志记录
        return jsonify({"error": "Token已过期"}), 401
    except jwt.InvalidTokenError:
        log_user_activity('Logout attempt with invalid token', username=username_val)  # 添加日志记录
        return jsonify({"error": "无效的Token"}), 401
    except Exception as e:
        log_user_activity('Logout error', username=username_val)  # 添加日志记录
        return jsonify({"error": str(e)}), 500

# 验证Token
@app.route('/api/validate', methods=['GET'])
def validate_jwt_token():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        users = load_user_data()
        username = payload.get('username')
        user = next((user for user in users['users'] if user['username'] == username), None)
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify({
            "status": "success",
            "payload": {
                "username": user['display_name'],
                "level": user['level'],
                "is_online": user['is_online']
            }
        })
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token已过期"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "无效的Token"}), 401

# 获取当前用户
@app.route('/api/current-user', methods=['GET'])
def get_current_user():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        users = load_user_data()
        username = payload.get('username')
        user = next((user for user in users['users'] if user['username'] == username), None)
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify({
            "username": user['display_name'],
            "display_name": user['display_name'],
            "level": user['level'],
            "last_login": user['last_login'],
            "is_online": user['is_online']
        })
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token已过期"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "无效的Token"}), 401

# 成员管理相关 API
@app.route('/api/members', methods=['GET'])
def get_members():
    try:
        sort_by = request.args.get('sort_by', 'id')
        order = request.args.get('order', 'asc')
        search = request.args.get('search', '')
        level = request.args.get('level', None)
        status = request.args.get('status', None)
        last_login_start = request.args.get('last_login_start', None)
        last_login_end = request.args.get('last_login_end', None)
        created_start = request.args.get('created_start', None)
        created_end = request.args.get('created_end', None)
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 30))

        data = load_user_data(
            filter_level=level,
            filter_status=status,
            search_query=search,
            sort_by=sort_by,
            sort_order=order,
            last_login_start=last_login_start,
            last_login_end=last_login_end,
            created_start=created_start,
            created_end=created_end,
            page=page,
            page_size=page_size
        )
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/members/<string:id>', methods=['GET'])
def get_member(id):
    try:
        users = load_user_data()
        user = next((user for user in users['users'] if user['id'] == id), None)
        if not user:
            return jsonify({"error": "成员未找到"}), 404
        return jsonify(user)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/members', methods=['POST'])
# 在 add_member 函数中修改ID生成逻辑
def add_member():
    try:
        data = request.get_json()
        username = data.get('username')
        display_name = data.get('display_name')
        password = data.get('password')
        level = data.get('level', 1)
        phone = data.get('phone', '')
        email = data.get('email', '')
        is_banned = data.get('is_banned', False)
        created_at = datetime.datetime.now().isoformat()
        is_online = False

        users = load_user_data()
        if any(user['username'] == username for user in users['users']):
            return jsonify({"error": "用户名已存在"}), 400

        # 原错误代码：new_id = str(len(users['users']) + 1)
        # 改为获取最大ID+1
        max_id = max(int(user['id']) for user in users['users']) if users['users'] else 0
        new_id = str(max_id + 1)

        new_user = {
            'id': new_id,  # 使用新的ID生成方式
            'username': username,
            'display_name': display_name,
            'password': password,
            'level': level,
            'phone': phone,
            'email': email,
            'is_banned': is_banned,
            'last_login': None,
            'created_at': created_at,
            'is_online': is_online
        }
        users['users'].append(new_user)
        save_user_data(users['users'])
        return jsonify(new_user), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/members/<string:id>/ban', methods=['POST'])
def ban_member(id):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        current_user_level = payload.get('level')

        users = load_user_data()
        user = next((user for user in users['users'] if user['id'] == id), None)
        if not user:
            return jsonify({"error": "成员未找到"}), 404

        if current_user_level <= user['level']:
            return jsonify({"error": "权限不足，无法封禁该用户"}), 403

        user['is_banned'] = not user['is_banned']
        updated_users = [u for u in users['users'] if u['id'] != id]
        updated_users.append(user)
        save_user_data(updated_users)

        # 记录操作日志
        action = 'Unban member' if not user['is_banned'] else 'Ban member'
        log_user_activity(action, user['id'], user['username'])

        return jsonify({
            'unbanned': not user['is_banned'],
            'message': f"成员 {user['username']} {'已解封' if not user['is_banned'] else '已封禁'}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 删除成员
@app.route('/api/members/<string:id>/delete', methods=['DELETE'])
def delete_member(id):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        current_user_level = payload.get('level')

        users = load_user_data()
        # 注意：id 本身就是字符串，不再 int(id)
        user = next((u for u in users['users'] if u['id'] == id), None)
        if not user:
            return jsonify({"error": "成员未找到"}), 404

        if current_user_level <= user['level']:
            return jsonify({"error": "权限不足，无法删除该用户"}), 403

        updated_users = [u for u in users['users'] if u['id'] != id]
        save_user_data(updated_users)

        log_user_activity('Delete member', user['id'], user['username'])
        return jsonify({"message": f"成员 {user['display_name']} 已删除"})
    except Exception as e:
        logging.error(f"删除成员错误: {e}")
        return jsonify({"error": str(e)}), 500
@app.route('/api/members/<string:id>/edit', methods=['POST'])
def edit_member(id):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        current_user_level = payload.get('level')

        data = request.get_json()
        username = data.get('username')
        display_name = data.get('display_name')
        phone = data.get('phone')
        email = data.get('email')
        level = data.get('level')

        users = load_user_data()
        user = next((user for user in users['users'] if user['id'] == id), None)
        if not user:
            return jsonify({"error": "成员未找到"}), 404

        if current_user_level <= user['level']:
            return jsonify({"error": "权限不足，无法编辑该用户"}), 403

        user['username'] = username or user['username']
        user['display_name'] = display_name or user['display_name']
        user['phone'] = phone or user['phone']
        user['email'] = email or user['email']
        user['level'] = level or user['level']

        updated_users = [u for u in users['users'] if u['id'] != user['id']]
        updated_users.append(user)
        save_user_data(updated_users)

        # 记录操作日志
        log_user_activity('Edit member', user['id'], user['username'])

        return jsonify(user)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 查询访问日志表
        cursor.execute('SELECT * FROM access_logs ORDER BY access_time DESC')
        rows = cursor.fetchall()

        # 转换为字典格式
        logs = []
        for row in rows:
            log = {
                'id': row[0],
                'user_id': row[1],
                'username': row[2],
                'action': row[3],
                'ip_address': row[4],
                'browser': row[5],
                'device_type': row[6],
                'access_time': row[7],
                'location': row[8]
            }
            logs.append(log)

        conn.close()
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True, port=5000)