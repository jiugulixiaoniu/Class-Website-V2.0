from flask import Blueprint, request, jsonify
import sqlite3
import jwt
import datetime
import logging

# 定义蓝图
user_home_bp = Blueprint('user_home', __name__)

LEVEL_COLORS = {
    1: "#3498db",
    2: "#2ecc71",
    3: "#e67e22",
    4: "#9b59b6",
    5: "#e74c3c",
    6: "#f1c40f"
}

# 获取当前用户信息
@user_home_bp.route('/api/user-profile', methods=['GET'])
def get_user_profile():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401

        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, 'dev_secret_key_here', algorithms=['HS256'])
        username = payload.get('username')

        # 确保数据库路径正确
        conn = sqlite3.connect('database/class_site.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # 构建用户信息字典
        user_info = {
            "display_name": user[2],
            "username": user[1],
            "level": user[4],
            "level_color": LEVEL_COLORS.get(user[4], "#3498db"),
            "bio": user[5] if len(user) > 5 else "暂无简介",  # 确保bio字段存在
            "real_name": user[6] if len(user) > 6 else "暂无信息",
            "gender": user[7] if len(user) > 7 else "暂无信息",
            "grade": user[8] if len(user) > 8 else "暂无信息",
            "class_info": user[9] if len(user) > 9 else "暂无信息",
            "email": user[10] if len(user) > 10 else "暂无信息",
            "registration_date": user[11] if len(user) > 11 else "暂无信息",
            "learning_hours": user[12] if len(user) > 12 else 0,
            "completed_projects": user[13] if len(user) > 13 else 0,
            "awards_won": user[14] if len(user) > 14 else 0
        }

        return jsonify(user_info)
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token已过期"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "无效的Token"}), 401
    except Exception as e:
        logging.error(f"获取用户信息错误: {e}")
        return jsonify({"error": "获取用户信息失败"}), 500

# 获取最近活动
@user_home_bp.route('/api/recent-activities', methods=['GET'])
def get_user_activities():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401

        token = auth_header.split(' ')[1]
        jwt.decode(token, 'dev_secret_key_here', algorithms=['HS256'])

        activities = [
            {"title": "完成了编程项目", "time": "2天前", "category": "程序设计", "icon": "fa-code"},
            {"title": "发表了学习笔记", "time": "3天前", "category": "数学", "icon": "fa-book"},
            {"title": "获得月度之星", "time": "7天前", "category": "班级评选", "icon": "fa-trophy"},
            {"title": "参与了讨论", "time": "10天前", "category": "物理学习组", "icon": "fa-comments"},
            {"title": "报名了竞赛", "time": "14天前", "category": "信息学竞赛", "icon": "fa-calendar-check"}
        ]

        return jsonify(activities)
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token已过期"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "无效的Token"}), 401
    except Exception as e:
        logging.error(f"获取活动记录错误: {e}")
        return jsonify({"error": "获取活动记录失败"}), 500

# 获取学习统计
@user_home_bp.route('/api/learning-stats', methods=['GET'])
def get_learning_stats():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401

        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, 'dev_secret_key_here', algorithms=['HS256'])
        username = payload.get('username')

        # 确保数据库路径正确
        conn = sqlite3.connect('database/class_site.db')
        c = conn.cursor()
        c.execute('SELECT learning_hours FROM users WHERE username = ?', (username,))
        learning_hours = c.fetchone()
        conn.close()

        # 模拟学习统计数据
        months = ['9月', '10月', '11月', '12月', '1月', '2月', '3月']
        data = [12, 18, 15, 20, 25, 22, 18]

        return jsonify({
            "labels": months,
            "data": data,
            "backgroundColor": [
                'rgba(52, 152, 219, 0.7)',
                'rgba(46, 204, 113, 0.7)',
                'rgba(231, 76, 60, 0.7)',
                'rgba(241, 196, 15, 0.7)',
                'rgba(155, 89, 182, 0.7)',
                'rgba(52, 152, 219, 0.7)',
                'rgba(46, 204, 113, 0.7)'
            ]
        })
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token已过期"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "无效的Token"}), 401
    except Exception as e:
        logging.error(f"获取学习统计错误: {e}")
        # 返回模拟数据作为降级处理
        months = ['9月', '10月', '11月', '12月', '1月', '2月', '3月']
        data = [12, 18, 15, 20, 25, 22, 18]
        return jsonify({
            "labels": months,
            "data": data,
            "backgroundColor": [
                'rgba(52, 152, 219, 0.7)',
                'rgba(46, 204, 113, 0.7)',
                'rgba(231, 76, 60, 0.7)',
                'rgba(241, 196, 15, 0.7)',
                'rgba(155, 89, 182, 0.7)',
                'rgba(52, 152, 219, 0.7)',
                'rgba(46, 204, 113, 0.7)'
            ]
        })