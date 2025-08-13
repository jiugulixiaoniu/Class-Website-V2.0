# app.py
import sqlite3
from flask import Flask, request, jsonify, render_template
import jwt
import datetime
import logging
from flask_cors import CORS
from log_activity import log_user_activity, init_logging
from register import registration_bp
from database_utils import init_db, load_user_data, save_user_data, DB_PATH
from user_home import user_home_bp  # 导入用户首页蓝图
from article import article_bp
# 确保所有JWT操作使用相同的密钥
app = Flask(__name__)
app.secret_key = 'dev_secret_key_here'  # 必须与注册/登录使用的密钥一致
app.register_blueprint(article_bp)
CORS(app, supports_credentials=True)


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 注册文章蓝图

# 注册蓝图时使用新的蓝图名称
app.register_blueprint(registration_bp)  # 更新为新的蓝图名称
app.register_blueprint(user_home_bp)  # 注册新的蓝图
# 初始化数据库
init_db()

init_logging()  # 新增初始化日志

LEVEL_COLORS = {
    1: "#3498db",
    2: "#2ecc71",
    3: "#e67e22",
    4: "#9b59b6",
    5: "#e74c3c",
    6: "#f1c40f"
}
# 登录
@app.route('/api/login', methods=['POST'])
def handle_login():
    try:
        # 获取请求数据
        data = request.get_json()
        login_id = data.get('login_id')
        password = data.get('password')

        # 加载用户数据
        users = load_user_data()
        user = None

        # 尝试按ID或用户名登录
        if login_id.isdigit():
            user = next((user for user in users['users'] if user['id'] == login_id and user['password'] == password and not user['is_banned']), None)
        else:
            user = next((user for user in users['users'] if user['username'] == login_id and user['password'] == password and not user['is_banned']), None)

        # 用户不存在或密码错误
        if not user:
            log_user_activity('Failed login attempt', username=login_id, operator_user_id='Unknown', operator_username='Unknown')
            return jsonify({"error": "用户名或密码错误，或用户已被封禁"}), 401

        # 生成JWT Token
        payload = {
            'user_id': user['id'],
            'username': user['username'],
            'display_name': user['display_name'],
            'level': user['level'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=168)
        }
        token = jwt.encode(payload, app.secret_key, algorithm='HS256')

        # 更新用户状态
        user['last_login'] = datetime.datetime.now().isoformat()
        user['is_online'] = True
        updated_users = [u for u in users['users'] if u['id'] != user['id']]
        updated_users.append(user)
        save_user_data(updated_users)

        # 记录登录成功的日志
        log_user_activity(
            'Successful login',
            user_id=user['id'],
            username=user['username'],
            operator_user_id=user['id'],
            operator_username=user['username']
        )

        # 返回响应
        return jsonify({
            "token": token,
            "user_id": user['id'],
            "username": user['username'],
            "display_name": user['display_name'],
            "level": user['level'],
            "last_login": user['last_login']
        })

    except jwt.ExpiredSignatureError:
        log_user_activity('Login attempt with expired token', username=login_id, operator_user_id='Unknown', operator_username='Unknown')
        return jsonify({"error": "Token已过期"}), 401
    except jwt.InvalidTokenError:
        log_user_activity('Login attempt with invalid token', username=login_id, operator_user_id='Unknown', operator_username='Unknown')
        return jsonify({"error": "无效的Token"}), 401
    except Exception as e:
        logging.error(f"登录错误: {e}")
        log_user_activity('Login error', username=login_id, operator_user_id='Unknown', operator_username='Unknown')
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
        log_user_activity('Logout', user_id, username_val, operator_user_id=user_id, operator_username=username_val)
        return jsonify({"message": "Logout successful"})
    except jwt.ExpiredSignatureError:
        log_user_activity('Logout attempt with expired token', username=username_val, operator_user_id='Unknown', operator_username='Unknown')
        return jsonify({"error": "Token已过期"}), 401
    except jwt.InvalidTokenError:
        log_user_activity('Logout attempt with invalid token', username=username_val, operator_user_id='Unknown', operator_username='Unknown')
        return jsonify({"error": "无效的Token"}), 401
    except Exception as e:
        log_user_activity('Logout error', username=username_val, operator_user_id='Unknown', operator_username='Unknown')
        return jsonify({"error": str(e)}), 500

# 验证Token
@app.route('/api/validate', methods=['GET'])
def validate_jwt_token():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Unauthorized"}), 401

        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, app.secret_key, algorithms=['HS256'])

        # 使用user_id查找用户
        user_id = payload.get('user_id')
        users = load_user_data()
        user = next((u for u in users['users'] if u['id'] == user_id), None)

        if not user or user.get('is_banned', False):
            return jsonify({"error": "User invalid"}), 401

        return jsonify({
            "status": "success",
            "payload": {
                "user_id": user['id'],
                "display_name": user['display_name'],
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

        # 使用user_id查找用户
        user_id = payload.get('user_id')
        users = load_user_data()
        user = next((u for u in users['users'] if u['id'] == user_id), None)

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "user_id": user['id'],
            "username": user['username'],
            "display_name": user['display_name'],
            "level": user['level'],
            "last_login": user['last_login'],
            "is_online": user['is_online']
        })
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        logging.error(f"获取当前用户失败: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
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
        log_user_activity('Add member', new_id, display_name, operator_user_id='id', operator_username='username')
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
        log_user_activity(action, user['id'], user['username'], operator_user_id=payload.get('id'), operator_username=payload.get('username'))

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
        log_user_activity('Delete member', user['id'], user['username'], operator_user_id=payload.get('id'), operator_username=payload.get('username'))
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
        log_user_activity('Edit member', user['id'], user['username'], operator_user_id=payload.get('id'), operator_username=payload.get('username'))

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
                'operator_user_id': row[3],
                'operator_username': row[4],
                'action': row[5],
                'ip_address': row[6],
                'browser': row[7],
                'device_type': row[8],
                'access_time': row[9],
                'location': row[10]
            }
            logs.append(log)

        conn.close()
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# 获取统计数据
@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        # 获取在线人数
        online_users = len([user for user in load_user_data()['users'] if user.get('is_online', False)])

        # 获取注册人数
        registered_users = len(load_user_data()['users'])

        # 获取文章总数（这里先返回固定值，后续可以接入实际数据）
        article_count = 42

        # 获取今日访问量
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM access_logs WHERE date(access_time) = ?', (today,))
        today_visits = cursor.fetchone()[0]
        conn.close()

        return jsonify({
            "online_users": online_users,
            "registered_users": registered_users,
            "article_count": article_count,
            "today_visits": today_visits
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/visits/weekly', methods=['GET'])
def get_weekly_visits():
    try:
        # 验证 JWT 令牌
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
        token = auth_header.split(' ')[1]
        jwt.decode(token, app.secret_key, algorithms=['HS256'])

        # 计算最近7天的日期
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=6)

        # 初始化日期列表
        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date.strftime('%Y-%m-%d'))
            current_date += datetime.timedelta(days=1)

        # 查询数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 获取每日访问量
        daily_visits = []
        for date_str in date_list:
            cursor.execute('SELECT COUNT(*) FROM access_logs WHERE date(access_time) = ?', (date_str,))
            count = cursor.fetchone()[0]
            daily_visits.append(count)

        conn.close()

        return jsonify({
            "dates": date_list,
            "visits": daily_visits,
            "total": sum(daily_visits)
        })
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token已过期"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "无效的Token"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/activities/recent', methods=['GET'])
def get_recent_activities():
    try:
        # 验证JWT令牌
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401

        token = auth_header.split(' ')[1]
        jwt.decode(token, app.secret_key, algorithms=['HS256'])

        # 查询数据库获取最近5条日志
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM access_logs 
            ORDER BY access_time DESC 
            LIMIT 5
        ''')
        rows = cursor.fetchall()
        conn.close()

        # 转换为字典格式
        logs = []
        for row in rows:
            log = {
                'id': row[0],
                'user_id': row[1],
                'username': row[2],
                'operator_user_id': row[3],
                'operator_username': row[4],
                'action': row[5],
                'ip_address': row[6],
                'browser': row[7],
                'device_type': row[8],
                'access_time': row[9],
                'location': row[10]
            }
            logs.append(log)

        return jsonify(logs)
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token已过期"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "无效的Token"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True, port=5000)