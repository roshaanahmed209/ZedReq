let currentUser = null;
let searchTimeout = null;

async function loadUser() {
    try {
        const response = await fetch('/api/user');
        if (response.ok) {
            currentUser = await response.json();
            document.getElementById('profileName').textContent = currentUser.full_name || currentUser.username;
            document.getElementById('profileHeadline').textContent = currentUser.headline || 'No headline yet';
            document.getElementById('profileBio').textContent = currentUser.bio || 'No bio yet';
            const avatar = document.getElementById('profileAvatar');
            avatar.textContent = currentUser.full_name ? currentUser.full_name.charAt(0).toUpperCase() : '👤';
        }
    } catch (error) {
        console.error('Error loading user:', error);
    }
}

async function loadPosts() {
    try {
        const response = await fetch('/api/posts');
        if (!response.ok) throw new Error('Failed to load posts');
        
        const posts = await response.json();
        const container = document.getElementById('postsContainer');
        
        if (posts.length === 0) {
            container.innerHTML = '<div class="loading">No posts yet. Be the first to share!</div>';
            return;
        }
        
        container.innerHTML = posts.map(post => createPostHTML(post)).join('');
        
        document.querySelectorAll('.like-btn').forEach(btn => {
            btn.addEventListener('click', handleLike);
        });
    } catch (error) {
        console.error('Error loading posts:', error);
        document.getElementById('postsContainer').innerHTML = 
            '<div class="loading">Error loading posts. Please refresh.</div>';
    }
}

function createPostHTML(post) {
    const timeAgo = getTimeAgo(post.created_at);
    const initial = post.full_name ? post.full_name.charAt(0).toUpperCase() : '👤';
    const likeClass = post.is_liked ? 'liked' : '';
    
    return `
        <div class="post">
            <div class="post-header">
                <div class="post-avatar">${initial}</div>
                <div class="post-info">
                    <h4>${post.full_name || post.username}</h4>
                    <div class="post-username">@${post.username}</div>
                    <div class="post-time">${timeAgo}</div>
                </div>
            </div>
            <div class="post-content">${escapeHtml(post.content)}</div>
            <div class="post-actions">
                <button class="post-action like-btn ${likeClass}" data-post-id="${post.id}">
                    ${post.is_liked ? '❤️' : '🤍'} <span class="like-count">${post.like_count}</span>
                </button>
            </div>
        </div>
    `;
}

async function handleLike(e) {
    const postId = e.currentTarget.dataset.postId;
    
    try {
        const response = await fetch(`/api/posts/${postId}/like`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const data = await response.json();
            const btn = e.currentTarget;
            const countSpan = btn.querySelector('.like-count');
            
            countSpan.textContent = data.like_count;
            
            if (btn.classList.contains('liked')) {
                btn.classList.remove('liked');
                btn.innerHTML = `🤍 <span class="like-count">${data.like_count}</span>`;
            } else {
                btn.classList.add('liked');
                btn.innerHTML = `❤️ <span class="like-count">${data.like_count}</span>`;
            }
        }
    } catch (error) {
        console.error('Error toggling like:', error);
    }
}

async function createPost() {
    const content = document.getElementById('postContent').value.trim();
    
    if (!content) {
        alert('Please enter some content');
        return;
    }
    
    try {
        const response = await fetch('/api/posts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });
        
        if (response.ok) {
            document.getElementById('postContent').value = '';
            loadPosts();
        }
    } catch (error) {
        console.error('Error creating post:', error);
        alert('Failed to create post');
    }
}

async function searchUsers(query) {
    if (!query.trim()) {
        document.getElementById('searchResults').style.display = 'none';
        return;
    }
    
    try {
        const response = await fetch(`/api/users/search?q=${encodeURIComponent(query)}`);
        const users = await response.json();
        
        const resultsDiv = document.getElementById('searchResults');
        
        if (users.length === 0) {
            resultsDiv.innerHTML = '<div class="search-result-item">No users found</div>';
        } else {
            resultsDiv.innerHTML = users.map(user => `
                <div class="search-result-item">
                    <div class="search-result-avatar">${user.full_name ? user.full_name.charAt(0).toUpperCase() : '👤'}</div>
                    <div>
                        <div><strong>${user.full_name || user.username}</strong></div>
                        <div style="font-size: 0.85em; color: #999;">@${user.username}</div>
                    </div>
                </div>
            `).join('');
        }
        
        resultsDiv.style.display = 'block';
    } catch (error) {
        console.error('Error searching users:', error);
    }
}

function getTimeAgo(dateString) {
    const now = new Date();
    const date = new Date(dateString);
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

document.addEventListener('DOMContentLoaded', () => {
    // Add page load animation
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.6s ease-in';
    
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 100);
    
    loadUser();
    loadPosts();
    
    document.getElementById('createPostBtn').addEventListener('click', createPost);
    document.getElementById('postContent').addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            createPost();
        }
    });
    
    document.getElementById('searchInput').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            searchUsers(e.target.value);
        }, 300);
    });
    
    document.getElementById('logoutBtn').addEventListener('click', () => {
        // Add smooth page transition
        document.body.style.transition = 'opacity 0.5s ease-out';
        document.body.style.opacity = '0';
        
        setTimeout(() => {
            window.location.href = '/logout';
        }, 500);
    });
    
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.nav-center')) {
            document.getElementById('searchResults').style.display = 'none';
        }
    });
});
