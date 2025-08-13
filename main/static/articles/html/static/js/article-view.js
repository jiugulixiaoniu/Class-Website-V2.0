document.addEventListener('DOMContentLoaded', () => {
    // 设置正确的API基础URL
    const API_BASE = 'http://localhost:5000/api';

    // 从URL获取文章ID
    const path = window.location.pathname;
    let articleId;

    if (path.includes('/article/')) {
        articleId = path.split('/').pop().replace('.html', '');
    } else {
        articleId = path.split('/').pop().replace('.html', '');
    }

    // 验证文章ID
    if (!articleId || !/^\d+$/.test(articleId)) {
        console.error('无效的文章ID:', articleId);
        document.getElementById('article-content').innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i> 文章ID无效
            </div>`;
        return;
    }

    // 加载文章Markdown内容
    loadArticleContent(articleId, API_BASE);

    // 检查用户权限
    checkUserPermissions(articleId, API_BASE);
});

function loadArticleContent(articleId, API_BASE) {
    const contentContainer = document.getElementById('article-content');

    // 首先获取文章基本信息
    fetch(`${API_BASE}/articles/${articleId}`, {
        method: 'GET',  // 明确指定GET方法
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('token')
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('获取文章内容失败');
        }
        return response.json();
    })
    .then(article => {
        // 然后获取Markdown内容
        return fetch(`${API_BASE}/articles/${articleId}/raw-md`, {
            method: 'GET',  // 明确指定GET方法
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            }
        })
        .then(response => {
            if (!response.ok) throw new Error('获取Markdown内容失败');
            return response.json();
        })
        .then(mdData => {
            // 渲染Markdown
            const htmlContent = marked.parse(mdData.content, {
                breaks: true,
                gfm: true,
                highlight: function(code, lang) {
                    return `<pre><code class="language-${lang}">${code}</code></pre>`;
                }
            });
            contentContainer.innerHTML = htmlContent;
        });
    })
    .catch(error => {
        console.error('加载文章失败:', error);
        contentContainer.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i> ${error.message}
            </div>`;
    });
}

function checkUserPermissions(articleId, API_BASE) {
    const token = localStorage.getItem('token');
    if (!token) return;

    fetch(`${API_BASE}/articles/${articleId}`, {
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
    .then(response => {
        if (!response.ok) throw new Error('获取文章信息失败');
        return response.json();
    })
    .then(article => {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));

            // 作者或管理员可以编辑/删除
            if (payload.id == article.author_id || payload.level >= 4) {
                document.getElementById('editBtn').style.display = 'inline-block';
                document.getElementById('deleteBtn').style.display = 'inline-block';

                // 绑定编辑和删除事件
                document.getElementById('editBtn').addEventListener('click', () => {
                    window.location.href = `/edit_article.html?id=${articleId}`;
                });

                document.getElementById('deleteBtn').addEventListener('click', () => {
                    if (confirm('确定要删除这篇文章吗？此操作不可恢复。')) {
                        deleteArticle(articleId, API_BASE);
                    }
                });
            }
        } catch (e) {
            console.error('解析token失败:', e);
        }
    })
    .catch(error => {
        console.error('权限检查失败:', error);
    });
}