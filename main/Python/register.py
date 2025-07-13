# register.py
import sqlite3

from flask import Blueprint, request, jsonify
import datetime
from database_utils import DB_PATH1, DB_PATH2, DB_PATH3

register_bp = Blueprint('register', __name__)

def get_system_registration_status(db_path):
    # 从数据库获取系统设置
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT setting_value FROM system_settings WHERE setting_name = ?', ('registration_status',))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'open'  # 默认值为 open，如果数据库中没有该设置

@register_bp.route('/api/register', methods=['POST'])
def handle_register():
    try:
        data = request.get_json()
        username = data.get('username')
        display_name = data.get('display_name')
        password = data.get('password')
        phone = data.get('phone', '')
        email = data.get('email', '')

        # 使用第一个数据库文件
        db_path = DB_PATH1

        # 检查用户名是否已存在
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查用户是否已在 users 表中
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({"error": "用户名已存在"}), 400

        # 检查用户是否已在 registration_requests 表中
        cursor.execute('SELECT * FROM registration_requests WHERE username = ?', (username,))
        existing_request = cursor.fetchone()
        if existing_request:
            return jsonify({"error": "该用户名已提交过注册申请"}), 400

        # 获取当前系统注册状态
        registration_status = get_system_registration_status(db_path)

        if registration_status == 'closed':
            return jsonify({"error": "注册已关闭"}), 400

        if registration_status == 'open':
            # 直接创建用户
            cursor.execute('''
                INSERT INTO users 
                (username, display_name, password, level, phone, email, is_banned, created_at, is_online)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                username, display_name, password, 1, phone, email, False, datetime.datetime.now().isoformat(), False
            ))
            conn.commit()
            conn.close()
            return jsonify({
                "message": "注册成功",
                "user": {
                    'username': username,
                    'display_name': display_name,
                    'level': 1,
                    'phone': phone,
                    'email': email,
                }
            }), 201
        elif registration_status == 'verify':
            # 创建注册申请
            cursor.execute('''
                INSERT INTO registration_requests 
                (username, display_name, password, phone, email, created_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                username, display_name, password, phone, email, datetime.datetime.now().isoformat(), 'pending'
            ))
            conn.commit()
            conn.close()
            return jsonify({
                "message": "注册申请已提交，等待管理员审核"
            }), 201
        else:
            return jsonify({"error": "无效的注册状态"}), 400
    except Exception as e:
        return jsonify({"error": f"注册失败: {str(e)}"}), 500

@register_bp.route('/api/registration-requests', methods=['GET'])
def get_registration_requests():
    try:
        db_path = DB_PATH1
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, display_name, created_at, status 
            FROM registration_requests
            ORDER BY created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()

        requests = []
        for row in rows:
            requests.append({
                'id': row[0],
                'username': row[1],
                'display_name': row[2],
                'created_at': row[3],
                'status': row[4]
            })

        return jsonify(requests)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@register_bp.route('/api/registration-requests/<int:request_id>/review', methods=['POST'])
def review_registration_request(request_id):
    try:
        data = request.get_json()
        action = data.get('action')  # approve 或 reject

        db_path = DB_PATH1
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 获取申请详情
        cursor.execute('SELECT * FROM registration_requests WHERE id = ?', (request_id,))
        request_data = cursor.fetchone()

        if not request_data:
            return jsonify({"error": "注册申请不存在"}), 404

        if action == 'approve':
            # 创建用户
            cursor.execute('''
                INSERT INTO users 
                (username, display_name, password, level, phone, email, is_banned, created_at, is_online)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                request_data[1], request_data[2], request_data[3], 1, request_data[4], request_data[5], False, request_data[6], False
            ))

            # 更新申请状态
            cursor.execute('''
                UPDATE registration_requests 
                SET status = ?, reviewed_by = ?, reviewed_at = ?
                WHERE id = ?
            ''', (
                'approved', 'admin', datetime.datetime.now().isoformat(), request_id
            ))
            conn.commit()
            conn.close()

            return jsonify({
                "message": "注册申请已批准，用户已创建"
            })
        elif action == 'reject':
            # 更新申请状态
            cursor.execute('''
                UPDATE registration_requests 
                SET status = ?, reviewed_by = ?, reviewed_at = ?
                WHERE id = ?
            ''', (
                'rejected', 'admin', datetime.datetime.now().isoformat(), request_id
            ))
            conn.commit()
            conn.close()

            return jsonify({
                "message": "注册申请已拒绝"
            })
        else:
            return jsonify({"error": "无效的操作"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@register_bp.route('/api/admin/create-user', methods=['POST'])
def admin_create_user():
    try:
        data = request.get_json()
        username = data.get('username')
        display_name = data.get('display_name')
        password = data.get('password')
        phone = data.get('phone', '')
        email = data.get('email', '')

        db_path = DB_PATH1
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查用户名是否已存在
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({"error": "用户名已存在"}), 400

        # 检查是否存在未处理的注册申请
        cursor.execute('SELECT * FROM registration_requests WHERE username = ? AND status = ?', (username, 'pending'))
        pending_request = cursor.fetchone()
        if pending_request:
            return jsonify({"error": "该用户名已有未处理的注册申请"}), 400

        # 创建新用户
        cursor.execute('''
            INSERT INTO users 
            (username, display_name, password, level, phone, email, is_banned, created_at, is_online)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            username, display_name, password, 1, phone, email, False, datetime.datetime.now().isoformat(), False
        ))
        conn.commit()
        conn.close()
        return jsonify({
            "message": "用户创建成功",
            "user": {
                'username': username,
                'display_name': display_name,
                'level': 1,
                'phone': phone,
                'email': email,
            }
        }), 201
    except Exception as e:
        return jsonify({"error": f"创建用户失败: {str(e)}"}), 500

@register_bp.route('/api/admin/settings', methods=['PUT'])
def update_registration_status():
    try:
        data = request.get_json()
        new_status = data.get('registration_status')  # open, verify, closed

        db_path = DB_PATH1
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 更新系统设置中的注册状态
        cursor.execute('''
            INSERT OR REPLACE INTO system_settings 
            (id, setting_name, setting_value)
            VALUES ((SELECT id FROM system_settings WHERE setting_name = 'registration_status'), 
            'registration_status', ?)
        ''', (new_status,))
        conn.commit()
        conn.close()

        return jsonify({
            "message": "注册状态已更新",
            "new_status": new_status
        })
    except Exception as e:
        return jsonify({"error": f"更新注册状态失败: {str(e)}"}), 500