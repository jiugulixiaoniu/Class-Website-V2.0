# article.py
import sqlite3
import os
import markdown
import datetime
import jwt
from flask import Blueprint, request, jsonify, render_template
from database_utils import DB_PATH, init_db
from jinja2 import Template
import logging
from flask import render_template as flask_render_template
article_bp = Blueprint('article', __name__)


def render_jinja_template(template_name, **context):
    template_path = os.path.join(TEMPLATES_DIR, template_name)

    if not os.path.exists(template_path):
        logging.error(f"Template not found: {template_path}")
        return ""

    with open(template_path, 'r', encoding='utf-8') as file:
        template_content = file.read()

    template = Template(template_content)
    return template.render(**context)

# 定义文章存储路径
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(base_dir, 'static', 'articles')
os.makedirs(TEMPLATES_DIR, exist_ok=True)
HTML_ARTICLES_DIR = os.path.join(TEMPLATES_DIR, 'html')
os.makedirs(HTML_ARTICLES_DIR, exist_ok=True)
MD_ARTICLES_DIR = os.path.join(TEMPLATES_DIR, 'md')
os.makedirs(MD_ARTICLES_DIR, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@article_bp.route('/api/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, author_id, author_name, status, created_at, updated_at, html_path, md_path 
            FROM articles 
            WHERE id = ?
        ''', (article_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({"error": "文章不存在"}), 404

        article = {
            'id': row['id'],
            'title': row['title'],
            'author_id': row['author_id'],
            'author_name': row['author_name'],
            'status': row['status'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
            'html_path': row['html_path'],
            'md_path': row['md_path']
        }

        return jsonify(article)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@article_bp.route('/api/articles/<int:article_id>/md', methods=['GET'], endpoint='get_article_md')
def get_article_md(article_id):
    """获取文章的Markdown内容"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT md_path FROM articles WHERE id = ?', (article_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({"error": "文章不存在"}), 404

        # 构建完整的MD文件路径
        md_filename = os.path.basename(row['md_path'])
        md_filepath = os.path.join(MD_ARTICLES_DIR, md_filename)

        # 读取MD文件内容
        if not os.path.exists(md_filepath):
            return jsonify({"error": "Markdown文件不存在"}), 404

        with open(md_filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        return jsonify({
            'id': article_id,
            'content': content
        })

    except Exception as e:
        logging.error(f"获取MD内容失败: {str(e)}")
        return jsonify({"error": str(e)}), 500


@article_bp.route('/api/articles', methods=['POST'])
def create_article():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401

        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, 'dev_secret_key_here', algorithms=['HS256'])
        user_level = payload.get('level')

        if user_level < 4:
            return jsonify({"error": "权限不足"}), 403

        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        status = data.get('status', 'draft')

        if not title or not content:
            return jsonify({"error": "标题和内容不能为空"}), 400

        # 生成唯一的文章 ID
        article_id = int(datetime.datetime.utcnow().timestamp() * 1000)

        # 保存 Markdown 文件
        md_filename = f"{article_id}.md"
        md_filepath = os.path.join(MD_ARTICLES_DIR, md_filename)
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"Markdown file saved to: {md_filepath}")

        # 转换为 HTML 并保存
        html_content = markdown.markdown(content)
        html_filename = f"{article_id}.html"
        html_filepath = os.path.join(HTML_ARTICLES_DIR, html_filename)

        # 使用模板生成 HTML 文件
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(render_jinja_template(
                'articles.html',
                title=title,
                author_name=payload.get('username'),
                created_at=datetime.datetime.utcnow().isoformat(),
                content=html_content
            ))
        logging.info(f"HTML file saved to: {html_filepath}")

        # 保存到数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO articles 
            (id, title, author_id, author_name, status, created_at, updated_at, html_path, md_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            article_id,
            title,
            payload.get('id'),
            payload.get('username'),
            status,
            datetime.datetime.utcnow().isoformat(),
            datetime.datetime.utcnow().isoformat(),
            f"/articles/html/{html_filename}",
            f"/articles/md/{md_filename}"
        ))
        conn.commit()
        conn.close()
        logging.info(f"Article saved to database with ID: {article_id}")

        new_article = {
            'id': article_id,
            'title': title,
            'author_id': payload.get('id'),
            'author_name': payload.get('username'),
            'status': status,
            'created_at': datetime.datetime.utcnow().isoformat(),
            'updated_at': datetime.datetime.utcnow().isoformat(),
            'html_path': f"/articles/html/{html_filename}",
            'md_path': f"/articles/md/{md_filename}"
        }

        return jsonify(new_article), 201

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token已过期"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "无效的Token"}), 401
    except Exception as e:
        logging.error(f"Error creating article: {str(e)}")
        return jsonify({"error": str(e)}), 500
@article_bp.route('/api/articles/<int:article_id>', methods=['PUT'])
def update_article(article_id):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401

        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, 'dev_secret_key_here', algorithms=['HS256'])
        user_level = payload.get('level')

        if user_level < 4:  # 只有四级管理员及以上可以编辑文章
            return jsonify({"error": "权限不足"}), 403

        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        status = data.get('status')

        if not title or not content:
            return jsonify({"error": "标题和内容不能为空"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT html_path, md_path FROM articles WHERE id = ?', (article_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "文章不存在"}), 404

        html_path, md_path = row['html_path'], row['md_path']

        # 更新 Markdown 文件
        with open(os.path.join(MD_ARTICLES_DIR, os.path.basename(md_path)), 'w', encoding='utf-8') as f:
            f.write(content)

        # 更新 HTML 文件
        html_content = markdown.markdown(content)
        html_filename = os.path.basename(html_path)
        html_filepath = os.path.join(HTML_ARTICLES_DIR, html_filename)

        # 使用模板生成 HTML 文件
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(render_jinja_template(
                'articles.html',
                title=title,
                author_name=payload.get('username'),
                created_at=datetime.datetime.utcnow().isoformat(),
                content=html_content
            ))

        # 更新数据库
        cursor.execute('''
            UPDATE articles 
            SET title = ?, status = ?, updated_at = ?
            WHERE id = ?
        ''', (
            title,
            status,
            datetime.datetime.utcnow().isoformat(),
            article_id
        ))
        conn.commit()
        conn.close()

        updated_article = {
            'id': article_id,
            'title': title,
            'author_id': payload.get('id'),
            'author_name': payload.get('username'),
            'status': status,
            'updated_at': datetime.datetime.utcnow().isoformat(),
            'html_path': html_path,
            'md_path': md_path
        }

        return jsonify(updated_article)

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token已过期"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "无效的Token"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@article_bp.route('/api/articles/<int:article_id>', methods=['DELETE'], endpoint='delete_article')
def delete_article(article_id):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401

        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, 'dev_secret_key_here', algorithms=['HS256'])
        user_level = payload.get('level')

        # 只有管理员或文章作者可以删除
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT author_id FROM articles WHERE id = ?', (article_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return jsonify({"error": "文章不存在"}), 404

        # 检查权限：管理员(level >=4)或文章作者
        if user_level < 4 and row['author_id'] != payload.get('id'):
            conn.close()
            return jsonify({"error": "权限不足"}), 403

        # 获取文件路径
        cursor.execute('SELECT html_path, md_path FROM articles WHERE id = ?', (article_id,))
        files = cursor.fetchone()

        # 删除数据库记录
        cursor.execute('DELETE FROM articles WHERE id = ?', (article_id,))
        conn.commit()
        conn.close()

        # 删除文件
        try:
            html_file = os.path.join(HTML_ARTICLES_DIR, os.path.basename(files['html_path']))
            if os.path.exists(html_file):
                os.remove(html_file)

            md_file = os.path.join(MD_ARTICLES_DIR, os.path.basename(files['md_path']))
            if os.path.exists(md_file):
                os.remove(md_file)
        except Exception as e:
            logging.warning(f"删除文章文件失败: {str(e)}")

        return jsonify({"message": "文章已成功删除"}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token已过期"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "无效的Token"}), 401
    except Exception as e:
        logging.error(f"删除文章失败: {str(e)}")
        return jsonify({"error": str(e)}), 500


@article_bp.route('/api/articles/<int:article_id>/view')
def view_article(article_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM articles WHERE id = ?', (article_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "文章不存在"}), 404

        article = {
            'id': row['id'],
            'title': row['title'],
            'author_name': row['author_name'],
            'created_at': row['created_at'],
            'md_path': row['md_path']
        }
        conn.close()

        with open(os.path.join(HTML_ARTICLES_DIR, os.path.basename(row['html_path'])), 'r', encoding='utf-8') as f:
            html_content = f.read()

        return render_template(
            'articles.html',  # 需要创建新模板
            title=row['title'],
            author_name=row['author_name'],
            created_at=row['created_at'],
            html_content=html_content
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@article_bp.route('/api/articles/<int:article_id>/raw-md', endpoint='get_raw_md')
def get_raw_md(article_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT md_path FROM articles WHERE id = ?', (article_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "文章不存在"}), 404

        md_path = row['md_path']
        md_filename = os.path.basename(md_path)
        md_filepath = os.path.join(MD_ARTICLES_DIR, md_filename)

        if not os.path.exists(md_filepath):
            return jsonify({"error": "Markdown文件不存在"}), 500

        with open(md_filepath, 'r', encoding='utf-8') as f:
            md_content = f.read()

        return jsonify({"content": md_content})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@article_bp.route('/api/articles', methods=['GET'])
def list_articles():
    try:
        # 获取查询参数
        search = request.args.get('search', '')
        status = request.args.get('status', 'all')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))

        # 构建基础查询
        base_query = '''
            SELECT id, title, author_id, author_name, status, 
                   created_at, updated_at 
            FROM articles 
            WHERE 1=1
        '''
        params = []

        # 添加搜索条件
        if search:
            base_query += ' AND (id LIKE ? OR title LIKE ? OR author_name LIKE ?)'
            search_term = f'%{search}%'
            params.extend([search_term, search_term, search_term])

        # 添加状态过滤
        if status != 'all':
            base_query += ' AND status = ?'
            params.append(status)

        # 添加分页
        offset = (page - 1) * page_size
        base_query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([page_size, offset])

        # 执行查询
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(base_query, params)
        rows = cursor.fetchall()

        # 获取总数
        count_query = 'SELECT COUNT(*) FROM articles WHERE 1=1'
        count_params = params[:-2]  # 去掉LIMIT和OFFSET参数
        if search:
            count_query += ' AND (id LIKE ? OR title LIKE ? OR author_name LIKE ?)'
        if status != 'all':
            count_query += ' AND status = ?'

        cursor.execute(count_query, count_params)
        total = cursor.fetchone()[0]

        # 格式化结果
        articles = []
        for row in rows:
            article = {
                'id': row['id'],
                'title': row['title'],
                'author': row['author_name'],
                'status': row['status'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
            articles.append(article)

        return jsonify({
            'articles': articles,
            'total': total,
            'page': page,
            'page_size': page_size
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@article_bp.route('/api/articles/<int:article_id>/title', methods=['PUT'])
def update_article_title(article_id):
    try:
        # 验证权限
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401

        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, 'dev_secret_key_here', algorithms=['HS256'])

        # 获取新标题
        data = request.get_json()
        new_title = data.get('title')
        if not new_title:
            return jsonify({"error": "标题不能为空"}), 400

        # 更新数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE articles 
            SET title = ?, updated_at = ?
            WHERE id = ?
        ''', (
            new_title,
            datetime.datetime.utcnow().isoformat(),
            article_id
        ))
        conn.commit()

        return jsonify({
            "message": "标题更新成功",
            "id": article_id,
            "title": new_title
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500