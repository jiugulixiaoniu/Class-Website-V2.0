# register.py
import sqlite3
from flask import Blueprint, request, jsonify
import datetime
from database_utils import get_system_setting, update_system_setting, DB_PATH

# 修改蓝图名称为 registration_bp
registration_bp = Blueprint('registration', __name__)

# ------------------ 注册 ------------------
@registration_bp.route('/api/register', methods=['POST'])
def handle_register():
    data = request.get_json()
    username = data.get('username')
    display_name = data.get('display_name')
    password = data.get('password')
    phone = data.get('phone', '')
    email = data.get('email', '')

    status = get_system_setting('registration_status', 'open')

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        # 唯一性检查
        cur.execute('SELECT 1 FROM users WHERE username = ?', (username,))
        if cur.fetchone():
            return jsonify({"error": "用户名已存在"}), 400
        cur.execute('SELECT 1 FROM registration_requests WHERE username = ?', (username,))
        if cur.fetchone():
            return jsonify({"error": "该用户名已提交过注册申请"}), 400

        # 修改后的ID生成逻辑
        cur.execute('SELECT MAX(id) FROM users')
        max_id = cur.fetchone()[0]

        # 添加类型转换处理
        if max_id is not None:
            max_id = int(max_id)  # 确保转换为整数
        new_id = (max_id if max_id is not None else 0) + 1

        if status == 'open':
            cur.execute('''
                INSERT INTO users (id, username, display_name, password, level, phone, email, created_at, is_online)
                VALUES (?,?,?,?,?,?,?,?,?)
            ''', (new_id, username, display_name, password, 1, phone, email,
                  datetime.datetime.now().isoformat(), 0))
            conn.commit()
            return jsonify({"message": "注册成功"}), 201

        elif status == 'verify':
            cur.execute('''
                INSERT INTO registration_requests
                (username, display_name, password, phone, email, created_at, status)
                VALUES (?,?,?,?,?,?,?)
            ''', (username, display_name, password, phone, email,
                  datetime.datetime.now().isoformat(), 'pending'))
            conn.commit()
            return jsonify({"message": "注册申请已提交，等待管理员审核"}), 201

        else:  # closed
            return jsonify({"error": "注册已关闭"}), 400

# ------------------ 管理员 ------------------
@registration_bp.route('/api/admin/settings', methods=['PUT'])
def update_registration_status():
    new_status = request.json.get('registration_status')
    if new_status not in ['open', 'verify', 'closed']:
        return jsonify({"error": "无效状态"}), 400
    update_system_setting('registration_status', new_status)
    return jsonify({"message": "注册状态已更新", "new_status": new_status})

@registration_bp.route('/api/registration-requests', methods=['GET'])
def list_requests():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, username, display_name, created_at, status FROM registration_requests ORDER BY created_at DESC')
        rows = cur.fetchall()
    return jsonify([dict(zip(['id', 'username', 'display_name', 'created_at', 'status'], row)) for row in rows])

# 在注册审批逻辑中修改ID生成
@registration_bp.route('/api/registration-requests/<int:req_id>/review', methods=['POST'])
def review(req_id):
    action = request.json.get('action')
    if action not in ('approve', 'reject'):
        return jsonify({"error": "操作无效"}), 400

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM registration_requests WHERE id = ?', (req_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "申请不存在"}), 404

        if action == 'approve':
            # 改为获取当前最大ID
            cur.execute('SELECT MAX(id) FROM users')
            max_id = cur.fetchone()[0] or 0
            new_id = max_id + 1

            cur.execute('''
                INSERT INTO users (id, username, display_name, password, level, phone, email, created_at) 
                VALUES (?,?,?,?,?,?,?,?)
            ''', (new_id, row[1], row[2], row[3], 1, row[4], row[5], datetime.datetime.now().isoformat()))

        cur.execute('UPDATE registration_requests SET status = ?, reviewed_by = ?, reviewed_at = ? WHERE id = ?',
                    (action, 'admin', datetime.datetime.now().isoformat(), req_id))
        conn.commit()

        return jsonify({"message": f"已{action}"})