document.addEventListener('DOMContentLoaded', () => {
    // 初始化 Toast-UI Editor
    const editor = new toastui.Editor({
        el: document.getElementById('editor-content'),
        height: '500px',
        initialEditType: 'markdown',
        previewStyle: 'tab',
        plugins: [toastui.Editor.plugin.codeSyntaxHighlight],
        toolbarItems: [
            ['heading', 'bold', 'italic', 'strike'],
            ['hr', 'quote'],
            ['ul', 'ol', 'task', 'indent', 'outdent'],
            ['table', 'image', 'link'],
            ['code', 'codeblock'],
            ['scrollSync']
        ],
        hooks: {
            addImageBlobHook: (blob, callback) => {
                const formData = new FormData();
                formData.append('image', blob);
                fetch('http://localhost:5000/api/upload', {
                    method: 'POST',
                    headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') },
                    body: formData
                })
                .then(res => res.json())
                .then(data => callback(data.url, 'alt'))
                .catch(() => callback('', '上传失败'));
            }
        }
    });

    // 从URL获取文章ID（如果是编辑页面）
    const urlParams = new URLSearchParams(window.location.search);
    const articleId = urlParams.get('id');
    if (articleId) {
        // 加载文章内容到编辑器
        loadArticleForEdit(articleId, editor);
        document.querySelector('h2').textContent = '编辑文章';
        document.getElementById('publish-article').textContent = '更新文章';
    }

    // 发布/更新文章
    document.getElementById('publish-article').addEventListener('click', function(e) {
        e.preventDefault();
        const title = document.getElementById('article-title').value;
        const content = editor.getMarkdown();
        const status = document.getElementById('article-status').value || 'draft';

        if (!title || !content) {
            showNotification('标题和内容不能为空', 'error');
            return;
        }

        const formData = { title, content, status };
        const url = articleId
            ? `http://localhost:5000/api/articles/${articleId}`
            : 'http://localhost:5000/api/articles';
        const method = articleId ? 'PUT' : 'POST';

        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || '操作失败') });
            }
            return response.json();
        })
        .then(data => {
            const message = articleId ? '文章更新成功' : '文章发布成功';
            showNotification(message, 'success');
            setTimeout(() => {
                window.location.href = data.html_path;
            }, 1500);
        })
        .catch(error => {
            console.error('操作失败:', error);
            showNotification(error.message || '操作失败，请检查网络连接', 'error');
        });
    });

    // 保存草稿
    document.querySelector('.draft-btn').addEventListener('click', function(e) {
        e.preventDefault();
        const title = document.getElementById('article-title').value;
        const content = editor.getMarkdown();

        if (!title || !content) {
            showNotification('标题和内容不能为空', 'error');
            return;
        }

        const formData = {
            title: title,
            content: content,
            status: 'draft'
        };

        const url = articleId
            ? `http://localhost:5000/api/articles/${articleId}`
            : 'http://localhost:5000/api/articles';
        const method = articleId ? 'PUT' : 'POST';

        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (!response.ok) throw new Error('保存失败');
            return response.json();
        })
        .then(data => {
            showNotification('草稿保存成功', 'success');
        })
        .catch(error => {
            console.error('保存草稿失败:', error);
            showNotification('草稿保存失败，请检查网络连接', 'error');
        });
    });

    // 加载文章用于编辑
    function loadArticleForEdit(articleId, editor) {
        fetch(`http://localhost:5000/api/articles/${articleId}/raw-md`, {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            }
        })
        .then(response => {
            if (!response.ok) throw new Error('获取文章失败');
            return response.json();
        })
        .then(data => {
            editor.setMarkdown(data.content);
            // 获取文章标题
            return fetch(`http://localhost:5000/api/articles/${articleId}`, {
                headers: {
                    'Authorization': 'Bearer ' + localStorage.getItem('token')
                }
            });
        })
        .then(response => response.json())
        .then(article => {
            document.getElementById('article-title').value = article.title;
            document.getElementById('article-status').value = article.status;
        })
        .catch(error => {
            console.error('加载文章失败:', error);
            showNotification('加载文章失败，请重试', 'error');
        });
    }

    // 显示通知
    function showNotification(message, type = 'success') {
        const notificationContainer = document.createElement('div');
        notificationContainer.className = 'notification-container';
        document.body.appendChild(notificationContainer);

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="fas ${type === 'success' ? 'fa-check' : 'fa-times'}"></i>
            </div>
            <div class="notification-content">
                ${message}
            </div>
            <div class="notification-progress-bar"></div>
        `;
        notificationContainer.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notificationContainer.remove();
            }, 500);
        }, 3000);
    }
});