#!/bin/bash
# ============================================
# Friendzone Social Media App - Auto Builder
# Commits new code every hour automatically
# ============================================

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"

INTERVAL=3600  # seconds (1 hour)
STEP=0

# Read step from tracker file if resuming
if [ -f ".build_step" ]; then
    STEP=$(cat .build_step)
fi

commit_step() {
    local msg="$1"
    git add -A
    git commit -m "$msg"
    STEP=$((STEP + 1))
    echo "$STEP" > .build_step
    echo "[$(date)] Committed: $msg (step $STEP)"
}

while true; do
    case $STEP in

    0)
        # --- Initial project structure ---
        cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FriendZone - Connect With Friends</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div id="app">
        <header class="navbar">
            <h1 class="logo">FriendZone</h1>
            <nav>
                <a href="#" id="nav-home">Home</a>
                <a href="#" id="nav-profile">Profile</a>
                <a href="#" id="nav-login">Login</a>
            </nav>
        </header>
        <main id="main-content">
            <h2>Welcome to FriendZone</h2>
            <p>Connect, share, and stay in touch with your friends.</p>
        </main>
    </div>
    <script src="js/app.js"></script>
</body>
</html>
EOF
        mkdir -p css js
        cat > css/style.css << 'EOF'
/* FriendZone - Base Styles */
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #f0f2f5;
    color: #1c1e21;
}

.navbar {
    background: #4a90d9;
    color: white;
    padding: 12px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.navbar .logo { font-size: 1.5rem; }

.navbar nav a {
    color: white;
    text-decoration: none;
    margin-left: 16px;
    font-weight: 500;
}

#main-content {
    max-width: 680px;
    margin: 24px auto;
    padding: 0 16px;
}
EOF
        cat > js/app.js << 'EOF'
// FriendZone App - Entry Point
console.log("FriendZone app loaded");

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM ready");
});
EOF
        cat > README.md << 'EOF'
# FriendZone

A social media app to connect with friends.

## Features (planned)
- User authentication
- News feed with posts
- Friend requests
- Messaging
- Profile pages
- Notifications
EOF
        commit_step "Initial project setup with HTML, CSS, JS scaffold"
        ;;

    1)
        # --- Login / Signup page ---
        cat > js/auth.js << 'EOF'
// FriendZone - Authentication Module
const Auth = {
    currentUser: null,

    renderLoginForm() {
        return `
            <div class="auth-container">
                <h2>Login to FriendZone</h2>
                <form id="login-form">
                    <input type="email" id="login-email" placeholder="Email" required>
                    <input type="password" id="login-password" placeholder="Password" required>
                    <button type="submit" class="btn btn-primary">Log In</button>
                </form>
                <p class="auth-switch">Don't have an account? <a href="#" id="show-signup">Sign Up</a></p>
            </div>
        `;
    },

    renderSignupForm() {
        return `
            <div class="auth-container">
                <h2>Join FriendZone</h2>
                <form id="signup-form">
                    <input type="text" id="signup-name" placeholder="Full Name" required>
                    <input type="email" id="signup-email" placeholder="Email" required>
                    <input type="password" id="signup-password" placeholder="Password" required>
                    <input type="password" id="signup-confirm" placeholder="Confirm Password" required>
                    <button type="submit" class="btn btn-primary">Sign Up</button>
                </form>
                <p class="auth-switch">Already have an account? <a href="#" id="show-login">Log In</a></p>
            </div>
        `;
    },

    login(email, password) {
        const users = JSON.parse(localStorage.getItem("fz_users") || "[]");
        const user = users.find(u => u.email === email && u.password === password);
        if (user) {
            this.currentUser = user;
            localStorage.setItem("fz_session", JSON.stringify(user));
            return { success: true, user };
        }
        return { success: false, error: "Invalid email or password" };
    },

    signup(name, email, password) {
        const users = JSON.parse(localStorage.getItem("fz_users") || "[]");
        if (users.find(u => u.email === email)) {
            return { success: false, error: "Email already registered" };
        }
        const newUser = {
            id: Date.now().toString(),
            name,
            email,
            password,
            avatar: null,
            bio: "",
            friends: [],
            createdAt: new Date().toISOString()
        };
        users.push(newUser);
        localStorage.setItem("fz_users", JSON.stringify(users));
        this.currentUser = newUser;
        localStorage.setItem("fz_session", JSON.stringify(newUser));
        return { success: true, user: newUser };
    },

    logout() {
        this.currentUser = null;
        localStorage.removeItem("fz_session");
    },

    checkSession() {
        const session = localStorage.getItem("fz_session");
        if (session) {
            this.currentUser = JSON.parse(session);
            return true;
        }
        return false;
    }
};
EOF
        cat >> css/style.css << 'EOF'

/* Auth Forms */
.auth-container {
    max-width: 400px;
    margin: 60px auto;
    padding: 32px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.auth-container h2 { margin-bottom: 20px; text-align: center; }

.auth-container input {
    width: 100%;
    padding: 12px;
    margin-bottom: 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
}

.btn {
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
}

.btn-primary {
    background: #4a90d9;
    color: white;
    width: 100%;
    padding: 12px;
}

.btn-primary:hover { background: #3a7bc8; }

.auth-switch {
    text-align: center;
    margin-top: 16px;
    color: #666;
}

.auth-switch a { color: #4a90d9; text-decoration: none; }
EOF
        commit_step "Add authentication module with login and signup forms"
        ;;

    2)
        # --- Post feed ---
        cat > js/feed.js << 'EOF'
// FriendZone - News Feed Module
const Feed = {
    getPosts() {
        return JSON.parse(localStorage.getItem("fz_posts") || "[]")
            .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    },

    createPost(userId, userName, content) {
        const posts = this.getPosts();
        const post = {
            id: Date.now().toString(),
            userId,
            userName,
            content,
            likes: [],
            comments: [],
            createdAt: new Date().toISOString()
        };
        posts.unshift(post);
        localStorage.setItem("fz_posts", JSON.stringify(posts));
        return post;
    },

    likePost(postId, userId) {
        const posts = this.getPosts();
        const post = posts.find(p => p.id === postId);
        if (!post) return null;
        const idx = post.likes.indexOf(userId);
        if (idx === -1) {
            post.likes.push(userId);
        } else {
            post.likes.splice(idx, 1);
        }
        localStorage.setItem("fz_posts", JSON.stringify(posts));
        return post;
    },

    renderFeed(currentUserId) {
        const posts = this.getPosts();
        if (posts.length === 0) {
            return '<div class="empty-feed"><p>No posts yet. Be the first to share!</p></div>';
        }
        return posts.map(post => this.renderPost(post, currentUserId)).join("");
    },

    renderPost(post, currentUserId) {
        const liked = post.likes.includes(currentUserId);
        const timeAgo = this.timeAgo(new Date(post.createdAt));
        return `
            <div class="post-card" data-post-id="${post.id}">
                <div class="post-header">
                    <div class="post-avatar">${post.userName.charAt(0)}</div>
                    <div>
                        <strong>${post.userName}</strong>
                        <span class="post-time">${timeAgo}</span>
                    </div>
                </div>
                <div class="post-content">${post.content}</div>
                <div class="post-actions">
                    <button class="btn-like ${liked ? 'liked' : ''}" data-id="${post.id}">
                        ${liked ? '❤️' : '🤍'} ${post.likes.length}
                    </button>
                    <button class="btn-comment" data-id="${post.id}">
                        💬 ${post.comments.length}
                    </button>
                </div>
            </div>
        `;
    },

    renderCreatePost() {
        return `
            <div class="create-post">
                <textarea id="post-input" placeholder="What's on your mind?" rows="3"></textarea>
                <button class="btn btn-primary" id="submit-post">Post</button>
            </div>
        `;
    },

    timeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);
        if (seconds < 60) return "just now";
        if (seconds < 3600) return Math.floor(seconds / 60) + "m ago";
        if (seconds < 86400) return Math.floor(seconds / 3600) + "h ago";
        return Math.floor(seconds / 86400) + "d ago";
    }
};
EOF
        cat >> css/style.css << 'EOF'

/* Feed & Posts */
.create-post {
    background: white;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}

.create-post textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    resize: vertical;
    font-family: inherit;
    font-size: 14px;
    margin-bottom: 8px;
}

.post-card {
    background: white;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}

.post-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
}

.post-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #4a90d9;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 18px;
}

.post-time { color: #999; font-size: 12px; margin-left: 8px; }

.post-content { margin-bottom: 12px; line-height: 1.5; }

.post-actions {
    display: flex;
    gap: 12px;
    border-top: 1px solid #eee;
    padding-top: 8px;
}

.post-actions button {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 14px;
    padding: 4px 8px;
    border-radius: 4px;
}

.post-actions button:hover { background: #f0f2f5; }

.btn-like.liked { color: #e74c3c; }

.empty-feed { text-align: center; padding: 40px; color: #999; }
EOF
        commit_step "Add news feed with post creation, likes, and time display"
        ;;

    3)
        # --- Profile page ---
        cat > js/profile.js << 'EOF'
// FriendZone - Profile Module
const Profile = {
    renderProfile(user, isOwn) {
        return `
            <div class="profile-page">
                <div class="profile-header">
                    <div class="profile-avatar-lg">${user.name.charAt(0)}</div>
                    <h2>${user.name}</h2>
                    <p class="profile-bio">${user.bio || "No bio yet."}</p>
                    <div class="profile-stats">
                        <div class="stat"><strong>${user.friends.length}</strong><span>Friends</span></div>
                        <div class="stat"><strong>${this.getPostCount(user.id)}</strong><span>Posts</span></div>
                    </div>
                    ${isOwn ? '<button class="btn btn-secondary" id="edit-profile">Edit Profile</button>' : ''}
                </div>
                <div class="profile-posts">
                    <h3>Posts</h3>
                    ${this.getUserPosts(user.id)}
                </div>
            </div>
        `;
    },

    getPostCount(userId) {
        const posts = JSON.parse(localStorage.getItem("fz_posts") || "[]");
        return posts.filter(p => p.userId === userId).length;
    },

    getUserPosts(userId) {
        const posts = JSON.parse(localStorage.getItem("fz_posts") || "[]")
            .filter(p => p.userId === userId)
            .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
        if (posts.length === 0) return '<p class="empty-feed">No posts yet.</p>';
        return posts.map(p => Feed.renderPost(p, userId)).join("");
    },

    renderEditProfile(user) {
        return `
            <div class="auth-container">
                <h2>Edit Profile</h2>
                <form id="edit-profile-form">
                    <input type="text" id="edit-name" value="${user.name}" placeholder="Full Name" required>
                    <textarea id="edit-bio" placeholder="Write a bio..." rows="3">${user.bio || ""}</textarea>
                    <button type="submit" class="btn btn-primary">Save Changes</button>
                    <button type="button" class="btn btn-secondary" id="cancel-edit">Cancel</button>
                </form>
            </div>
        `;
    },

    updateProfile(userId, name, bio) {
        const users = JSON.parse(localStorage.getItem("fz_users") || "[]");
        const user = users.find(u => u.id === userId);
        if (user) {
            user.name = name;
            user.bio = bio;
            localStorage.setItem("fz_users", JSON.stringify(users));
            localStorage.setItem("fz_session", JSON.stringify(user));
            return user;
        }
        return null;
    }
};
EOF
        cat >> css/style.css << 'EOF'

/* Profile Page */
.profile-page { max-width: 680px; margin: 0 auto; }

.profile-header {
    background: white;
    padding: 32px;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}

.profile-avatar-lg {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: #4a90d9;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 36px;
    font-weight: bold;
    margin: 0 auto 12px;
}

.profile-bio { color: #666; margin: 8px 0 16px; }

.profile-stats {
    display: flex;
    justify-content: center;
    gap: 40px;
    margin-bottom: 16px;
}

.profile-stats .stat { text-align: center; }
.profile-stats .stat span { display: block; color: #999; font-size: 13px; }

.btn-secondary {
    background: #e4e6eb;
    color: #1c1e21;
}

.btn-secondary:hover { background: #d4d6db; }

.profile-posts h3 { margin-bottom: 12px; }
EOF
        commit_step "Add user profile page with stats, bio, and edit functionality"
        ;;

    4)
        # --- Friends system ---
        cat > js/friends.js << 'EOF'
// FriendZone - Friends Module
const Friends = {
    sendRequest(fromId, toId) {
        const requests = JSON.parse(localStorage.getItem("fz_friend_requests") || "[]");
        if (requests.find(r => r.from === fromId && r.to === toId)) {
            return { success: false, error: "Request already sent" };
        }
        requests.push({
            id: Date.now().toString(),
            from: fromId,
            to: toId,
            status: "pending",
            createdAt: new Date().toISOString()
        });
        localStorage.setItem("fz_friend_requests", JSON.stringify(requests));
        return { success: true };
    },

    acceptRequest(requestId) {
        const requests = JSON.parse(localStorage.getItem("fz_friend_requests") || "[]");
        const req = requests.find(r => r.id === requestId);
        if (!req) return false;

        req.status = "accepted";
        localStorage.setItem("fz_friend_requests", JSON.stringify(requests));

        const users = JSON.parse(localStorage.getItem("fz_users") || "[]");
        const fromUser = users.find(u => u.id === req.from);
        const toUser = users.find(u => u.id === req.to);
        if (fromUser && toUser) {
            fromUser.friends.push(req.to);
            toUser.friends.push(req.from);
            localStorage.setItem("fz_users", JSON.stringify(users));
        }
        return true;
    },

    declineRequest(requestId) {
        let requests = JSON.parse(localStorage.getItem("fz_friend_requests") || "[]");
        requests = requests.filter(r => r.id !== requestId);
        localStorage.setItem("fz_friend_requests", JSON.stringify(requests));
    },

    getPendingRequests(userId) {
        const requests = JSON.parse(localStorage.getItem("fz_friend_requests") || "[]");
        return requests.filter(r => r.to === userId && r.status === "pending");
    },

    getFriendsList(userId) {
        const users = JSON.parse(localStorage.getItem("fz_users") || "[]");
        const user = users.find(u => u.id === userId);
        if (!user) return [];
        return users.filter(u => user.friends.includes(u.id));
    },

    renderFriendsList(userId) {
        const friends = this.getFriendsList(userId);
        if (friends.length === 0) {
            return '<div class="empty-feed"><p>No friends yet. Start connecting!</p></div>';
        }
        return `
            <div class="friends-grid">
                ${friends.map(f => `
                    <div class="friend-card">
                        <div class="post-avatar">${f.name.charAt(0)}</div>
                        <strong>${f.name}</strong>
                        <button class="btn btn-secondary btn-sm" data-user-id="${f.id}">View Profile</button>
                    </div>
                `).join("")}
            </div>
        `;
    },

    renderPendingRequests(userId) {
        const requests = this.getPendingRequests(userId);
        const users = JSON.parse(localStorage.getItem("fz_users") || "[]");
        if (requests.length === 0) return '<p>No pending requests.</p>';
        return requests.map(r => {
            const from = users.find(u => u.id === r.from);
            return `
                <div class="friend-request">
                    <div class="post-avatar">${from ? from.name.charAt(0) : "?"}</div>
                    <span>${from ? from.name : "Unknown"} wants to be your friend</span>
                    <button class="btn btn-primary btn-sm" data-accept="${r.id}">Accept</button>
                    <button class="btn btn-secondary btn-sm" data-decline="${r.id}">Decline</button>
                </div>
            `;
        }).join("");
    }
};
EOF
        cat >> css/style.css << 'EOF'

/* Friends */
.friends-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 12px;
}

.friend-card {
    background: white;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}

.friend-card .post-avatar { margin: 0 auto 8px; }

.friend-request {
    display: flex;
    align-items: center;
    gap: 12px;
    background: white;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 8px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}

.btn-sm { padding: 6px 12px; font-size: 12px; }
EOF
        commit_step "Add friends system with requests, accept/decline, and friends list"
        ;;

    5)
        # --- Comments on posts ---
        cat > js/comments.js << 'EOF'
// FriendZone - Comments Module
const Comments = {
    addComment(postId, userId, userName, text) {
        const posts = JSON.parse(localStorage.getItem("fz_posts") || "[]");
        const post = posts.find(p => p.id === postId);
        if (!post) return null;

        const comment = {
            id: Date.now().toString(),
            userId,
            userName,
            text,
            createdAt: new Date().toISOString()
        };
        post.comments.push(comment);
        localStorage.setItem("fz_posts", JSON.stringify(posts));
        return comment;
    },

    deleteComment(postId, commentId, userId) {
        const posts = JSON.parse(localStorage.getItem("fz_posts") || "[]");
        const post = posts.find(p => p.id === postId);
        if (!post) return false;
        const idx = post.comments.findIndex(c => c.id === commentId && c.userId === userId);
        if (idx === -1) return false;
        post.comments.splice(idx, 1);
        localStorage.setItem("fz_posts", JSON.stringify(posts));
        return true;
    },

    renderComments(postId, currentUserId) {
        const posts = JSON.parse(localStorage.getItem("fz_posts") || "[]");
        const post = posts.find(p => p.id === postId);
        if (!post || post.comments.length === 0) {
            return '<p class="no-comments">No comments yet.</p>';
        }
        return post.comments.map(c => `
            <div class="comment">
                <div class="comment-avatar">${c.userName.charAt(0)}</div>
                <div class="comment-body">
                    <strong>${c.userName}</strong>
                    <p>${c.text}</p>
                    <span class="post-time">${Feed.timeAgo(new Date(c.createdAt))}</span>
                </div>
                ${c.userId === currentUserId ? `<button class="comment-delete" data-post="${postId}" data-comment="${c.id}">✕</button>` : ''}
            </div>
        `).join("");
    },

    renderCommentForm(postId) {
        return `
            <div class="comment-form">
                <input type="text" class="comment-input" data-post="${postId}" placeholder="Write a comment...">
                <button class="btn btn-primary btn-sm comment-submit" data-post="${postId}">Send</button>
            </div>
        `;
    }
};
EOF
        cat >> css/style.css << 'EOF'

/* Comments */
.comment {
    display: flex;
    gap: 8px;
    padding: 8px 0;
    align-items: flex-start;
}

.comment-avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #ccc;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    flex-shrink: 0;
}

.comment-body {
    background: #f0f2f5;
    padding: 8px 12px;
    border-radius: 12px;
    flex: 1;
}

.comment-body p { margin: 4px 0; font-size: 14px; }

.comment-delete {
    background: none;
    border: none;
    color: #999;
    cursor: pointer;
}

.comment-form {
    display: flex;
    gap: 8px;
    margin-top: 8px;
}

.comment-input {
    flex: 1;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 20px;
    font-size: 13px;
}

.no-comments { color: #999; font-size: 13px; padding: 8px 0; }
EOF
        commit_step "Add commenting system with add, delete, and display"
        ;;

    6)
        # --- Messaging system ---
        cat > js/messaging.js << 'EOF'
// FriendZone - Messaging Module
const Messaging = {
    getConversations(userId) {
        const messages = JSON.parse(localStorage.getItem("fz_messages") || "[]");
        const convos = {};
        messages.forEach(m => {
            if (m.from === userId || m.to === userId) {
                const otherId = m.from === userId ? m.to : m.from;
                if (!convos[otherId]) {
                    convos[otherId] = { userId: otherId, messages: [], lastMessage: null };
                }
                convos[otherId].messages.push(m);
                if (!convos[otherId].lastMessage || new Date(m.createdAt) > new Date(convos[otherId].lastMessage.createdAt)) {
                    convos[otherId].lastMessage = m;
                }
            }
        });
        return Object.values(convos).sort((a, b) =>
            new Date(b.lastMessage.createdAt) - new Date(a.lastMessage.createdAt)
        );
    },

    sendMessage(fromId, toId, text) {
        const messages = JSON.parse(localStorage.getItem("fz_messages") || "[]");
        const msg = {
            id: Date.now().toString(),
            from: fromId,
            to: toId,
            text,
            read: false,
            createdAt: new Date().toISOString()
        };
        messages.push(msg);
        localStorage.setItem("fz_messages", JSON.stringify(messages));
        return msg;
    },

    getThread(userId, otherUserId) {
        const messages = JSON.parse(localStorage.getItem("fz_messages") || "[]");
        return messages
            .filter(m => (m.from === userId && m.to === otherUserId) || (m.from === otherUserId && m.to === userId))
            .sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
    },

    getUnreadCount(userId) {
        const messages = JSON.parse(localStorage.getItem("fz_messages") || "[]");
        return messages.filter(m => m.to === userId && !m.read).length;
    },

    markAsRead(userId, otherUserId) {
        const messages = JSON.parse(localStorage.getItem("fz_messages") || "[]");
        messages.forEach(m => {
            if (m.from === otherUserId && m.to === userId && !m.read) {
                m.read = true;
            }
        });
        localStorage.setItem("fz_messages", JSON.stringify(messages));
    },

    renderInbox(userId) {
        const convos = this.getConversations(userId);
        const users = JSON.parse(localStorage.getItem("fz_users") || "[]");
        if (convos.length === 0) {
            return '<div class="empty-feed"><p>No messages yet.</p></div>';
        }
        return `<div class="inbox">${convos.map(c => {
            const other = users.find(u => u.id === c.userId);
            const unread = c.messages.filter(m => m.to === userId && !m.read).length;
            return `
                <div class="inbox-item" data-user="${c.userId}">
                    <div class="post-avatar">${other ? other.name.charAt(0) : "?"}</div>
                    <div class="inbox-preview">
                        <strong>${other ? other.name : "Unknown"}</strong>
                        ${unread > 0 ? `<span class="badge">${unread}</span>` : ''}
                        <p>${c.lastMessage.text.substring(0, 50)}...</p>
                    </div>
                </div>
            `;
        }).join("")}</div>`;
    },

    renderThread(userId, otherUserId) {
        const thread = this.getThread(userId, otherUserId);
        const users = JSON.parse(localStorage.getItem("fz_users") || "[]");
        const other = users.find(u => u.id === otherUserId);
        return `
            <div class="chat-header">
                <button class="btn btn-secondary btn-sm" id="back-to-inbox">← Back</button>
                <strong>${other ? other.name : "Unknown"}</strong>
            </div>
            <div class="chat-messages">
                ${thread.map(m => `
                    <div class="chat-bubble ${m.from === userId ? 'sent' : 'received'}">
                        <p>${m.text}</p>
                        <span class="post-time">${Feed.timeAgo(new Date(m.createdAt))}</span>
                    </div>
                `).join("")}
            </div>
            <div class="chat-input">
                <input type="text" id="msg-input" placeholder="Type a message...">
                <button class="btn btn-primary btn-sm" id="send-msg" data-to="${otherUserId}">Send</button>
            </div>
        `;
    }
};
EOF
        cat >> css/style.css << 'EOF'

/* Messaging */
.inbox-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: white;
    border-radius: 8px;
    margin-bottom: 4px;
    cursor: pointer;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.inbox-item:hover { background: #f7f8fa; }

.inbox-preview { flex: 1; }
.inbox-preview p { color: #999; font-size: 13px; margin-top: 2px; }

.badge {
    background: #e74c3c;
    color: white;
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 11px;
    margin-left: 8px;
}

.chat-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: white;
    border-radius: 8px 8px 0 0;
    border-bottom: 1px solid #eee;
}

.chat-messages {
    background: white;
    padding: 16px;
    min-height: 300px;
    max-height: 400px;
    overflow-y: auto;
}

.chat-bubble {
    max-width: 70%;
    padding: 10px 14px;
    border-radius: 16px;
    margin-bottom: 8px;
}

.chat-bubble.sent {
    background: #4a90d9;
    color: white;
    margin-left: auto;
    border-bottom-right-radius: 4px;
}

.chat-bubble.received {
    background: #f0f2f5;
    border-bottom-left-radius: 4px;
}

.chat-bubble .post-time { font-size: 10px; opacity: 0.7; }

.chat-input {
    display: flex;
    gap: 8px;
    padding: 12px;
    background: white;
    border-radius: 0 0 8px 8px;
    border-top: 1px solid #eee;
}

.chat-input input {
    flex: 1;
    padding: 10px 14px;
    border: 1px solid #ddd;
    border-radius: 20px;
}
EOF
        commit_step "Add direct messaging with inbox, threads, and unread badges"
        ;;

    7)
        # --- Notifications ---
        cat > js/notifications.js << 'EOF'
// FriendZone - Notifications Module
const Notifications = {
    add(userId, type, message, relatedId) {
        const notifs = JSON.parse(localStorage.getItem("fz_notifications") || "[]");
        notifs.unshift({
            id: Date.now().toString(),
            userId,
            type,
            message,
            relatedId,
            read: false,
            createdAt: new Date().toISOString()
        });
        localStorage.setItem("fz_notifications", JSON.stringify(notifs));
    },

    getForUser(userId) {
        const notifs = JSON.parse(localStorage.getItem("fz_notifications") || "[]");
        return notifs.filter(n => n.userId === userId);
    },

    getUnreadCount(userId) {
        return this.getForUser(userId).filter(n => !n.read).length;
    },

    markAllRead(userId) {
        const notifs = JSON.parse(localStorage.getItem("fz_notifications") || "[]");
        notifs.forEach(n => {
            if (n.userId === userId) n.read = true;
        });
        localStorage.setItem("fz_notifications", JSON.stringify(notifs));
    },

    renderNotifications(userId) {
        const notifs = this.getForUser(userId);
        if (notifs.length === 0) {
            return '<div class="empty-feed"><p>No notifications.</p></div>';
        }
        return `<div class="notif-list">${notifs.map(n => `
            <div class="notif-item ${n.read ? '' : 'unread'}">
                <div class="notif-icon">${this.getIcon(n.type)}</div>
                <div class="notif-body">
                    <p>${n.message}</p>
                    <span class="post-time">${Feed.timeAgo(new Date(n.createdAt))}</span>
                </div>
            </div>
        `).join("")}</div>`;
    },

    getIcon(type) {
        const icons = {
            like: "❤️",
            comment: "💬",
            friend_request: "👥",
            friend_accept: "🤝",
            message: "✉️"
        };
        return icons[type] || "🔔";
    }
};
EOF
        cat >> css/style.css << 'EOF'

/* Notifications */
.notif-list { max-width: 500px; }

.notif-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: white;
    border-radius: 8px;
    margin-bottom: 4px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.notif-item.unread { background: #e8f0fe; }

.notif-icon { font-size: 20px; }

.notif-body p { margin: 0; font-size: 14px; }
EOF
        commit_step "Add notification system with types, icons, and unread tracking"
        ;;

    8)
        # --- Search functionality ---
        cat > js/search.js << 'EOF'
// FriendZone - Search Module
const Search = {
    searchUsers(query) {
        const users = JSON.parse(localStorage.getItem("fz_users") || "[]");
        const q = query.toLowerCase();
        return users.filter(u =>
            u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)
        );
    },

    searchPosts(query) {
        const posts = JSON.parse(localStorage.getItem("fz_posts") || "[]");
        const q = query.toLowerCase();
        return posts.filter(p => p.content.toLowerCase().includes(q));
    },

    renderSearchPage() {
        return `
            <div class="search-page">
                <div class="search-bar">
                    <input type="text" id="search-input" placeholder="Search people or posts...">
                    <button class="btn btn-primary" id="search-btn">Search</button>
                </div>
                <div id="search-results"></div>
            </div>
        `;
    },

    renderResults(query) {
        const users = this.searchUsers(query);
        const posts = this.searchPosts(query);

        let html = '';

        if (users.length > 0) {
            html += `<h3>People</h3><div class="friends-grid">`;
            html += users.map(u => `
                <div class="friend-card">
                    <div class="post-avatar">${u.name.charAt(0)}</div>
                    <strong>${u.name}</strong>
                </div>
            `).join("");
            html += `</div>`;
        }

        if (posts.length > 0) {
            html += `<h3 style="margin-top:16px;">Posts</h3>`;
            html += posts.map(p => Feed.renderPost(p, "")).join("");
        }

        if (users.length === 0 && posts.length === 0) {
            html = '<div class="empty-feed"><p>No results found.</p></div>';
        }

        return html;
    }
};
EOF
        cat >> css/style.css << 'EOF'

/* Search */
.search-bar {
    display: flex;
    gap: 8px;
    margin-bottom: 20px;
}

.search-bar input {
    flex: 1;
    padding: 12px 16px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 15px;
}
EOF
        commit_step "Add search functionality for users and posts"
        ;;

    9)
        # --- Update app.js to wire everything together ---
        cat > js/app.js << 'EOF'
// FriendZone App - Main Controller
const App = {
    init() {
        if (Auth.checkSession()) {
            this.showHome();
            this.updateNavbar(true);
        } else {
            this.showLogin();
            this.updateNavbar(false);
        }
        this.bindNavigation();
    },

    updateNavbar(loggedIn) {
        const nav = document.querySelector(".navbar nav");
        if (loggedIn) {
            const unreadNotifs = Notifications.getUnreadCount(Auth.currentUser.id);
            const unreadMsgs = Messaging.getUnreadCount(Auth.currentUser.id);
            nav.innerHTML = `
                <a href="#" id="nav-home">Home</a>
                <a href="#" id="nav-search">Search</a>
                <a href="#" id="nav-friends">Friends</a>
                <a href="#" id="nav-messages">Messages ${unreadMsgs > 0 ? '<span class="badge">' + unreadMsgs + '</span>' : ''}</a>
                <a href="#" id="nav-notifs">Notifications ${unreadNotifs > 0 ? '<span class="badge">' + unreadNotifs + '</span>' : ''}</a>
                <a href="#" id="nav-profile">Profile</a>
                <a href="#" id="nav-logout">Logout</a>
            `;
        } else {
            nav.innerHTML = '<a href="#" id="nav-login">Login</a>';
        }
        this.bindNavigation();
    },

    bindNavigation() {
        const bind = (id, handler) => {
            const el = document.getElementById(id);
            if (el) el.onclick = (e) => { e.preventDefault(); handler(); };
        };
        bind("nav-home", () => this.showHome());
        bind("nav-login", () => this.showLogin());
        bind("nav-profile", () => this.showProfile());
        bind("nav-friends", () => this.showFriends());
        bind("nav-messages", () => this.showMessages());
        bind("nav-notifs", () => this.showNotifications());
        bind("nav-search", () => this.showSearch());
        bind("nav-logout", () => {
            Auth.logout();
            this.updateNavbar(false);
            this.showLogin();
        });
    },

    setContent(html) {
        document.getElementById("main-content").innerHTML = html;
    },

    showLogin() {
        this.setContent(Auth.renderLoginForm());
        document.getElementById("login-form").onsubmit = (e) => {
            e.preventDefault();
            const email = document.getElementById("login-email").value;
            const password = document.getElementById("login-password").value;
            const result = Auth.login(email, password);
            if (result.success) {
                this.updateNavbar(true);
                this.showHome();
            } else {
                alert(result.error);
            }
        };
        const showSignup = document.getElementById("show-signup");
        if (showSignup) showSignup.onclick = (e) => { e.preventDefault(); this.showSignup(); };
    },

    showSignup() {
        this.setContent(Auth.renderSignupForm());
        document.getElementById("signup-form").onsubmit = (e) => {
            e.preventDefault();
            const name = document.getElementById("signup-name").value;
            const email = document.getElementById("signup-email").value;
            const pw = document.getElementById("signup-password").value;
            const confirm = document.getElementById("signup-confirm").value;
            if (pw !== confirm) { alert("Passwords don't match"); return; }
            const result = Auth.signup(name, email, pw);
            if (result.success) {
                this.updateNavbar(true);
                this.showHome();
            } else {
                alert(result.error);
            }
        };
        const showLogin = document.getElementById("show-login");
        if (showLogin) showLogin.onclick = (e) => { e.preventDefault(); this.showLogin(); };
    },

    showHome() {
        const user = Auth.currentUser;
        this.setContent(Feed.renderCreatePost() + Feed.renderFeed(user.id));
        document.getElementById("submit-post").onclick = () => {
            const input = document.getElementById("post-input");
            if (input.value.trim()) {
                Feed.createPost(user.id, user.name, input.value.trim());
                this.showHome();
            }
        };
    },

    showProfile() {
        this.setContent(Profile.renderProfile(Auth.currentUser, true));
    },

    showFriends() {
        const user = Auth.currentUser;
        this.setContent(`
            <h2>Friend Requests</h2>
            ${Friends.renderPendingRequests(user.id)}
            <h2 style="margin-top:20px;">My Friends</h2>
            ${Friends.renderFriendsList(user.id)}
        `);
    },

    showMessages() {
        this.setContent(`<h2>Messages</h2>${Messaging.renderInbox(Auth.currentUser.id)}`);
    },

    showNotifications() {
        Notifications.markAllRead(Auth.currentUser.id);
        this.setContent(`<h2>Notifications</h2>${Notifications.renderNotifications(Auth.currentUser.id)}`);
        this.updateNavbar(true);
    },

    showSearch() {
        this.setContent(Search.renderSearchPage());
        document.getElementById("search-btn").onclick = () => {
            const q = document.getElementById("search-input").value.trim();
            if (q) {
                document.getElementById("search-results").innerHTML = Search.renderResults(q);
            }
        };
    }
};

document.addEventListener("DOMContentLoaded", () => App.init());
EOF
        # Update index.html to include all scripts
        cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FriendZone - Connect With Friends</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div id="app">
        <header class="navbar">
            <h1 class="logo">FriendZone</h1>
            <nav>
                <a href="#" id="nav-login">Login</a>
            </nav>
        </header>
        <main id="main-content">
            <h2>Welcome to FriendZone</h2>
            <p>Connect, share, and stay in touch with your friends.</p>
        </main>
        <footer class="footer">
            <p>&copy; 2026 FriendZone. All rights reserved.</p>
        </footer>
    </div>
    <script src="js/auth.js"></script>
    <script src="js/feed.js"></script>
    <script src="js/profile.js"></script>
    <script src="js/friends.js"></script>
    <script src="js/comments.js"></script>
    <script src="js/messaging.js"></script>
    <script src="js/notifications.js"></script>
    <script src="js/search.js"></script>
    <script src="js/app.js"></script>
</body>
</html>
EOF
        cat >> css/style.css << 'EOF'

/* Footer */
.footer {
    text-align: center;
    padding: 24px;
    color: #999;
    font-size: 13px;
    margin-top: 40px;
}
EOF
        commit_step "Wire up all modules in main app controller and update HTML"
        ;;

    10)
        # --- Settings page ---
        cat > js/settings.js << 'EOF'
// FriendZone - Settings Module
const Settings = {
    getPreferences(userId) {
        return JSON.parse(localStorage.getItem(`fz_prefs_${userId}`) || '{}');
    },

    savePreferences(userId, prefs) {
        localStorage.setItem(`fz_prefs_${userId}`, JSON.stringify(prefs));
    },

    renderSettings(userId) {
        const prefs = this.getPreferences(userId);
        return `
            <div class="settings-page">
                <h2>Settings</h2>
                <div class="settings-section">
                    <h3>Privacy</h3>
                    <label class="setting-row">
                        <span>Make profile public</span>
                        <input type="checkbox" id="pref-public" ${prefs.publicProfile ? 'checked' : ''}>
                    </label>
                    <label class="setting-row">
                        <span>Show online status</span>
                        <input type="checkbox" id="pref-online" ${prefs.showOnline !== false ? 'checked' : ''}>
                    </label>
                </div>
                <div class="settings-section">
                    <h3>Notifications</h3>
                    <label class="setting-row">
                        <span>Email notifications</span>
                        <input type="checkbox" id="pref-email-notif" ${prefs.emailNotifs ? 'checked' : ''}>
                    </label>
                    <label class="setting-row">
                        <span>Friend request alerts</span>
                        <input type="checkbox" id="pref-friend-notif" ${prefs.friendNotifs !== false ? 'checked' : ''}>
                    </label>
                </div>
                <div class="settings-section">
                    <h3>Account</h3>
                    <button class="btn btn-secondary" id="change-password">Change Password</button>
                    <button class="btn btn-danger" id="delete-account">Delete Account</button>
                </div>
                <button class="btn btn-primary" id="save-settings">Save Settings</button>
            </div>
        `;
    }
};
EOF
        cat >> css/style.css << 'EOF'

/* Settings */
.settings-page { max-width: 500px; margin: 0 auto; }

.settings-section {
    background: white;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}

.settings-section h3 { margin-bottom: 12px; color: #333; }

.setting-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #f0f0f0;
}

.setting-row:last-child { border-bottom: none; }

.btn-danger {
    background: #e74c3c;
    color: white;
    margin-left: 8px;
}

.btn-danger:hover { background: #c0392b; }
EOF
        commit_step "Add settings page with privacy, notification, and account options"
        ;;

    11)
        # --- Dark mode support ---
        cat > js/theme.js << 'EOF'
// FriendZone - Theme Module
const Theme = {
    current: "light",

    init() {
        const saved = localStorage.getItem("fz_theme") || "light";
        this.apply(saved);
    },

    toggle() {
        const newTheme = this.current === "light" ? "dark" : "light";
        this.apply(newTheme);
    },

    apply(theme) {
        this.current = theme;
        document.body.setAttribute("data-theme", theme);
        localStorage.setItem("fz_theme", theme);
    }
};
EOF
        cat >> css/style.css << 'EOF'

/* Dark Mode */
[data-theme="dark"] body,
[data-theme="dark"] { background: #18191a; color: #e4e6eb; }

[data-theme="dark"] .navbar { background: #242526; }

[data-theme="dark"] .post-card,
[data-theme="dark"] .auth-container,
[data-theme="dark"] .profile-header,
[data-theme="dark"] .friend-card,
[data-theme="dark"] .settings-section,
[data-theme="dark"] .inbox-item,
[data-theme="dark"] .chat-header,
[data-theme="dark"] .chat-messages,
[data-theme="dark"] .chat-input,
[data-theme="dark"] .create-post,
[data-theme="dark"] .notif-item,
[data-theme="dark"] .friend-request {
    background: #242526;
    color: #e4e6eb;
    box-shadow: none;
}

[data-theme="dark"] input,
[data-theme="dark"] textarea {
    background: #3a3b3c;
    border-color: #3a3b3c;
    color: #e4e6eb;
}

[data-theme="dark"] .comment-body { background: #3a3b3c; }

[data-theme="dark"] .post-actions { border-top-color: #3a3b3c; }

[data-theme="dark"] .notif-item.unread { background: #2d3748; }

.theme-toggle {
    cursor: pointer;
    background: none;
    border: none;
    font-size: 18px;
    color: white;
    margin-left: 12px;
}
EOF
        commit_step "Add dark mode theme toggle with full CSS support"
        ;;

    12)
        # --- Image post support & emoji picker ---
        cat > js/media.js << 'EOF'
// FriendZone - Media Module
const Media = {
    supportedTypes: ["image/jpeg", "image/png", "image/gif", "image/webp"],
    maxFileSize: 5 * 1024 * 1024, // 5MB

    handleImageUpload(file) {
        return new Promise((resolve, reject) => {
            if (!this.supportedTypes.includes(file.type)) {
                reject(new Error("Unsupported file type"));
                return;
            }
            if (file.size > this.maxFileSize) {
                reject(new Error("File too large (max 5MB)"));
                return;
            }
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = () => reject(new Error("Failed to read file"));
            reader.readAsDataURL(file);
        });
    },

    renderImagePreview(dataUrl) {
        return `<div class="image-preview">
            <img src="${dataUrl}" alt="Upload preview">
            <button class="remove-image" onclick="this.parentElement.remove()">✕</button>
        </div>`;
    }
};

const EmojiPicker = {
    emojis: ["😀","😂","❤️","👍","🎉","🔥","💯","😎","🤔","👋","🙌","💪","✨","🌟","😍","🥳"],

    render() {
        return `<div class="emoji-picker">
            ${this.emojis.map(e => `<span class="emoji-btn">${e}</span>`).join("")}
        </div>`;
    }
};
EOF
        cat >> css/style.css << 'EOF'

/* Media & Emoji */
.image-preview {
    position: relative;
    margin: 8px 0;
}

.image-preview img {
    max-width: 100%;
    border-radius: 8px;
    max-height: 300px;
    object-fit: cover;
}

.remove-image {
    position: absolute;
    top: 8px;
    right: 8px;
    background: rgba(0,0,0,0.6);
    color: white;
    border: none;
    border-radius: 50%;
    width: 28px;
    height: 28px;
    cursor: pointer;
}

.emoji-picker {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    padding: 8px;
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    max-width: 280px;
}

[data-theme="dark"] .emoji-picker { background: #3a3b3c; border-color: #3a3b3c; }

.emoji-btn {
    cursor: pointer;
    font-size: 20px;
    padding: 4px;
    border-radius: 4px;
}

.emoji-btn:hover { background: #f0f2f5; }
EOF
        commit_step "Add image upload support and emoji picker component"
        ;;

    13)
        # --- Responsive design improvements ---
        cat >> css/style.css << 'EOF'

/* Responsive Design */
@media (max-width: 768px) {
    .navbar {
        flex-direction: column;
        gap: 8px;
        padding: 12px;
    }

    .navbar nav {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 4px;
    }

    .navbar nav a { margin-left: 0; padding: 4px 8px; font-size: 13px; }

    #main-content { padding: 0 8px; margin: 12px auto; }

    .friends-grid { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); }

    .chat-bubble { max-width: 85%; }

    .profile-stats { gap: 20px; }

    .auth-container { margin: 20px 12px; padding: 20px; }

    .search-bar { flex-direction: column; }
}

@media (max-width: 480px) {
    .navbar .logo { font-size: 1.2rem; }

    .profile-avatar-lg { width: 60px; height: 60px; font-size: 28px; }

    .friends-grid { grid-template-columns: 1fr 1fr; }

    .inbox-item { padding: 8px; }
}
EOF
        commit_step "Add responsive design with mobile breakpoints"
        ;;

    14)
        # --- Backend API structure (Python) ---
        mkdir -p backend
        cat > backend/requirements.txt << 'EOF'
flask==3.0.0
flask-cors==4.0.0
flask-sqlalchemy==3.1.1
flask-jwt-extended==4.6.0
werkzeug==3.0.1
EOF
        cat > backend/app.py << 'EOF'
"""FriendZone Backend API"""
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = "friendzone-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///friendzone.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "app": "FriendZone API"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
EOF
        cat > backend/models.py << 'EOF'
"""FriendZone - Database Models"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    bio = db.Column(db.Text, default="")
    avatar_url = db.Column(db.String(500), default=None)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship("Post", backref="author", lazy=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), default=None)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    likes = db.relationship("Like", backref="post", lazy=True)
    comments = db.relationship("Comment", backref="post", lazy=True)


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    addressee_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
EOF
        commit_step "Add Flask backend with SQLAlchemy models for all entities"
        ;;

    15)
        # --- Backend auth routes ---
        cat > backend/routes_auth.py << 'EOF'
"""FriendZone - Authentication Routes"""
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/signup", methods=["POST"])
def signup():
    data = request.get_json()
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 400

    user = User(
        name=data["name"],
        email=data["email"],
        password_hash=generate_password_hash(data["password"])
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": {"id": user.id, "name": user.name, "email": user.email}}), 201


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password_hash, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": {"id": user.id, "name": user.name, "email": user.email}})


@auth_bp.route("/api/auth/me", methods=["GET"])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "bio": user.bio,
        "avatar_url": user.avatar_url,
        "created_at": user.created_at.isoformat()
    })
EOF
        commit_step "Add backend authentication routes with JWT support"
        ;;

    16)
        # --- Backend post routes ---
        cat > backend/routes_posts.py << 'EOF'
"""FriendZone - Post Routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Post, Like, Comment, User

posts_bp = Blueprint("posts", __name__)


@posts_bp.route("/api/posts", methods=["GET"])
@jwt_required()
def get_posts():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=per_page)

    return jsonify({
        "posts": [{
            "id": p.id,
            "content": p.content,
            "image_url": p.image_url,
            "user_id": p.user_id,
            "author_name": p.author.name,
            "likes_count": len(p.likes),
            "comments_count": len(p.comments),
            "created_at": p.created_at.isoformat()
        } for p in posts.items],
        "total": posts.total,
        "pages": posts.pages,
        "current_page": posts.page
    })


@posts_bp.route("/api/posts", methods=["POST"])
@jwt_required()
def create_post():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    post = Post(content=data["content"], user_id=user_id, image_url=data.get("image_url"))
    db.session.add(post)
    db.session.commit()
    return jsonify({"id": post.id, "content": post.content, "created_at": post.created_at.isoformat()}), 201


@posts_bp.route("/api/posts/<int:post_id>/like", methods=["POST"])
@jwt_required()
def toggle_like(post_id):
    user_id = int(get_jwt_identity())
    existing = Like.query.filter_by(user_id=user_id, post_id=post_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({"liked": False})
    like = Like(user_id=user_id, post_id=post_id)
    db.session.add(like)
    db.session.commit()
    return jsonify({"liked": True})


@posts_bp.route("/api/posts/<int:post_id>/comments", methods=["GET"])
@jwt_required()
def get_comments(post_id):
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    return jsonify([{
        "id": c.id,
        "text": c.text,
        "user_id": c.user_id,
        "created_at": c.created_at.isoformat()
    } for c in comments])


@posts_bp.route("/api/posts/<int:post_id>/comments", methods=["POST"])
@jwt_required()
def add_comment(post_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    comment = Comment(text=data["text"], user_id=user_id, post_id=post_id)
    db.session.add(comment)
    db.session.commit()
    return jsonify({"id": comment.id, "text": comment.text}), 201
EOF
        commit_step "Add backend post routes with CRUD, likes, and comments"
        ;;

    17)
        # --- Add .gitignore and package.json ---
        cat > .gitignore << 'EOF'
# Python
__pycache__/
*.pyc
*.pyo
venv/
.env
*.db

# Node
node_modules/
dist/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Build
.build_step
EOF
        cat > package.json << 'EOF'
{
  "name": "friendzone",
  "version": "1.0.0",
  "description": "FriendZone - A social media app to connect with friends",
  "main": "js/app.js",
  "scripts": {
    "start": "python backend/app.py",
    "dev": "live-server --port=3000"
  },
  "keywords": ["social-media", "friends", "messaging"],
  "author": "FriendZone Team",
  "license": "MIT"
}
EOF
        commit_step "Add .gitignore, package.json, and project configuration"
        ;;

    18)
        # --- Loading spinner & toast notifications ---
        cat > js/ui.js << 'EOF'
// FriendZone - UI Utilities
const UI = {
    showLoading() {
        const loader = document.createElement("div");
        loader.className = "loading-overlay";
        loader.id = "loading";
        loader.innerHTML = '<div class="spinner"></div>';
        document.body.appendChild(loader);
    },

    hideLoading() {
        const loader = document.getElementById("loading");
        if (loader) loader.remove();
    },

    showToast(message, type = "info") {
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.classList.add("show"), 10);
        setTimeout(() => {
            toast.classList.remove("show");
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    confirmDialog(message) {
        return new Promise((resolve) => {
            const overlay = document.createElement("div");
            overlay.className = "dialog-overlay";
            overlay.innerHTML = `
                <div class="dialog">
                    <p>${message}</p>
                    <div class="dialog-actions">
                        <button class="btn btn-secondary" id="dialog-cancel">Cancel</button>
                        <button class="btn btn-primary" id="dialog-confirm">Confirm</button>
                    </div>
                </div>
            `;
            document.body.appendChild(overlay);
            document.getElementById("dialog-confirm").onclick = () => { overlay.remove(); resolve(true); };
            document.getElementById("dialog-cancel").onclick = () => { overlay.remove(); resolve(false); };
        });
    },

    formatDate(dateString) {
        const options = { year: "numeric", month: "short", day: "numeric" };
        return new Date(dateString).toLocaleDateString(undefined, options);
    }
};
EOF
        cat >> css/style.css << 'EOF'

/* Loading Spinner */
.loading-overlay {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #4a90d9;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Toast Notifications */
.toast {
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: 12px 24px;
    border-radius: 8px;
    color: white;
    font-size: 14px;
    z-index: 1001;
    transform: translateY(100px);
    opacity: 0;
    transition: all 0.3s ease;
}

.toast.show { transform: translateY(0); opacity: 1; }
.toast-info { background: #4a90d9; }
.toast-success { background: #27ae60; }
.toast-error { background: #e74c3c; }
.toast-warning { background: #f39c12; }

/* Confirm Dialog */
.dialog-overlay {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1002;
}

.dialog {
    background: white;
    padding: 24px;
    border-radius: 12px;
    max-width: 400px;
    text-align: center;
}

[data-theme="dark"] .dialog { background: #242526; }

.dialog-actions {
    display: flex;
    gap: 8px;
    justify-content: center;
    margin-top: 16px;
}
EOF
        commit_step "Add UI utilities: loading spinner, toast notifications, confirm dialog"
        ;;

    *)
        # --- All steps done, make minor updates each cycle ---
        TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
        cat >> js/app.js << EOF

// Updated: $TIMESTAMP - maintenance check
EOF
        # Increment a version counter
        VERSION=$((STEP - 18))
        sed -i "s/\"version\": \".*\"/\"version\": \"1.0.${VERSION}\"/" package.json 2>/dev/null
        commit_step "Maintenance update v1.0.${VERSION} - $(date +%H:%M)"
        ;;
    esac

    echo "[$(date)] Sleeping for $((INTERVAL / 60)) minutes until next commit..."
    sleep $INTERVAL
done
