// 全局API密钥
let apiKey = '';

// 存储当前视频列表
let currentVideos = [];
let currentPage = 1;
const videosPerPage = 100;

// 页面加载完成后执行
window.onload = function() {
    console.log("页面加载完成");
    
    // 加载保存的API密钥
    apiKey = localStorage.getItem('youtube_api_key') || '';
    if (apiKey) {
        document.getElementById('apiKey').value = apiKey;
        console.log("已加载保存的API密钥");
    }
};

// 保存API密钥
function saveApiKey() {
    console.log("保存API密钥");
    const inputElement = document.getElementById('apiKey');
    if (!inputElement) {
        console.error("找不到API密钥输入框");
        return;
    }
    
    apiKey = inputElement.value.trim();
    if (!apiKey) {
        alert("请输入API密钥");
        return;
    }
    
    // 保存到本地存储
    localStorage.setItem('youtube_api_key', apiKey);
    alert("API密钥已保存");
    
    // 测试API密钥
    testApiKey(apiKey);
}

// 测试API密钥
async function testApiKey(key) {
    try {
        console.log("测试API密钥:", key);
        
        // 显示测试中...
        console.log("发送API测试请求...");
        
        // 使用新的测试端点
        const response = await fetch('/test_api', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ apiKey: key })
        });
        
        console.log("收到响应状态:", response.status);
        
        if (!response.ok) {
            if (response.status === 404) {
                alert("错误: 找不到API测试路由 (404)");
                throw new Error("找不到API测试路由，请确保服务器正确配置");
            } else {
                alert("错误: 服务器返回 " + response.status);
                throw new Error("服务器错误: " + response.status);
            }
        }
        
        const data = await response.json();
        console.log("测试结果:", data);
        
        if (data.success) {
            // 测试路由成功，保存API密钥
            alert("API密钥测试成功！");
            localStorage.setItem('youtube_api_key', key);
            return true;
        } else {
            alert("API密钥测试失败: " + (data.error || "未知错误"));
            return false;
        }
    } catch (error) {
        console.error("API测试错误:", error);
        alert("测试出错: " + error.message);
        return false;
    }
}

// 搜索视频
async function searchVideos() {
    const keyInput = document.getElementById('apiKey');
    const queryInput = document.getElementById('searchInput');
    const videoCountSelect = document.getElementById('videoCount');
    
    if (!keyInput || !queryInput) {
        console.error("找不到输入元素");
        return;
    }
    
    // 添加搜索提示文字
    const searchContainer = queryInput.parentElement;
    if (!document.querySelector('.search-hint')) {
        const hintElement = document.createElement('div');
        hintElement.className = 'search-hint';
        hintElement.textContent = '芝士猫特别提醒：关键词搜索"#关键词"或"关键词"，频道搜索格式"@频道名"。有任何疑问请联系芝士猫邮箱:imluluj8@outlook.com';
        searchContainer.appendChild(hintElement);
    }

    const key = keyInput.value.trim();
    const query = queryInput.value.trim();
    const maxResults = parseInt(videoCountSelect.value);
    
    if (!key) {
        alert("请先设置API密钥");
        return;
    }
    
    if (!query) {
        alert("请输入搜索内容");
        return;
    }
    
    try {
        console.log("搜索视频:", query, "数量限制:", maxResults);
        
        // 显示加载中
        const loadingElement = document.getElementById('loading');
        if (loadingElement) {
            loadingElement.style.display = 'flex';
        }
        
        const searchType = document.getElementById('searchType')?.value || 'keyword';
        
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                apiKey: key,
                type: searchType,
                query: query,
                maxResults: maxResults,
                sortBy: 'date' // 默认按时间排序
            })
        });
        
        const data = await response.json();
        console.log("搜索结果:", data);
        
        // 隐藏加载中
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
        
        // 处理结果
        const resultsElement = document.getElementById('results');
        const sortOptionsElement = document.getElementById('sortOptions');
        
        if (!resultsElement) {
            console.error("找不到结果显示区域");
            return;
        }
        
        if (response.ok && data.videos && data.videos.length > 0) {
            // 限制视频数量
            currentVideos = data.videos.slice(0, maxResults);
            // 显示排序选项
            if (sortOptionsElement) {
                sortOptionsElement.style.display = 'flex';
            }
            // 显示结果
            displayResults(currentVideos, resultsElement);
        } else {
            resultsElement.innerHTML = '<div class="no-results">未找到相关视频</div>';
            // 隐藏排序选项
            if (sortOptionsElement) {
                sortOptionsElement.style.display = 'none';
            }
            
            if (!response.ok && data.error) {
                alert("搜索失败: " + data.error);
            }
        }
    } catch (error) {
        console.error("搜索出错:", error);
        alert("搜索出错: " + error.message);
        
        // 隐藏加载中
        const loadingElement = document.getElementById('loading');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }
}

// 显示结果
function displayResults(videos, container) {
    currentVideos = videos;
    const totalPages = Math.ceil(videos.length / videosPerPage);
    
    // 显示分页控件
    displayPagination(totalPages);
    
    // 显示当前页的视频
    displayCurrentPage();
}

// 显示当前页的视频
function displayCurrentPage() {
    const container = document.getElementById('results');
    if (!container) return;

    const start = (currentPage - 1) * videosPerPage;
    const end = start + videosPerPage;
    const pageVideos = currentVideos.slice(start, end);

    let html = '<div class="video-grid">';
    
    pageVideos.forEach(video => {
        const thumbnail = video.thumbnails ? 
            (video.thumbnails.maxres || 
             video.thumbnails.high || 
             video.thumbnails.medium || 
             video.thumbnails.default).url :
            'https://via.placeholder.com/480x360.png?text=No+Thumbnail';

        html += `
            <div class="video-card">
                <div class="thumbnail-container">
                    <a href="${video.url}" target="_blank">
                        <img src="${thumbnail}" alt="${escapeHTML(video.title)}" class="video-thumbnail">
                    </a>
                </div>
                <div class="video-content">
                    <h3><a href="${video.url}" target="_blank">${escapeHTML(video.title)}</a></h3>
                    <div class="video-info">
                        <p>${escapeHTML(video.channelTitle)}</p>
                        <p>发布时间: ${video.publishedAt}</p>
                        <p class="stats">
                            <span title="观看次数"><i class="fas fa-eye"></i> ${formatNumber(video.viewCount)}</span>
                            <span title="点赞数"><i class="fas fa-thumbs-up"></i> ${formatNumber(video.likeCount)}</span>
                            <span title="评论数"><i class="fas fa-comments"></i> ${formatNumber(video.commentCount)}</span>
                        </p>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// 显示分页控件
function displayPagination(totalPages) {
    const paginationContainer = document.getElementById('pagination');
    if (!paginationContainer) return;

    let html = '<div class="pagination">';
    
    // 上一页按钮
    html += `<button onclick="changePage(${currentPage - 1})" class="page-btn" ${currentPage === 1 ? 'disabled' : ''}>
        <i class="fas fa-chevron-left"></i> 上一页
    </button>`;

    // 页码按钮
    for (let i = 1; i <= totalPages; i++) {
        html += `<button onclick="changePage(${i})" class="page-btn ${currentPage === i ? 'active' : ''}">${i}</button>`;
    }

    // 下一页按钮
    html += `<button onclick="changePage(${currentPage + 1})" class="page-btn" ${currentPage === totalPages ? 'disabled' : ''}>
        下一页 <i class="fas fa-chevron-right"></i>
    </button>`;

    html += '</div>';
    paginationContainer.innerHTML = html;
}

// 切换页面
function changePage(page) {
    const totalPages = Math.ceil(currentVideos.length / videosPerPage);
    if (page < 1 || page > totalPages) return;
    
    currentPage = page;
    displayCurrentPage();
    displayPagination(totalPages);
    
    // 滚动到页面顶部
    window.scrollTo({
        top: document.getElementById('results').offsetTop,
        behavior: 'smooth'
    });
}

// HTML安全转义
function escapeHTML(text) {
    if (!text) return '';
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// 数字格式化
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

// 获取当前API密钥
function getApiKey() {
    return document.getElementById('apiKey').value.trim() || localStorage.getItem('youtube_api_key');
}

// 获取代理设置
function getUseProxy() {
    const useProxy = document.getElementById('useProxy').checked;
    localStorage.setItem('useProxy', useProxy);
    return useProxy;
}

// 测试连接
async function testConnection() {
    showLoading(true);
    hideError();
    
    try {
        const response = await fetch('/connection_test');
        const data = await response.json();
        
        if (data.status === 'success') {
            showMessage(data.message, 'success');
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('网络测试失败: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// 显示错误信息
function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.innerHTML = message.replace(/\n/g, '<br>');
    errorDiv.style.display = 'block';
    errorDiv.className = 'error';
    console.error("错误:", message);
}

// 隐藏错误信息
function hideError() {
    document.getElementById('error').style.display = 'none';
}

// 排序视频
function sortVideos(sortBy) {
    if (!currentVideos.length) return;
    
    // 更新按钮状态
    const buttons = document.querySelectorAll('.sort-btn');
    buttons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.onclick.toString().includes(sortBy)) {
            btn.classList.add('active');
        }
    });
    
    const sortedVideos = [...currentVideos];
    
    switch (sortBy) {
        case 'date':
            sortedVideos.sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt));
            break;
        case 'viewCount':
            sortedVideos.sort((a, b) => b.viewCount - a.viewCount);
            break;
        case 'likeCount':
            sortedVideos.sort((a, b) => b.likeCount - a.likeCount);
            break;
        case 'commentCount':
            sortedVideos.sort((a, b) => b.commentCount - a.commentCount);
            break;
    }
    
    // 重置到第一页并显示结果
    currentPage = 1;
    currentVideos = sortedVideos;
    displayCurrentPage();
    displayPagination(Math.ceil(sortedVideos.length / videosPerPage));
} 