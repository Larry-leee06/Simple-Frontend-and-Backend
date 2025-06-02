// 模拟文章数据
const articles = [
    {
        id: 1,
        title: '环保小贴士：如何减少日常生活中的碳足迹',
        content: '随着全球气候变化日益严重，减少碳足迹变得越来越重要...',
        author: '绿色先锋',
        date: '2024-03-20',
        likes: 156,
        comments: 23
    },
    {
        id: 2,
        title: '可持续发展：城市垃圾分类指南',
        content: '垃圾分类是环境保护的第一步...',
        author: '环保达人',
        date: '2024-03-19',
        likes: 89,
        comments: 15
    }
];

// 模拟商品数据
const products = [
    {
        id: 1,
        name: '环保购物袋',
        price: 15.00,
        description: '可重复使用的环保购物袋'
    },
    {
        id: 2,
        name: '不锈钢吸管',
        price: 20.00,
        description: '可重复使用的不锈钢吸管'
    }
];

// 加载文章列表
function loadArticles() {
    const articleList = document.querySelector('.article-list');
    if (!articleList) return;

    articleList.innerHTML = articles.map(article => `
        <div class="article-card" data-id="${article.id}">
            <h3>${article.title}</h3>
            <p>${article.content}</p>
            <div class="article-meta">
                <span class="author">${article.author}</span>
                <span class="date">${article.date}</span>
                <div class="article-actions">
                    <button class="like-btn" onclick="handleLike(${article.id})">
                        👍 ${article.likes}
                    </button>
                    <button class="comment-btn" onclick="handleComment(${article.id})">
                        💬 ${article.comments}
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// 加载商品列表
function loadProducts() {
    const productList = document.querySelector('.product-list');
    if (!productList) return;

    productList.innerHTML = products.map(product => `
        <div class="product-card" data-id="${product.id}">
            <h4>${product.name}</h4>
            <p>${product.description}</p>
            <div class="product-price">¥${product.price.toFixed(2)}</div>
        </div>
    `).join('');
}

// 处理点赞
function handleLike(articleId) {
    const article = articles.find(a => a.id === articleId);
    if (article) {
        article.likes++;
        loadArticles();
    }
}

// 处理评论
function handleComment(articleId) {
    // 这里可以添加打开评论模态框的逻辑
    alert('评论功能即将上线！');
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    loadArticles();
    loadProducts();
}); 