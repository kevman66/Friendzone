"""
FriendZone Auto-Builder Desktop App
A GUI tool that auto-generates social media app code and commits every hour.
Works fully offline - only needs git installed.
"""

import os
import sys
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

# ── Resolve paths ──────────────────────────────────────────────────────────
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

REPO_DIR = BASE_DIR
STEP_FILE = os.path.join(REPO_DIR, ".build_step")
INTERVAL = 3600  # 1 hour in seconds


# ── Git helpers ────────────────────────────────────────────────────────────
def git(*args):
    result = subprocess.run(
        ["git"] + list(args),
        cwd=REPO_DIR,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def git_commit(message):
    git("add", "-A")
    code, out, err = git("commit", "-m", message)
    return code == 0


# ── Code generation steps ─────────────────────────────────────────────────
def write_file(rel_path, content):
    full = os.path.join(REPO_DIR, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


def append_file(rel_path, content):
    full = os.path.join(REPO_DIR, rel_path)
    with open(full, "a", encoding="utf-8") as f:
        f.write(content)


# Each step returns a commit message
STEPS = []


def step(fn):
    STEPS.append(fn)
    return fn


# ── STEP 0: Scaffold ──────────────────────────────────────────────────────
@step
def step_0():
    write_file("index.html", """\
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
""")
    write_file("css/style.css", """\
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
""")
    write_file("js/app.js", """\
// FriendZone App - Entry Point
console.log("FriendZone app loaded");

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM ready");
});
""")
    write_file("README.md", """\
# FriendZone

A social media app to connect with friends.

## Features (planned)
- User authentication
- News feed with posts
- Friend requests
- Messaging
- Profile pages
- Notifications
""")
    return "Initial project setup with HTML, CSS, JS scaffold"


# ── STEP 1: Auth module ───────────────────────────────────────────────────
@step
def step_1():
    write_file("js/auth.js", """\
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
            id: Date.now().toString(), name, email, password,
            avatar: null, bio: "", friends: [],
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
        if (session) { this.currentUser = JSON.parse(session); return true; }
        return false;
    }
};
""")
    append_file("css/style.css", """
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
    width: 100%; padding: 12px; margin-bottom: 12px;
    border: 1px solid #ddd; border-radius: 6px; font-size: 14px;
}
.btn { padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn-primary { background: #4a90d9; color: white; width: 100%; padding: 12px; }
.btn-primary:hover { background: #3a7bc8; }
.auth-switch { text-align: center; margin-top: 16px; color: #666; }
.auth-switch a { color: #4a90d9; text-decoration: none; }
""")
    return "Add authentication module with login and signup forms"


# ── STEP 2: Feed ──────────────────────────────────────────────────────────
@step
def step_2():
    write_file("js/feed.js", """\
// FriendZone - News Feed Module
const Feed = {
    getPosts() {
        return JSON.parse(localStorage.getItem("fz_posts") || "[]")
            .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    },

    createPost(userId, userName, content) {
        const posts = this.getPosts();
        const post = {
            id: Date.now().toString(), userId, userName, content,
            likes: [], comments: [], createdAt: new Date().toISOString()
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
        if (idx === -1) post.likes.push(userId);
        else post.likes.splice(idx, 1);
        localStorage.setItem("fz_posts", JSON.stringify(posts));
        return post;
    },

    renderFeed(currentUserId) {
        const posts = this.getPosts();
        if (posts.length === 0)
            return '<div class="empty-feed"><p>No posts yet. Be the first to share!</p></div>';
        return posts.map(p => this.renderPost(p, currentUserId)).join("");
    },

    renderPost(post, currentUserId) {
        const liked = post.likes.includes(currentUserId);
        const timeAgo = this.timeAgo(new Date(post.createdAt));
        return `
            <div class="post-card" data-post-id="${post.id}">
                <div class="post-header">
                    <div class="post-avatar">${post.userName.charAt(0)}</div>
                    <div><strong>${post.userName}</strong><span class="post-time">${timeAgo}</span></div>
                </div>
                <div class="post-content">${post.content}</div>
                <div class="post-actions">
                    <button class="btn-like ${liked ? 'liked' : ''}" data-id="${post.id}">
                        ${liked ? '\\u2764\\uFE0F' : '\\uD83E\\uDD0D'} ${post.likes.length}</button>
                    <button class="btn-comment" data-id="${post.id}">
                        \\uD83D\\uDCAC ${post.comments.length}</button>
                </div>
            </div>`;
    },

    renderCreatePost() {
        return `<div class="create-post">
            <textarea id="post-input" placeholder="What's on your mind?" rows="3"></textarea>
            <button class="btn btn-primary" id="submit-post">Post</button>
        </div>`;
    },

    timeAgo(date) {
        const s = Math.floor((new Date() - date) / 1000);
        if (s < 60) return "just now";
        if (s < 3600) return Math.floor(s / 60) + "m ago";
        if (s < 86400) return Math.floor(s / 3600) + "h ago";
        return Math.floor(s / 86400) + "d ago";
    }
};
""")
    append_file("css/style.css", """
/* Feed & Posts */
.create-post { background: white; padding: 16px; border-radius: 8px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
.create-post textarea { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; resize: vertical; font-family: inherit; font-size: 14px; margin-bottom: 8px; }
.post-card { background: white; padding: 16px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
.post-header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.post-avatar { width: 40px; height: 40px; border-radius: 50%; background: #4a90d9; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 18px; }
.post-time { color: #999; font-size: 12px; margin-left: 8px; }
.post-content { margin-bottom: 12px; line-height: 1.5; }
.post-actions { display: flex; gap: 12px; border-top: 1px solid #eee; padding-top: 8px; }
.post-actions button { background: none; border: none; cursor: pointer; font-size: 14px; padding: 4px 8px; border-radius: 4px; }
.post-actions button:hover { background: #f0f2f5; }
.btn-like.liked { color: #e74c3c; }
.empty-feed { text-align: center; padding: 40px; color: #999; }
""")
    return "Add news feed with post creation, likes, and time display"


# ── STEP 3: Profile ───────────────────────────────────────────────────────
@step
def step_3():
    write_file("js/profile.js", """\
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
                <div class="profile-posts"><h3>Posts</h3>${this.getUserPosts(user.id)}</div>
            </div>`;
    },
    getPostCount(userId) {
        return JSON.parse(localStorage.getItem("fz_posts") || "[]").filter(p => p.userId === userId).length;
    },
    getUserPosts(userId) {
        const posts = JSON.parse(localStorage.getItem("fz_posts") || "[]")
            .filter(p => p.userId === userId).sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
        if (posts.length === 0) return '<p class="empty-feed">No posts yet.</p>';
        return posts.map(p => Feed.renderPost(p, userId)).join("");
    },
    renderEditProfile(user) {
        return `<div class="auth-container"><h2>Edit Profile</h2>
            <form id="edit-profile-form">
                <input type="text" id="edit-name" value="${user.name}" placeholder="Full Name" required>
                <textarea id="edit-bio" placeholder="Write a bio..." rows="3">${user.bio || ""}</textarea>
                <button type="submit" class="btn btn-primary">Save Changes</button>
                <button type="button" class="btn btn-secondary" id="cancel-edit">Cancel</button>
            </form></div>`;
    },
    updateProfile(userId, name, bio) {
        const users = JSON.parse(localStorage.getItem("fz_users") || "[]");
        const user = users.find(u => u.id === userId);
        if (user) { user.name = name; user.bio = bio;
            localStorage.setItem("fz_users", JSON.stringify(users));
            localStorage.setItem("fz_session", JSON.stringify(user)); return user; }
        return null;
    }
};
""")
    append_file("css/style.css", """
/* Profile */
.profile-page { max-width: 680px; margin: 0 auto; }
.profile-header { background: white; padding: 32px; border-radius: 8px; text-align: center; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
.profile-avatar-lg { width: 80px; height: 80px; border-radius: 50%; background: #4a90d9; color: white; display: flex; align-items: center; justify-content: center; font-size: 36px; font-weight: bold; margin: 0 auto 12px; }
.profile-bio { color: #666; margin: 8px 0 16px; }
.profile-stats { display: flex; justify-content: center; gap: 40px; margin-bottom: 16px; }
.profile-stats .stat { text-align: center; }
.profile-stats .stat span { display: block; color: #999; font-size: 13px; }
.btn-secondary { background: #e4e6eb; color: #1c1e21; }
.btn-secondary:hover { background: #d4d6db; }
.profile-posts h3 { margin-bottom: 12px; }
""")
    return "Add user profile page with stats, bio, and edit functionality"


# ── STEP 4: Friends ───────────────────────────────────────────────────────
@step
def step_4():
    write_file("js/friends.js", """\
// FriendZone - Friends Module
const Friends = {
    sendRequest(fromId, toId) {
        const requests = JSON.parse(localStorage.getItem("fz_friend_requests") || "[]");
        if (requests.find(r => r.from === fromId && r.to === toId))
            return { success: false, error: "Request already sent" };
        requests.push({ id: Date.now().toString(), from: fromId, to: toId, status: "pending", createdAt: new Date().toISOString() });
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
        const from = users.find(u => u.id === req.from);
        const to = users.find(u => u.id === req.to);
        if (from && to) { from.friends.push(req.to); to.friends.push(req.from); localStorage.setItem("fz_users", JSON.stringify(users)); }
        return true;
    },
    declineRequest(requestId) {
        let requests = JSON.parse(localStorage.getItem("fz_friend_requests") || "[]");
        requests = requests.filter(r => r.id !== requestId);
        localStorage.setItem("fz_friend_requests", JSON.stringify(requests));
    },
    getPendingRequests(userId) {
        return JSON.parse(localStorage.getItem("fz_friend_requests") || "[]").filter(r => r.to === userId && r.status === "pending");
    },
    getFriendsList(userId) {
        const users = JSON.parse(localStorage.getItem("fz_users") || "[]");
        const user = users.find(u => u.id === userId);
        if (!user) return [];
        return users.filter(u => user.friends.includes(u.id));
    },
    renderFriendsList(userId) {
        const friends = this.getFriendsList(userId);
        if (friends.length === 0) return '<div class="empty-feed"><p>No friends yet. Start connecting!</p></div>';
        return `<div class="friends-grid">${friends.map(f => `
            <div class="friend-card"><div class="post-avatar">${f.name.charAt(0)}</div>
            <strong>${f.name}</strong></div>`).join("")}</div>`;
    },
    renderPendingRequests(userId) {
        const requests = this.getPendingRequests(userId);
        const users = JSON.parse(localStorage.getItem("fz_users") || "[]");
        if (requests.length === 0) return '<p>No pending requests.</p>';
        return requests.map(r => { const from = users.find(u => u.id === r.from);
            return `<div class="friend-request"><div class="post-avatar">${from ? from.name.charAt(0) : "?"}</div>
            <span>${from ? from.name : "Unknown"} wants to be your friend</span>
            <button class="btn btn-primary btn-sm" data-accept="${r.id}">Accept</button>
            <button class="btn btn-secondary btn-sm" data-decline="${r.id}">Decline</button></div>`; }).join("");
    }
};
""")
    append_file("css/style.css", """
/* Friends */
.friends-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }
.friend-card { background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
.friend-card .post-avatar { margin: 0 auto 8px; }
.friend-request { display: flex; align-items: center; gap: 12px; background: white; padding: 12px; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
.btn-sm { padding: 6px 12px; font-size: 12px; }
""")
    return "Add friends system with requests, accept/decline, and friends list"


# ── STEP 5: Comments ──────────────────────────────────────────────────────
@step
def step_5():
    write_file("js/comments.js", """\
// FriendZone - Comments Module
const Comments = {
    addComment(postId, userId, userName, text) {
        const posts = JSON.parse(localStorage.getItem("fz_posts") || "[]");
        const post = posts.find(p => p.id === postId);
        if (!post) return null;
        const comment = { id: Date.now().toString(), userId, userName, text, createdAt: new Date().toISOString() };
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
        if (!post || post.comments.length === 0) return '<p class="no-comments">No comments yet.</p>';
        return post.comments.map(c => `
            <div class="comment"><div class="comment-avatar">${c.userName.charAt(0)}</div>
            <div class="comment-body"><strong>${c.userName}</strong><p>${c.text}</p>
            <span class="post-time">${Feed.timeAgo(new Date(c.createdAt))}</span></div>
            ${c.userId === currentUserId ? '<button class="comment-delete" data-post="' + postId + '" data-comment="' + c.id + '">x</button>' : ''}</div>`).join("");
    },
    renderCommentForm(postId) {
        return `<div class="comment-form">
            <input type="text" class="comment-input" data-post="${postId}" placeholder="Write a comment...">
            <button class="btn btn-primary btn-sm comment-submit" data-post="${postId}">Send</button></div>`;
    }
};
""")
    append_file("css/style.css", """
/* Comments */
.comment { display: flex; gap: 8px; padding: 8px 0; align-items: flex-start; }
.comment-avatar { width: 28px; height: 28px; border-radius: 50%; background: #ccc; color: white; display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0; }
.comment-body { background: #f0f2f5; padding: 8px 12px; border-radius: 12px; flex: 1; }
.comment-body p { margin: 4px 0; font-size: 14px; }
.comment-delete { background: none; border: none; color: #999; cursor: pointer; }
.comment-form { display: flex; gap: 8px; margin-top: 8px; }
.comment-input { flex: 1; padding: 8px 12px; border: 1px solid #ddd; border-radius: 20px; font-size: 13px; }
.no-comments { color: #999; font-size: 13px; padding: 8px 0; }
""")
    return "Add commenting system with add, delete, and display"


# ── STEP 6: Messaging ─────────────────────────────────────────────────────
@step
def step_6():
    write_file("js/messaging.js", """\
// FriendZone - Messaging Module
const Messaging = {
    getConversations(userId) {
        const messages = JSON.parse(localStorage.getItem("fz_messages") || "[]");
        const convos = {};
        messages.forEach(m => {
            if (m.from === userId || m.to === userId) {
                const otherId = m.from === userId ? m.to : m.from;
                if (!convos[otherId]) convos[otherId] = { userId: otherId, messages: [], lastMessage: null };
                convos[otherId].messages.push(m);
                if (!convos[otherId].lastMessage || new Date(m.createdAt) > new Date(convos[otherId].lastMessage.createdAt))
                    convos[otherId].lastMessage = m;
            }
        });
        return Object.values(convos).sort((a, b) => new Date(b.lastMessage.createdAt) - new Date(a.lastMessage.createdAt));
    },
    sendMessage(fromId, toId, text) {
        const messages = JSON.parse(localStorage.getItem("fz_messages") || "[]");
        const msg = { id: Date.now().toString(), from: fromId, to: toId, text, read: false, createdAt: new Date().toISOString() };
        messages.push(msg);
        localStorage.setItem("fz_messages", JSON.stringify(messages));
        return msg;
    },
    getThread(userId, otherUserId) {
        return JSON.parse(localStorage.getItem("fz_messages") || "[]")
            .filter(m => (m.from === userId && m.to === otherUserId) || (m.from === otherUserId && m.to === userId))
            .sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
    },
    getUnreadCount(userId) {
        return JSON.parse(localStorage.getItem("fz_messages") || "[]").filter(m => m.to === userId && !m.read).length;
    },
    markAsRead(userId, otherUserId) {
        const messages = JSON.parse(localStorage.getItem("fz_messages") || "[]");
        messages.forEach(m => { if (m.from === otherUserId && m.to === userId && !m.read) m.read = true; });
        localStorage.setItem("fz_messages", JSON.stringify(messages));
    },
    renderInbox(userId) {
        const convos = this.getConversations(userId);
        const users = JSON.parse(localStorage.getItem("fz_users") || "[]");
        if (convos.length === 0) return '<div class="empty-feed"><p>No messages yet.</p></div>';
        return '<div class="inbox">' + convos.map(c => {
            const other = users.find(u => u.id === c.userId);
            const unread = c.messages.filter(m => m.to === userId && !m.read).length;
            return '<div class="inbox-item" data-user="' + c.userId + '">' +
                '<div class="post-avatar">' + (other ? other.name.charAt(0) : "?") + '</div>' +
                '<div class="inbox-preview"><strong>' + (other ? other.name : "Unknown") + '</strong>' +
                (unread > 0 ? ' <span class="badge">' + unread + '</span>' : '') +
                '<p>' + c.lastMessage.text.substring(0, 50) + '...</p></div></div>';
        }).join("") + '</div>';
    }
};
""")
    append_file("css/style.css", """
/* Messaging */
.inbox-item { display: flex; align-items: center; gap: 12px; padding: 12px; background: white; border-radius: 8px; margin-bottom: 4px; cursor: pointer; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.inbox-item:hover { background: #f7f8fa; }
.inbox-preview { flex: 1; }
.inbox-preview p { color: #999; font-size: 13px; margin-top: 2px; }
.badge { background: #e74c3c; color: white; border-radius: 10px; padding: 2px 8px; font-size: 11px; margin-left: 8px; }
.chat-header { display: flex; align-items: center; gap: 12px; padding: 12px; background: white; border-radius: 8px 8px 0 0; border-bottom: 1px solid #eee; }
.chat-messages { background: white; padding: 16px; min-height: 300px; max-height: 400px; overflow-y: auto; }
.chat-bubble { max-width: 70%; padding: 10px 14px; border-radius: 16px; margin-bottom: 8px; }
.chat-bubble.sent { background: #4a90d9; color: white; margin-left: auto; border-bottom-right-radius: 4px; }
.chat-bubble.received { background: #f0f2f5; border-bottom-left-radius: 4px; }
.chat-input { display: flex; gap: 8px; padding: 12px; background: white; border-radius: 0 0 8px 8px; border-top: 1px solid #eee; }
.chat-input input { flex: 1; padding: 10px 14px; border: 1px solid #ddd; border-radius: 20px; }
""")
    return "Add direct messaging with inbox, threads, and unread badges"


# ── STEP 7: Notifications ─────────────────────────────────────────────────
@step
def step_7():
    write_file("js/notifications.js", """\
// FriendZone - Notifications Module
const Notifications = {
    add(userId, type, message, relatedId) {
        const notifs = JSON.parse(localStorage.getItem("fz_notifications") || "[]");
        notifs.unshift({ id: Date.now().toString(), userId, type, message, relatedId, read: false, createdAt: new Date().toISOString() });
        localStorage.setItem("fz_notifications", JSON.stringify(notifs));
    },
    getForUser(userId) { return JSON.parse(localStorage.getItem("fz_notifications") || "[]").filter(n => n.userId === userId); },
    getUnreadCount(userId) { return this.getForUser(userId).filter(n => !n.read).length; },
    markAllRead(userId) {
        const notifs = JSON.parse(localStorage.getItem("fz_notifications") || "[]");
        notifs.forEach(n => { if (n.userId === userId) n.read = true; });
        localStorage.setItem("fz_notifications", JSON.stringify(notifs));
    },
    renderNotifications(userId) {
        const notifs = this.getForUser(userId);
        if (notifs.length === 0) return '<div class="empty-feed"><p>No notifications.</p></div>';
        return '<div class="notif-list">' + notifs.map(n =>
            '<div class="notif-item ' + (n.read ? '' : 'unread') + '">' +
            '<div class="notif-icon">' + this.getIcon(n.type) + '</div>' +
            '<div class="notif-body"><p>' + n.message + '</p>' +
            '<span class="post-time">' + Feed.timeAgo(new Date(n.createdAt)) + '</span></div></div>'
        ).join("") + '</div>';
    },
    getIcon(type) {
        const icons = { like: "heart", comment: "chat", friend_request: "people", friend_accept: "handshake", message: "mail" };
        return icons[type] || "bell";
    }
};
""")
    append_file("css/style.css", """
/* Notifications */
.notif-list { max-width: 500px; }
.notif-item { display: flex; align-items: center; gap: 12px; padding: 12px; background: white; border-radius: 8px; margin-bottom: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.notif-item.unread { background: #e8f0fe; }
.notif-icon { font-size: 20px; }
.notif-body p { margin: 0; font-size: 14px; }
""")
    return "Add notification system with types, icons, and unread tracking"


# ── STEP 8: Search ─────────────────────────────────────────────────────────
@step
def step_8():
    write_file("js/search.js", """\
// FriendZone - Search Module
const Search = {
    searchUsers(query) {
        const users = JSON.parse(localStorage.getItem("fz_users") || "[]");
        const q = query.toLowerCase();
        return users.filter(u => u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q));
    },
    searchPosts(query) {
        const posts = JSON.parse(localStorage.getItem("fz_posts") || "[]");
        const q = query.toLowerCase();
        return posts.filter(p => p.content.toLowerCase().includes(q));
    },
    renderSearchPage() {
        return '<div class="search-page"><div class="search-bar">' +
            '<input type="text" id="search-input" placeholder="Search people or posts...">' +
            '<button class="btn btn-primary" id="search-btn">Search</button>' +
            '</div><div id="search-results"></div></div>';
    },
    renderResults(query) {
        const users = this.searchUsers(query);
        const posts = this.searchPosts(query);
        let html = '';
        if (users.length > 0) {
            html += '<h3>People</h3><div class="friends-grid">' +
                users.map(u => '<div class="friend-card"><div class="post-avatar">' + u.name.charAt(0) + '</div><strong>' + u.name + '</strong></div>').join("") + '</div>';
        }
        if (posts.length > 0) {
            html += '<h3 style="margin-top:16px;">Posts</h3>' + posts.map(p => Feed.renderPost(p, "")).join("");
        }
        if (users.length === 0 && posts.length === 0) html = '<div class="empty-feed"><p>No results found.</p></div>';
        return html;
    }
};
""")
    append_file("css/style.css", """
/* Search */
.search-bar { display: flex; gap: 8px; margin-bottom: 20px; }
.search-bar input { flex: 1; padding: 12px 16px; border: 1px solid #ddd; border-radius: 8px; font-size: 15px; }
""")
    return "Add search functionality for users and posts"


# ── STEP 9: Wire up app.js ────────────────────────────────────────────────
@step
def step_9():
    write_file("js/app.js", """\
// FriendZone App - Main Controller
const App = {
    init() {
        if (Auth.checkSession()) { this.showHome(); this.updateNavbar(true); }
        else { this.showLogin(); this.updateNavbar(false); }
        this.bindNavigation();
    },
    updateNavbar(loggedIn) {
        const nav = document.querySelector(".navbar nav");
        if (loggedIn) {
            nav.innerHTML = '<a href="#" id="nav-home">Home</a><a href="#" id="nav-search">Search</a>' +
                '<a href="#" id="nav-friends">Friends</a><a href="#" id="nav-messages">Messages</a>' +
                '<a href="#" id="nav-notifs">Notifications</a><a href="#" id="nav-profile">Profile</a>' +
                '<a href="#" id="nav-logout">Logout</a>';
        } else { nav.innerHTML = '<a href="#" id="nav-login">Login</a>'; }
        this.bindNavigation();
    },
    bindNavigation() {
        const bind = (id, handler) => { const el = document.getElementById(id); if (el) el.onclick = (e) => { e.preventDefault(); handler(); }; };
        bind("nav-home", () => this.showHome());
        bind("nav-login", () => this.showLogin());
        bind("nav-profile", () => this.showProfile());
        bind("nav-friends", () => this.showFriends());
        bind("nav-messages", () => this.showMessages());
        bind("nav-notifs", () => this.showNotifications());
        bind("nav-search", () => this.showSearch());
        bind("nav-logout", () => { Auth.logout(); this.updateNavbar(false); this.showLogin(); });
    },
    setContent(html) { document.getElementById("main-content").innerHTML = html; },
    showLogin() {
        this.setContent(Auth.renderLoginForm());
        document.getElementById("login-form").onsubmit = (e) => {
            e.preventDefault();
            const result = Auth.login(document.getElementById("login-email").value, document.getElementById("login-password").value);
            if (result.success) { this.updateNavbar(true); this.showHome(); } else { alert(result.error); }
        };
        const s = document.getElementById("show-signup"); if (s) s.onclick = (e) => { e.preventDefault(); this.showSignup(); };
    },
    showSignup() {
        this.setContent(Auth.renderSignupForm());
        document.getElementById("signup-form").onsubmit = (e) => {
            e.preventDefault();
            const pw = document.getElementById("signup-password").value;
            if (pw !== document.getElementById("signup-confirm").value) { alert("Passwords don't match"); return; }
            const result = Auth.signup(document.getElementById("signup-name").value, document.getElementById("signup-email").value, pw);
            if (result.success) { this.updateNavbar(true); this.showHome(); } else { alert(result.error); }
        };
        const s = document.getElementById("show-login"); if (s) s.onclick = (e) => { e.preventDefault(); this.showLogin(); };
    },
    showHome() {
        const user = Auth.currentUser;
        this.setContent(Feed.renderCreatePost() + Feed.renderFeed(user.id));
        document.getElementById("submit-post").onclick = () => {
            const input = document.getElementById("post-input");
            if (input.value.trim()) { Feed.createPost(user.id, user.name, input.value.trim()); this.showHome(); }
        };
    },
    showProfile() { this.setContent(Profile.renderProfile(Auth.currentUser, true)); },
    showFriends() {
        const user = Auth.currentUser;
        this.setContent('<h2>Friend Requests</h2>' + Friends.renderPendingRequests(user.id) +
            '<h2 style="margin-top:20px;">My Friends</h2>' + Friends.renderFriendsList(user.id));
    },
    showMessages() { this.setContent('<h2>Messages</h2>' + Messaging.renderInbox(Auth.currentUser.id)); },
    showNotifications() {
        Notifications.markAllRead(Auth.currentUser.id);
        this.setContent('<h2>Notifications</h2>' + Notifications.renderNotifications(Auth.currentUser.id));
        this.updateNavbar(true);
    },
    showSearch() {
        this.setContent(Search.renderSearchPage());
        document.getElementById("search-btn").onclick = () => {
            const q = document.getElementById("search-input").value.trim();
            if (q) document.getElementById("search-results").innerHTML = Search.renderResults(q);
        };
    }
};
document.addEventListener("DOMContentLoaded", () => App.init());
""")
    write_file("index.html", """\
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
            <nav><a href="#" id="nav-login">Login</a></nav>
        </header>
        <main id="main-content">
            <h2>Welcome to FriendZone</h2>
            <p>Connect, share, and stay in touch with your friends.</p>
        </main>
        <footer class="footer"><p>&copy; 2026 FriendZone. All rights reserved.</p></footer>
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
""")
    append_file("css/style.css", """
/* Footer */
.footer { text-align: center; padding: 24px; color: #999; font-size: 13px; margin-top: 40px; }
""")
    return "Wire up all modules in main app controller and update HTML"


# ── STEP 10: Settings ─────────────────────────────────────────────────────
@step
def step_10():
    write_file("js/settings.js", """\
// FriendZone - Settings Module
const Settings = {
    getPreferences(userId) { return JSON.parse(localStorage.getItem('fz_prefs_' + userId) || '{}'); },
    savePreferences(userId, prefs) { localStorage.setItem('fz_prefs_' + userId, JSON.stringify(prefs)); },
    renderSettings(userId) {
        const prefs = this.getPreferences(userId);
        return '<div class="settings-page"><h2>Settings</h2>' +
            '<div class="settings-section"><h3>Privacy</h3>' +
            '<label class="setting-row"><span>Make profile public</span><input type="checkbox" id="pref-public" ' + (prefs.publicProfile ? 'checked' : '') + '></label>' +
            '<label class="setting-row"><span>Show online status</span><input type="checkbox" id="pref-online" ' + (prefs.showOnline !== false ? 'checked' : '') + '></label></div>' +
            '<div class="settings-section"><h3>Notifications</h3>' +
            '<label class="setting-row"><span>Email notifications</span><input type="checkbox" id="pref-email-notif" ' + (prefs.emailNotifs ? 'checked' : '') + '></label>' +
            '<label class="setting-row"><span>Friend request alerts</span><input type="checkbox" id="pref-friend-notif" ' + (prefs.friendNotifs !== false ? 'checked' : '') + '></label></div>' +
            '<div class="settings-section"><h3>Account</h3>' +
            '<button class="btn btn-secondary" id="change-password">Change Password</button>' +
            '<button class="btn btn-danger" id="delete-account">Delete Account</button></div>' +
            '<button class="btn btn-primary" id="save-settings">Save Settings</button></div>';
    }
};
""")
    append_file("css/style.css", """
/* Settings */
.settings-page { max-width: 500px; margin: 0 auto; }
.settings-section { background: white; padding: 16px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
.settings-section h3 { margin-bottom: 12px; color: #333; }
.setting-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
.setting-row:last-child { border-bottom: none; }
.btn-danger { background: #e74c3c; color: white; margin-left: 8px; }
.btn-danger:hover { background: #c0392b; }
""")
    return "Add settings page with privacy, notification, and account options"


# ── STEP 11: Dark mode ────────────────────────────────────────────────────
@step
def step_11():
    write_file("js/theme.js", """\
// FriendZone - Theme Module
const Theme = {
    current: "light",
    init() { this.apply(localStorage.getItem("fz_theme") || "light"); },
    toggle() { this.apply(this.current === "light" ? "dark" : "light"); },
    apply(theme) { this.current = theme; document.body.setAttribute("data-theme", theme); localStorage.setItem("fz_theme", theme); }
};
""")
    append_file("css/style.css", """
/* Dark Mode */
[data-theme="dark"] body, [data-theme="dark"] { background: #18191a; color: #e4e6eb; }
[data-theme="dark"] .navbar { background: #242526; }
[data-theme="dark"] .post-card, [data-theme="dark"] .auth-container, [data-theme="dark"] .profile-header,
[data-theme="dark"] .friend-card, [data-theme="dark"] .settings-section, [data-theme="dark"] .create-post,
[data-theme="dark"] .notif-item, [data-theme="dark"] .friend-request, [data-theme="dark"] .inbox-item { background: #242526; color: #e4e6eb; box-shadow: none; }
[data-theme="dark"] input, [data-theme="dark"] textarea { background: #3a3b3c; border-color: #3a3b3c; color: #e4e6eb; }
[data-theme="dark"] .comment-body { background: #3a3b3c; }
[data-theme="dark"] .notif-item.unread { background: #2d3748; }
""")
    return "Add dark mode theme toggle with full CSS support"


# ── STEP 12: Media & emoji ────────────────────────────────────────────────
@step
def step_12():
    write_file("js/media.js", """\
// FriendZone - Media Module
const Media = {
    supportedTypes: ["image/jpeg", "image/png", "image/gif", "image/webp"],
    maxFileSize: 5 * 1024 * 1024,
    handleImageUpload(file) {
        return new Promise((resolve, reject) => {
            if (!this.supportedTypes.includes(file.type)) { reject(new Error("Unsupported file type")); return; }
            if (file.size > this.maxFileSize) { reject(new Error("File too large (max 5MB)")); return; }
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = () => reject(new Error("Failed to read file"));
            reader.readAsDataURL(file);
        });
    },
    renderImagePreview(dataUrl) {
        return '<div class="image-preview"><img src="' + dataUrl + '" alt="Upload preview">' +
            '<button class="remove-image" onclick="this.parentElement.remove()">x</button></div>';
    }
};
const EmojiPicker = {
    emojis: ["😀","😂","❤️","👍","🎉","🔥","💯","😎","🤔","👋","🙌","💪","✨","🌟","😍","🥳"],
    render() { return '<div class="emoji-picker">' + this.emojis.map(e => '<span class="emoji-btn">' + e + '</span>').join("") + '</div>'; }
};
""")
    append_file("css/style.css", """
/* Media & Emoji */
.image-preview { position: relative; margin: 8px 0; }
.image-preview img { max-width: 100%; border-radius: 8px; max-height: 300px; object-fit: cover; }
.remove-image { position: absolute; top: 8px; right: 8px; background: rgba(0,0,0,0.6); color: white; border: none; border-radius: 50%; width: 28px; height: 28px; cursor: pointer; }
.emoji-picker { display: flex; flex-wrap: wrap; gap: 4px; padding: 8px; background: white; border: 1px solid #ddd; border-radius: 8px; max-width: 280px; }
.emoji-btn { cursor: pointer; font-size: 20px; padding: 4px; border-radius: 4px; }
.emoji-btn:hover { background: #f0f2f5; }
""")
    return "Add image upload support and emoji picker component"


# ── STEP 13: Responsive ───────────────────────────────────────────────────
@step
def step_13():
    append_file("css/style.css", """
/* Responsive Design */
@media (max-width: 768px) {
    .navbar { flex-direction: column; gap: 8px; padding: 12px; }
    .navbar nav { display: flex; flex-wrap: wrap; justify-content: center; gap: 4px; }
    .navbar nav a { margin-left: 0; padding: 4px 8px; font-size: 13px; }
    #main-content { padding: 0 8px; margin: 12px auto; }
    .friends-grid { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); }
    .auth-container { margin: 20px 12px; padding: 20px; }
    .search-bar { flex-direction: column; }
}
@media (max-width: 480px) {
    .navbar .logo { font-size: 1.2rem; }
    .profile-avatar-lg { width: 60px; height: 60px; font-size: 28px; }
    .friends-grid { grid-template-columns: 1fr 1fr; }
}
""")
    return "Add responsive design with mobile breakpoints"


# ── STEP 14: Backend models ───────────────────────────────────────────────
@step
def step_14():
    write_file("backend/requirements.txt", """\
flask==3.0.0
flask-cors==4.0.0
flask-sqlalchemy==3.1.1
flask-jwt-extended==4.6.0
werkzeug==3.0.1
""")
    write_file("backend/app.py", """\
\"\"\"FriendZone Backend API\"\"\"
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
""")
    write_file("backend/models.py", """\
\"\"\"FriendZone - Database Models\"\"\"
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
""")
    return "Add Flask backend with SQLAlchemy models for all entities"


# ── STEP 15: Auth routes ──────────────────────────────────────────────────
@step
def step_15():
    write_file("backend/routes_auth.py", """\
\"\"\"FriendZone - Authentication Routes\"\"\"
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
    user = User(name=data["name"], email=data["email"], password_hash=generate_password_hash(data["password"]))
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
    user = User.query.get(int(get_jwt_identity()))
    if not user: return jsonify({"error": "User not found"}), 404
    return jsonify({"id": user.id, "name": user.name, "email": user.email, "bio": user.bio, "created_at": user.created_at.isoformat()})
""")
    return "Add backend authentication routes with JWT support"


# ── STEP 16: Post routes ──────────────────────────────────────────────────
@step
def step_16():
    write_file("backend/routes_posts.py", """\
\"\"\"FriendZone - Post Routes\"\"\"
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Post, Like, Comment

posts_bp = Blueprint("posts", __name__)

@posts_bp.route("/api/posts", methods=["GET"])
@jwt_required()
def get_posts():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=per_page)
    return jsonify({"posts": [{"id": p.id, "content": p.content, "user_id": p.user_id, "author_name": p.author.name,
        "likes_count": len(p.likes), "comments_count": len(p.comments), "created_at": p.created_at.isoformat()} for p in posts.items],
        "total": posts.total, "pages": posts.pages, "current_page": posts.page})

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
    if existing: db.session.delete(existing); db.session.commit(); return jsonify({"liked": False})
    db.session.add(Like(user_id=user_id, post_id=post_id)); db.session.commit()
    return jsonify({"liked": True})

@posts_bp.route("/api/posts/<int:post_id>/comments", methods=["POST"])
@jwt_required()
def add_comment(post_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    comment = Comment(text=data["text"], user_id=user_id, post_id=post_id)
    db.session.add(comment); db.session.commit()
    return jsonify({"id": comment.id, "text": comment.text}), 201
""")
    return "Add backend post routes with CRUD, likes, and comments"


# ── STEP 17: Config files ─────────────────────────────────────────────────
@step
def step_17():
    write_file(".gitignore", """\
__pycache__/
*.pyc
venv/
.env
*.db
node_modules/
dist/
.vscode/
.idea/
.DS_Store
Thumbs.db
.build_step
build/
*.spec
""")
    write_file("package.json", """\
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
""")
    return "Add .gitignore, package.json, and project configuration"


# ── STEP 18: UI utilities ─────────────────────────────────────────────────
@step
def step_18():
    write_file("js/ui.js", """\
// FriendZone - UI Utilities
const UI = {
    showLoading() {
        const loader = document.createElement("div");
        loader.className = "loading-overlay"; loader.id = "loading";
        loader.innerHTML = '<div class="spinner"></div>';
        document.body.appendChild(loader);
    },
    hideLoading() { const l = document.getElementById("loading"); if (l) l.remove(); },
    showToast(message, type) {
        type = type || "info";
        const toast = document.createElement("div");
        toast.className = "toast toast-" + type; toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.classList.add("show"), 10);
        setTimeout(() => { toast.classList.remove("show"); setTimeout(() => toast.remove(), 300); }, 3000);
    },
    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
    }
};
""")
    append_file("css/style.css", """
/* Loading & Toasts */
.loading-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.spinner { width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #4a90d9; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.toast { position: fixed; bottom: 20px; right: 20px; padding: 12px 24px; border-radius: 8px; color: white; font-size: 14px; z-index: 1001; transform: translateY(100px); opacity: 0; transition: all 0.3s ease; }
.toast.show { transform: translateY(0); opacity: 1; }
.toast-info { background: #4a90d9; }
.toast-success { background: #27ae60; }
.toast-error { background: #e74c3c; }
""")
    return "Add UI utilities: loading spinner, toast notifications"


# ── STEP 19: Online status tracker ────────────────────────────────────────
@step
def step_19():
    write_file("js/status.js", """\
// FriendZone - Online Status Tracker
const StatusTracker = {
    updateStatus(userId) {
        const statuses = JSON.parse(localStorage.getItem("fz_statuses") || "{}");
        statuses[userId] = { online: true, lastSeen: new Date().toISOString() };
        localStorage.setItem("fz_statuses", JSON.stringify(statuses));
    },

    setOffline(userId) {
        const statuses = JSON.parse(localStorage.getItem("fz_statuses") || "{}");
        if (statuses[userId]) {
            statuses[userId].online = false;
            statuses[userId].lastSeen = new Date().toISOString();
            localStorage.setItem("fz_statuses", JSON.stringify(statuses));
        }
    },

    isOnline(userId) {
        const statuses = JSON.parse(localStorage.getItem("fz_statuses") || "{}");
        if (!statuses[userId]) return false;
        const lastSeen = new Date(statuses[userId].lastSeen);
        const fiveMinAgo = new Date(Date.now() - 5 * 60 * 1000);
        return statuses[userId].online && lastSeen > fiveMinAgo;
    },

    getLastSeen(userId) {
        const statuses = JSON.parse(localStorage.getItem("fz_statuses") || "{}");
        if (!statuses[userId]) return "Never";
        return Feed.timeAgo(new Date(statuses[userId].lastSeen));
    },

    renderStatusDot(userId) {
        const online = this.isOnline(userId);
        return '<span class="status-dot ' + (online ? 'online' : 'offline') + '"></span>';
    },

    startHeartbeat(userId) {
        this.updateStatus(userId);
        this._interval = setInterval(() => this.updateStatus(userId), 60000);
    },

    stopHeartbeat() {
        if (this._interval) clearInterval(this._interval);
    }
};
""")
    append_file("css/style.css", """
/* Online Status */
.status-dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-left: 6px;
    vertical-align: middle;
}
.status-dot.online { background: #27ae60; }
.status-dot.offline { background: #999; }
.last-seen { font-size: 11px; color: #999; }
""")
    return "Add online status tracker with heartbeat and last seen"


# ── STEP 20: Stories/Status updates ───────────────────────────────────────
@step
def step_20():
    write_file("js/stories.js", """\
// FriendZone - Stories Module
const Stories = {
    create(userId, userName, content, bgColor) {
        const stories = JSON.parse(localStorage.getItem("fz_stories") || "[]");
        stories.unshift({
            id: Date.now().toString(),
            userId,
            userName,
            content,
            bgColor: bgColor || "#4a90d9",
            viewers: [],
            createdAt: new Date().toISOString(),
            expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
        });
        localStorage.setItem("fz_stories", JSON.stringify(stories));
    },

    getActive() {
        const now = new Date();
        const stories = JSON.parse(localStorage.getItem("fz_stories") || "[]");
        return stories.filter(s => new Date(s.expiresAt) > now);
    },

    getByUser(userId) {
        return this.getActive().filter(s => s.userId === userId);
    },

    markViewed(storyId, userId) {
        const stories = JSON.parse(localStorage.getItem("fz_stories") || "[]");
        const story = stories.find(s => s.id === storyId);
        if (story && !story.viewers.includes(userId)) {
            story.viewers.push(userId);
            localStorage.setItem("fz_stories", JSON.stringify(stories));
        }
    },

    renderStoryBar(currentUserId) {
        const active = this.getActive();
        const userStories = {};
        active.forEach(s => {
            if (!userStories[s.userId]) userStories[s.userId] = { user: s.userName, stories: [], hasUnread: false };
            userStories[s.userId].stories.push(s);
            if (!s.viewers.includes(currentUserId)) userStories[s.userId].hasUnread = true;
        });

        let html = '<div class="story-bar"><div class="story-item add-story" id="add-story"><div class="story-avatar">+</div><span>Add Story</span></div>';
        Object.entries(userStories).forEach(([uid, data]) => {
            html += '<div class="story-item" data-user="' + uid + '"><div class="story-avatar ' +
                (data.hasUnread ? 'has-unread' : '') + '">' + data.user.charAt(0) + '</div><span>' +
                data.user.split(' ')[0] + '</span></div>';
        });
        html += '</div>';
        return html;
    },

    renderStoryViewer(story) {
        return '<div class="story-viewer" style="background:' + story.bgColor + '">' +
            '<div class="story-header"><strong>' + story.userName + '</strong>' +
            '<span class="post-time">' + Feed.timeAgo(new Date(story.createdAt)) + '</span>' +
            '<button class="story-close" id="close-story">X</button></div>' +
            '<div class="story-content"><p>' + story.content + '</p></div>' +
            '<div class="story-footer">' + story.viewers.length + ' viewers</div></div>';
    },

    renderCreateStory() {
        return '<div class="auth-container"><h2>Create Story</h2>' +
            '<textarea id="story-text" placeholder="What is on your mind?" rows="3"></textarea>' +
            '<div class="color-picker">' +
            ['#4a90d9','#e74c3c','#27ae60','#f39c12','#9b59b6','#1abc9c','#e67e22','#2c3e50'].map(c =>
                '<span class="color-option" data-color="' + c + '" style="background:' + c + '"></span>'
            ).join('') + '</div>' +
            '<button class="btn btn-primary" id="post-story">Share Story</button></div>';
    }
};
""")
    append_file("css/style.css", """
/* Stories */
.story-bar {
    display: flex;
    gap: 12px;
    padding: 12px 0;
    overflow-x: auto;
    margin-bottom: 16px;
}
.story-item { text-align: center; cursor: pointer; min-width: 70px; }
.story-item span { display: block; font-size: 12px; margin-top: 4px; color: #666; }
.story-avatar {
    width: 56px; height: 56px; border-radius: 50%;
    background: #4a90d9; color: white;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; font-weight: bold; margin: 0 auto;
    border: 3px solid #ddd;
}
.story-avatar.has-unread { border-color: #4a90d9; }
.add-story .story-avatar { background: #e4e6eb; color: #4a90d9; border: 2px dashed #4a90d9; }
.story-viewer {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    display: flex; flex-direction: column; justify-content: center;
    align-items: center; color: white; z-index: 999;
}
.story-header { position: absolute; top: 16px; left: 16px; right: 16px; display: flex; align-items: center; gap: 8px; }
.story-close { margin-left: auto; background: rgba(255,255,255,0.3); border: none; color: white; width: 32px; height: 32px; border-radius: 50%; cursor: pointer; font-size: 16px; }
.story-content { font-size: 24px; text-align: center; padding: 40px; max-width: 500px; }
.story-footer { position: absolute; bottom: 16px; font-size: 13px; opacity: 0.8; }
.color-picker { display: flex; gap: 8px; margin: 12px 0; }
.color-option { width: 32px; height: 32px; border-radius: 50%; cursor: pointer; border: 2px solid transparent; }
.color-option:hover { border-color: #333; }
""")
    return "Add stories feature with 24h expiry, viewer tracking, and color picker"


# ── STEP 21: Hashtag system ───────────────────────────────────────────────
@step
def step_21():
    write_file("js/hashtags.js", """\
// FriendZone - Hashtag System
const Hashtags = {
    extract(text) {
        const matches = text.match(/#[a-zA-Z0-9_]+/g);
        return matches ? [...new Set(matches.map(h => h.toLowerCase()))] : [];
    },

    getIndex() {
        return JSON.parse(localStorage.getItem("fz_hashtag_index") || "{}");
    },

    indexPost(postId, content) {
        const tags = this.extract(content);
        const index = this.getIndex();
        tags.forEach(tag => {
            if (!index[tag]) index[tag] = [];
            if (!index[tag].includes(postId)) index[tag].push(postId);
        });
        localStorage.setItem("fz_hashtag_index", JSON.stringify(index));
    },

    getTrending(limit) {
        limit = limit || 10;
        const index = this.getIndex();
        return Object.entries(index)
            .map(([tag, postIds]) => ({ tag, count: postIds.length }))
            .sort((a, b) => b.count - a.count)
            .slice(0, limit);
    },

    getPostsByTag(tag) {
        const index = this.getIndex();
        const postIds = index[tag.toLowerCase()] || [];
        const allPosts = JSON.parse(localStorage.getItem("fz_posts") || "[]");
        return allPosts.filter(p => postIds.includes(p.id));
    },

    renderTrending() {
        const trending = this.getTrending(10);
        if (trending.length === 0) return '<p class="empty-feed">No trending topics yet.</p>';
        return '<div class="trending-list">' +
            trending.map((t, i) => '<div class="trending-item">' +
                '<span class="trending-rank">' + (i + 1) + '</span>' +
                '<div class="trending-info"><strong>' + t.tag + '</strong>' +
                '<span>' + t.count + ' posts</span></div></div>'
            ).join("") + '</div>';
    },

    highlightInText(text) {
        return text.replace(/#[a-zA-Z0-9_]+/g, function(match) {
            return '<span class="hashtag">' + match + '</span>';
        });
    }
};
""")
    append_file("css/style.css", """
/* Hashtags & Trending */
.hashtag { color: #4a90d9; cursor: pointer; font-weight: 500; }
.hashtag:hover { text-decoration: underline; }
.trending-list { max-width: 350px; }
.trending-item {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 12px; background: white; border-radius: 8px;
    margin-bottom: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.trending-rank { font-size: 18px; font-weight: bold; color: #4a90d9; min-width: 24px; }
.trending-info span { display: block; font-size: 12px; color: #999; }
[data-theme="dark"] .trending-item { background: #242526; }
""")
    return "Add hashtag system with extraction, indexing, and trending topics"


# ── STEP 22: Bookmarks / Saved Posts ──────────────────────────────────────
@step
def step_22():
    write_file("js/bookmarks.js", """\
// FriendZone - Bookmarks Module
const Bookmarks = {
    toggle(userId, postId) {
        const key = "fz_bookmarks_" + userId;
        const bookmarks = JSON.parse(localStorage.getItem(key) || "[]");
        const idx = bookmarks.indexOf(postId);
        if (idx === -1) {
            bookmarks.push(postId);
        } else {
            bookmarks.splice(idx, 1);
        }
        localStorage.setItem(key, JSON.stringify(bookmarks));
        return idx === -1;
    },

    isBookmarked(userId, postId) {
        const key = "fz_bookmarks_" + userId;
        const bookmarks = JSON.parse(localStorage.getItem(key) || "[]");
        return bookmarks.includes(postId);
    },

    getAll(userId) {
        const key = "fz_bookmarks_" + userId;
        const bookmarkIds = JSON.parse(localStorage.getItem(key) || "[]");
        const allPosts = JSON.parse(localStorage.getItem("fz_posts") || "[]");
        return allPosts.filter(p => bookmarkIds.includes(p.id));
    },

    getCount(userId) {
        const key = "fz_bookmarks_" + userId;
        return JSON.parse(localStorage.getItem(key) || "[]").length;
    },

    renderBookmarksPage(userId) {
        const posts = this.getAll(userId);
        if (posts.length === 0) {
            return '<div class="empty-feed"><p>No saved posts yet. Bookmark posts to find them here later.</p></div>';
        }
        return '<div class="bookmarks-page"><h2>Saved Posts (' + posts.length + ')</h2>' +
            posts.map(p => Feed.renderPost(p, userId)).join("") + '</div>';
    },

    renderBookmarkButton(userId, postId) {
        const saved = this.isBookmarked(userId, postId);
        return '<button class="btn-bookmark ' + (saved ? 'saved' : '') +
            '" data-post="' + postId + '">' + (saved ? 'Saved' : 'Save') + '</button>';
    }
};
""")
    append_file("css/style.css", """
/* Bookmarks */
.btn-bookmark {
    background: none; border: 1px solid #ddd; border-radius: 6px;
    padding: 4px 12px; font-size: 13px; cursor: pointer; color: #666;
}
.btn-bookmark.saved { background: #4a90d9; color: white; border-color: #4a90d9; }
.btn-bookmark:hover { background: #f0f2f5; }
.btn-bookmark.saved:hover { background: #3a7bc8; }
.bookmarks-page h2 { margin-bottom: 16px; }
""")
    return "Add bookmarks system for saving and organizing posts"


# ── STEP 23: Report & Block users ─────────────────────────────────────────
@step
def step_23():
    write_file("js/moderation.js", """\
// FriendZone - Moderation Module
const Moderation = {
    reportContent(reporterId, contentType, contentId, reason) {
        const reports = JSON.parse(localStorage.getItem("fz_reports") || "[]");
        reports.push({
            id: Date.now().toString(),
            reporterId,
            contentType,
            contentId,
            reason,
            status: "pending",
            createdAt: new Date().toISOString()
        });
        localStorage.setItem("fz_reports", JSON.stringify(reports));
        return true;
    },

    blockUser(userId, blockedId) {
        const key = "fz_blocked_" + userId;
        const blocked = JSON.parse(localStorage.getItem(key) || "[]");
        if (!blocked.includes(blockedId)) {
            blocked.push(blockedId);
            localStorage.setItem(key, JSON.stringify(blocked));
        }
    },

    unblockUser(userId, blockedId) {
        const key = "fz_blocked_" + userId;
        let blocked = JSON.parse(localStorage.getItem(key) || "[]");
        blocked = blocked.filter(id => id !== blockedId);
        localStorage.setItem(key, JSON.stringify(blocked));
    },

    isBlocked(userId, targetId) {
        const key = "fz_blocked_" + userId;
        const blocked = JSON.parse(localStorage.getItem(key) || "[]");
        return blocked.includes(targetId);
    },

    getBlockedList(userId) {
        const key = "fz_blocked_" + userId;
        const blockedIds = JSON.parse(localStorage.getItem(key) || "[]");
        const users = JSON.parse(localStorage.getItem("fz_users") || "[]");
        return users.filter(u => blockedIds.includes(u.id));
    },

    renderReportForm(contentType, contentId) {
        const reasons = ["Spam", "Harassment", "Inappropriate content", "Misinformation", "Other"];
        return '<div class="report-form"><h3>Report ' + contentType + '</h3>' +
            '<div class="report-reasons">' +
            reasons.map(r => '<label class="report-reason"><input type="radio" name="report-reason" value="' + r + '"> ' + r + '</label>').join("") +
            '</div><textarea id="report-details" placeholder="Additional details (optional)..." rows="3"></textarea>' +
            '<button class="btn btn-primary" id="submit-report" data-type="' + contentType + '" data-id="' + contentId + '">Submit Report</button></div>';
    },

    renderBlockedList(userId) {
        const blocked = this.getBlockedList(userId);
        if (blocked.length === 0) return '<p>No blocked users.</p>';
        return '<div class="blocked-list">' + blocked.map(u =>
            '<div class="blocked-item"><div class="post-avatar">' + u.name.charAt(0) + '</div>' +
            '<strong>' + u.name + '</strong>' +
            '<button class="btn btn-secondary btn-sm" data-unblock="' + u.id + '">Unblock</button></div>'
        ).join("") + '</div>';
    }
};
""")
    append_file("css/style.css", """
/* Moderation */
.report-form { max-width: 400px; margin: 20px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.report-form h3 { margin-bottom: 12px; }
.report-reasons { margin-bottom: 12px; }
.report-reason { display: block; padding: 6px 0; cursor: pointer; }
.report-form textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 12px; font-family: inherit; }
.blocked-list { max-width: 400px; }
.blocked-item { display: flex; align-items: center; gap: 12px; padding: 10px; background: white; border-radius: 8px; margin-bottom: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
[data-theme="dark"] .report-form, [data-theme="dark"] .blocked-item { background: #242526; }
""")
    return "Add content reporting and user blocking system"


# ── STEP 24: Activity log ─────────────────────────────────────────────────
@step
def step_24():
    write_file("js/activity.js", """\
// FriendZone - Activity Log
const ActivityLog = {
    log(userId, action, details) {
        const logs = JSON.parse(localStorage.getItem("fz_activity") || "[]");
        logs.unshift({
            id: Date.now().toString(),
            userId,
            action,
            details,
            timestamp: new Date().toISOString()
        });
        // Keep only last 500 entries
        if (logs.length > 500) logs.length = 500;
        localStorage.setItem("fz_activity", JSON.stringify(logs));
    },

    getForUser(userId, limit) {
        limit = limit || 50;
        const logs = JSON.parse(localStorage.getItem("fz_activity") || "[]");
        return logs.filter(l => l.userId === userId).slice(0, limit);
    },

    getActionIcon(action) {
        const icons = {
            post_created: "New post",
            post_liked: "Liked a post",
            comment_added: "Commented",
            friend_added: "New friend",
            profile_updated: "Profile updated",
            story_created: "Shared a story",
            login: "Logged in",
            settings_changed: "Settings updated"
        };
        return icons[action] || action;
    },

    renderActivityLog(userId) {
        const logs = this.getForUser(userId, 50);
        if (logs.length === 0) return '<div class="empty-feed"><p>No activity yet.</p></div>';
        return '<div class="activity-log">' + logs.map(l =>
            '<div class="activity-item"><div class="activity-dot"></div>' +
            '<div class="activity-body"><strong>' + this.getActionIcon(l.action) + '</strong>' +
            (l.details ? '<p>' + l.details + '</p>' : '') +
            '<span class="post-time">' + Feed.timeAgo(new Date(l.timestamp)) + '</span></div></div>'
        ).join("") + '</div>';
    },

    renderActivitySummary(userId) {
        const logs = this.getForUser(userId, 100);
        const today = new Date().toDateString();
        const todayCount = logs.filter(l => new Date(l.timestamp).toDateString() === today).length;
        const weekAgo = new Date(Date.now() - 7 * 86400000);
        const weekCount = logs.filter(l => new Date(l.timestamp) > weekAgo).length;
        return '<div class="activity-summary">' +
            '<div class="summary-stat"><strong>' + todayCount + '</strong><span>Today</span></div>' +
            '<div class="summary-stat"><strong>' + weekCount + '</strong><span>This week</span></div>' +
            '<div class="summary-stat"><strong>' + logs.length + '</strong><span>Total</span></div></div>';
    }
};
""")
    append_file("css/style.css", """
/* Activity Log */
.activity-log { max-width: 500px; position: relative; padding-left: 20px; }
.activity-item { display: flex; gap: 12px; padding: 10px 0; border-left: 2px solid #e4e6eb; padding-left: 16px; margin-left: -20px; }
.activity-dot { width: 10px; height: 10px; border-radius: 50%; background: #4a90d9; margin-top: 4px; flex-shrink: 0; margin-left: -22px; }
.activity-body p { margin: 2px 0; font-size: 13px; color: #666; }
.activity-summary { display: flex; gap: 24px; padding: 16px; background: white; border-radius: 8px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
.summary-stat { text-align: center; }
.summary-stat strong { display: block; font-size: 20px; color: #4a90d9; }
.summary-stat span { font-size: 12px; color: #999; }
[data-theme="dark"] .activity-summary { background: #242526; }
[data-theme="dark"] .activity-item { border-left-color: #3a3b3c; }
""")
    return "Add activity log with timeline view and weekly summary"


# ── STEP 25: Groups feature ───────────────────────────────────────────────
@step
def step_25():
    write_file("js/groups.js", """\
// FriendZone - Groups Module
const Groups = {
    create(name, description, creatorId) {
        const groups = JSON.parse(localStorage.getItem("fz_groups") || "[]");
        const group = {
            id: Date.now().toString(),
            name,
            description,
            creatorId,
            members: [creatorId],
            admins: [creatorId],
            posts: [],
            createdAt: new Date().toISOString()
        };
        groups.push(group);
        localStorage.setItem("fz_groups", JSON.stringify(groups));
        return group;
    },

    getAll() {
        return JSON.parse(localStorage.getItem("fz_groups") || "[]");
    },

    getById(groupId) {
        return this.getAll().find(g => g.id === groupId);
    },

    getUserGroups(userId) {
        return this.getAll().filter(g => g.members.includes(userId));
    },

    join(groupId, userId) {
        const groups = this.getAll();
        const group = groups.find(g => g.id === groupId);
        if (group && !group.members.includes(userId)) {
            group.members.push(userId);
            localStorage.setItem("fz_groups", JSON.stringify(groups));
            return true;
        }
        return false;
    },

    leave(groupId, userId) {
        const groups = this.getAll();
        const group = groups.find(g => g.id === groupId);
        if (group) {
            group.members = group.members.filter(m => m !== userId);
            group.admins = group.admins.filter(a => a !== userId);
            localStorage.setItem("fz_groups", JSON.stringify(groups));
        }
    },

    addPost(groupId, userId, userName, content) {
        const groups = this.getAll();
        const group = groups.find(g => g.id === groupId);
        if (!group || !group.members.includes(userId)) return null;
        const post = {
            id: Date.now().toString(), userId, userName, content,
            likes: [], comments: [], createdAt: new Date().toISOString()
        };
        group.posts.unshift(post);
        localStorage.setItem("fz_groups", JSON.stringify(groups));
        return post;
    },

    renderGroupsList(userId) {
        const userGroups = this.getUserGroups(userId);
        const allGroups = this.getAll();
        let html = '<div class="groups-page"><h2>My Groups</h2>';
        if (userGroups.length === 0) {
            html += '<p class="empty-feed">You have not joined any groups yet.</p>';
        } else {
            html += '<div class="groups-grid">' + userGroups.map(g =>
                '<div class="group-card"><h3>' + g.name + '</h3>' +
                '<p>' + g.description.substring(0, 80) + '</p>' +
                '<span class="group-members">' + g.members.length + ' members</span></div>'
            ).join("") + '</div>';
        }
        html += '<h2 style="margin-top:24px;">Discover Groups</h2><div class="groups-grid">' +
            allGroups.filter(g => !g.members.includes(userId)).map(g =>
                '<div class="group-card"><h3>' + g.name + '</h3>' +
                '<p>' + g.description.substring(0, 80) + '</p>' +
                '<span class="group-members">' + g.members.length + ' members</span>' +
                '<button class="btn btn-primary btn-sm" data-join="' + g.id + '">Join</button></div>'
            ).join("") + '</div></div>';
        return html;
    },

    renderCreateGroup() {
        return '<div class="auth-container"><h2>Create Group</h2>' +
            '<form id="create-group-form">' +
            '<input type="text" id="group-name" placeholder="Group name" required>' +
            '<textarea id="group-desc" placeholder="Group description..." rows="3"></textarea>' +
            '<button type="submit" class="btn btn-primary">Create Group</button></form></div>';
    }
};
""")
    append_file("css/style.css", """
/* Groups */
.groups-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 12px; }
.group-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
.group-card h3 { margin-bottom: 8px; }
.group-card p { color: #666; font-size: 13px; margin-bottom: 8px; }
.group-members { font-size: 12px; color: #999; display: block; margin-bottom: 8px; }
[data-theme="dark"] .group-card { background: #242526; }
""")
    return "Add groups feature with create, join, leave, and group posts"


# ── STEP 26: Events feature ───────────────────────────────────────────────
@step
def step_26():
    write_file("js/events.js", """\
// FriendZone - Events Module
const Events = {
    create(title, description, date, location, creatorId) {
        const events = JSON.parse(localStorage.getItem("fz_events") || "[]");
        const event = {
            id: Date.now().toString(),
            title, description, date, location, creatorId,
            attendees: [creatorId],
            interested: [],
            createdAt: new Date().toISOString()
        };
        events.push(event);
        localStorage.setItem("fz_events", JSON.stringify(events));
        return event;
    },

    getUpcoming() {
        const now = new Date();
        return JSON.parse(localStorage.getItem("fz_events") || "[]")
            .filter(e => new Date(e.date) > now)
            .sort((a, b) => new Date(a.date) - new Date(b.date));
    },

    getPast() {
        const now = new Date();
        return JSON.parse(localStorage.getItem("fz_events") || "[]")
            .filter(e => new Date(e.date) <= now)
            .sort((a, b) => new Date(b.date) - new Date(a.date));
    },

    attend(eventId, userId) {
        const events = JSON.parse(localStorage.getItem("fz_events") || "[]");
        const event = events.find(e => e.id === eventId);
        if (event && !event.attendees.includes(userId)) {
            event.attendees.push(userId);
            event.interested = event.interested.filter(id => id !== userId);
            localStorage.setItem("fz_events", JSON.stringify(events));
        }
    },

    markInterested(eventId, userId) {
        const events = JSON.parse(localStorage.getItem("fz_events") || "[]");
        const event = events.find(e => e.id === eventId);
        if (event && !event.interested.includes(userId) && !event.attendees.includes(userId)) {
            event.interested.push(userId);
            localStorage.setItem("fz_events", JSON.stringify(events));
        }
    },

    renderEventsPage(userId) {
        const upcoming = this.getUpcoming();
        let html = '<div class="events-page"><h2>Upcoming Events</h2>';
        if (upcoming.length === 0) {
            html += '<p class="empty-feed">No upcoming events.</p>';
        } else {
            html += upcoming.map(e => this.renderEventCard(e, userId)).join("");
        }
        html += '<button class="btn btn-primary" id="create-event" style="margin-top:16px;">Create Event</button></div>';
        return html;
    },

    renderEventCard(event, userId) {
        const eventDate = new Date(event.date);
        const month = eventDate.toLocaleString('default', { month: 'short' }).toUpperCase();
        const day = eventDate.getDate();
        const isAttending = event.attendees.includes(userId);
        return '<div class="event-card"><div class="event-date-badge"><span class="event-month">' + month + '</span>' +
            '<span class="event-day">' + day + '</span></div>' +
            '<div class="event-info"><h3>' + event.title + '</h3>' +
            '<p class="event-location">' + event.location + '</p>' +
            '<span class="event-attendees">' + event.attendees.length + ' going / ' + event.interested.length + ' interested</span></div>' +
            '<div class="event-actions">' +
            (isAttending ? '<button class="btn btn-secondary btn-sm">Going</button>' :
                '<button class="btn btn-primary btn-sm" data-attend="' + event.id + '">Attend</button>') +
            '</div></div>';
    },

    renderCreateEvent() {
        return '<div class="auth-container"><h2>Create Event</h2>' +
            '<form id="create-event-form">' +
            '<input type="text" id="event-title" placeholder="Event title" required>' +
            '<textarea id="event-desc" placeholder="Description..." rows="3"></textarea>' +
            '<input type="datetime-local" id="event-date" required>' +
            '<input type="text" id="event-location" placeholder="Location" required>' +
            '<button type="submit" class="btn btn-primary">Create Event</button></form></div>';
    }
};
""")
    append_file("css/style.css", """
/* Events */
.event-card {
    display: flex; gap: 16px; align-items: center; padding: 16px;
    background: white; border-radius: 8px; margin-bottom: 8px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}
.event-date-badge {
    min-width: 56px; text-align: center; background: #f0f2f5;
    border-radius: 8px; padding: 8px;
}
.event-month { display: block; font-size: 11px; font-weight: bold; color: #e74c3c; text-transform: uppercase; }
.event-day { display: block; font-size: 24px; font-weight: bold; }
.event-info { flex: 1; }
.event-info h3 { margin-bottom: 4px; }
.event-location { color: #666; font-size: 13px; margin-bottom: 4px; }
.event-attendees { font-size: 12px; color: #999; }
[data-theme="dark"] .event-card { background: #242526; }
[data-theme="dark"] .event-date-badge { background: #3a3b3c; }
""")
    return "Add events feature with create, attend, and event calendar cards"


# ── STEP 27: Polls in posts ───────────────────────────────────────────────
@step
def step_27():
    write_file("js/polls.js", """\
// FriendZone - Polls Module
const Polls = {
    create(userId, userName, question, options) {
        const polls = JSON.parse(localStorage.getItem("fz_polls") || "[]");
        const poll = {
            id: Date.now().toString(),
            userId, userName, question,
            options: options.map(o => ({ text: o, votes: [] })),
            createdAt: new Date().toISOString(),
            expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
        };
        polls.push(poll);
        localStorage.setItem("fz_polls", JSON.stringify(polls));
        return poll;
    },

    vote(pollId, optionIndex, userId) {
        const polls = JSON.parse(localStorage.getItem("fz_polls") || "[]");
        const poll = polls.find(p => p.id === pollId);
        if (!poll) return false;

        // Remove previous vote
        poll.options.forEach(o => {
            o.votes = o.votes.filter(v => v !== userId);
        });
        // Add new vote
        if (poll.options[optionIndex]) {
            poll.options[optionIndex].votes.push(userId);
        }
        localStorage.setItem("fz_polls", JSON.stringify(polls));
        return true;
    },

    hasVoted(pollId, userId) {
        const polls = JSON.parse(localStorage.getItem("fz_polls") || "[]");
        const poll = polls.find(p => p.id === pollId);
        if (!poll) return false;
        return poll.options.some(o => o.votes.includes(userId));
    },

    getTotalVotes(poll) {
        return poll.options.reduce((sum, o) => sum + o.votes.length, 0);
    },

    renderPoll(poll, userId) {
        const voted = this.hasVoted(poll.id, userId);
        const total = this.getTotalVotes(poll);
        const expired = new Date(poll.expiresAt) < new Date();

        let html = '<div class="poll-card"><div class="post-header">' +
            '<div class="post-avatar">' + poll.userName.charAt(0) + '</div>' +
            '<div><strong>' + poll.userName + '</strong><span class="post-time">' +
            Feed.timeAgo(new Date(poll.createdAt)) + '</span></div></div>' +
            '<h3 class="poll-question">' + poll.question + '</h3><div class="poll-options">';

        poll.options.forEach(function(opt, i) {
            const pct = total > 0 ? Math.round((opt.votes.length / total) * 100) : 0;
            const isMyVote = opt.votes.includes(userId);
            if (voted || expired) {
                html += '<div class="poll-result"><div class="poll-bar" style="width:' + pct + '%"></div>' +
                    '<span class="poll-option-text">' + opt.text + (isMyVote ? ' (your vote)' : '') + '</span>' +
                    '<span class="poll-pct">' + pct + '%</span></div>';
            } else {
                html += '<button class="poll-vote-btn" data-poll="' + poll.id + '" data-option="' + i + '">' + opt.text + '</button>';
            }
        });

        html += '</div><div class="poll-footer">' + total + ' votes' +
            (expired ? ' - Poll ended' : ' - ' + Feed.timeAgo(new Date(poll.expiresAt)) + ' left') + '</div></div>';
        return html;
    },

    renderCreatePoll() {
        return '<div class="auth-container"><h2>Create Poll</h2>' +
            '<input type="text" id="poll-question" placeholder="Ask a question..." required>' +
            '<div id="poll-options-list">' +
            '<input type="text" class="poll-option-input" placeholder="Option 1" required>' +
            '<input type="text" class="poll-option-input" placeholder="Option 2" required></div>' +
            '<button class="btn btn-secondary" id="add-poll-option">+ Add option</button>' +
            '<button class="btn btn-primary" id="submit-poll" style="margin-top:12px;">Create Poll</button></div>';
    }
};
""")
    append_file("css/style.css", """
/* Polls */
.poll-card { background: white; padding: 16px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
.poll-question { margin: 12px 0; font-size: 16px; }
.poll-options { display: flex; flex-direction: column; gap: 8px; }
.poll-vote-btn {
    width: 100%; padding: 10px 16px; text-align: left;
    border: 2px solid #4a90d9; border-radius: 8px; background: none;
    cursor: pointer; font-size: 14px; transition: background 0.2s;
}
.poll-vote-btn:hover { background: #e8f0fe; }
.poll-result { position: relative; padding: 10px 16px; border-radius: 8px; background: #f0f2f5; overflow: hidden; }
.poll-bar { position: absolute; top: 0; left: 0; bottom: 0; background: #d4e4f7; border-radius: 8px; z-index: 0; transition: width 0.5s ease; }
.poll-option-text { position: relative; z-index: 1; }
.poll-pct { position: relative; z-index: 1; float: right; font-weight: bold; }
.poll-footer { margin-top: 8px; font-size: 12px; color: #999; }
.poll-option-input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 8px; }
[data-theme="dark"] .poll-card { background: #242526; }
[data-theme="dark"] .poll-result { background: #3a3b3c; }
[data-theme="dark"] .poll-bar { background: #2d4a6e; }
""")
    return "Add polls feature with voting, results bar, and expiration"


# ── STEP 28: Share / Repost ───────────────────────────────────────────────
@step
def step_28():
    write_file("js/share.js", """\
// FriendZone - Share / Repost Module
const Share = {
    repost(originalPostId, userId, userName, comment) {
        const posts = JSON.parse(localStorage.getItem("fz_posts") || "[]");
        const original = posts.find(p => p.id === originalPostId);
        if (!original) return null;

        const repost = {
            id: Date.now().toString(),
            userId, userName,
            content: comment || "",
            isRepost: true,
            originalPost: {
                id: original.id,
                userName: original.userName,
                content: original.content,
                createdAt: original.createdAt
            },
            likes: [], comments: [],
            createdAt: new Date().toISOString()
        };
        posts.unshift(repost);
        localStorage.setItem("fz_posts", JSON.stringify(posts));

        // Track share count
        const shares = JSON.parse(localStorage.getItem("fz_shares") || "{}");
        shares[originalPostId] = (shares[originalPostId] || 0) + 1;
        localStorage.setItem("fz_shares", JSON.stringify(shares));
        return repost;
    },

    getShareCount(postId) {
        const shares = JSON.parse(localStorage.getItem("fz_shares") || "{}");
        return shares[postId] || 0;
    },

    renderRepost(post, currentUserId) {
        const timeAgo = Feed.timeAgo(new Date(post.createdAt));
        return '<div class="post-card repost">' +
            '<div class="post-header"><div class="post-avatar">' + post.userName.charAt(0) + '</div>' +
            '<div><strong>' + post.userName + '</strong> shared a post<span class="post-time">' + timeAgo + '</span></div></div>' +
            (post.content ? '<div class="post-content">' + post.content + '</div>' : '') +
            '<div class="repost-original"><div class="post-header">' +
            '<div class="post-avatar" style="width:32px;height:32px;font-size:14px;">' + post.originalPost.userName.charAt(0) + '</div>' +
            '<div><strong>' + post.originalPost.userName + '</strong>' +
            '<span class="post-time">' + Feed.timeAgo(new Date(post.originalPost.createdAt)) + '</span></div></div>' +
            '<div class="post-content">' + post.originalPost.content + '</div></div>' +
            '<div class="post-actions">' +
            '<button class="btn-like" data-id="' + post.id + '"> ' + post.likes.length + '</button>' +
            '<button class="btn-comment" data-id="' + post.id + '"> ' + post.comments.length + '</button></div></div>';
    },

    renderShareButton(postId) {
        const count = this.getShareCount(postId);
        return '<button class="btn-share" data-id="' + postId + '">Share ' + (count > 0 ? count : '') + '</button>';
    },

    renderShareDialog(postId) {
        return '<div class="dialog-overlay" id="share-dialog">' +
            '<div class="dialog"><h3>Share this post</h3>' +
            '<textarea id="share-comment" placeholder="Add a comment (optional)..." rows="2"></textarea>' +
            '<div class="dialog-actions">' +
            '<button class="btn btn-secondary" id="cancel-share">Cancel</button>' +
            '<button class="btn btn-primary" id="confirm-share" data-post="' + postId + '">Share</button>' +
            '</div></div></div>';
    }
};
""")
    append_file("css/style.css", """
/* Share / Repost */
.repost-original {
    border: 1px solid #e4e6eb; border-radius: 8px;
    padding: 12px; margin: 8px 0; background: #fafafa;
}
.btn-share { background: none; border: none; cursor: pointer; font-size: 14px; padding: 4px 8px; border-radius: 4px; }
.btn-share:hover { background: #f0f2f5; }
[data-theme="dark"] .repost-original { background: #1e1e2e; border-color: #3a3b3c; }
""")
    return "Add share and repost functionality with share counts"


# ── STEP 29: Admin dashboard ──────────────────────────────────────────────
@step
def step_29():
    write_file("js/admin.js", """\
// FriendZone - Admin Dashboard
const Admin = {
    isAdmin(userId) {
        const admins = JSON.parse(localStorage.getItem("fz_admins") || "[]");
        return admins.includes(userId);
    },

    getStats() {
        const users = JSON.parse(localStorage.getItem("fz_users") || "[]");
        const posts = JSON.parse(localStorage.getItem("fz_posts") || "[]");
        const reports = JSON.parse(localStorage.getItem("fz_reports") || "[]");
        const messages = JSON.parse(localStorage.getItem("fz_messages") || "[]");
        const groups = JSON.parse(localStorage.getItem("fz_groups") || "[]");

        const today = new Date().toDateString();
        const newUsersToday = users.filter(u => new Date(u.createdAt).toDateString() === today).length;
        const postsToday = posts.filter(p => new Date(p.createdAt).toDateString() === today).length;
        const pendingReports = reports.filter(r => r.status === "pending").length;

        return {
            totalUsers: users.length,
            totalPosts: posts.length,
            totalMessages: messages.length,
            totalGroups: groups.length,
            newUsersToday, postsToday, pendingReports
        };
    },

    renderDashboard() {
        const stats = this.getStats();
        return '<div class="admin-dashboard"><h2>Admin Dashboard</h2>' +
            '<div class="admin-stats">' +
            this._statCard("Total Users", stats.totalUsers, "#4a90d9") +
            this._statCard("Total Posts", stats.totalPosts, "#27ae60") +
            this._statCard("Messages", stats.totalMessages, "#f39c12") +
            this._statCard("Groups", stats.totalGroups, "#9b59b6") +
            this._statCard("New Users Today", stats.newUsersToday, "#1abc9c") +
            this._statCard("Posts Today", stats.postsToday, "#e67e22") +
            this._statCard("Pending Reports", stats.pendingReports, "#e74c3c") +
            '</div>' +
            '<div class="admin-sections">' +
            '<div class="admin-section"><h3>Pending Reports</h3>' + this.renderPendingReports() + '</div>' +
            '<div class="admin-section"><h3>Recent Users</h3>' + this.renderRecentUsers() + '</div>' +
            '</div></div>';
    },

    _statCard(label, value, color) {
        return '<div class="admin-stat-card"><div class="stat-value" style="color:' + color + '">' + value + '</div>' +
            '<div class="stat-label">' + label + '</div></div>';
    },

    renderPendingReports() {
        const reports = JSON.parse(localStorage.getItem("fz_reports") || "[]").filter(r => r.status === "pending");
        if (reports.length === 0) return '<p>No pending reports.</p>';
        return reports.slice(0, 10).map(r =>
            '<div class="admin-report-item"><span class="report-type">' + r.contentType + '</span>' +
            '<span>' + r.reason + '</span><span class="post-time">' + Feed.timeAgo(new Date(r.createdAt)) + '</span>' +
            '<button class="btn btn-sm btn-secondary" data-dismiss="' + r.id + '">Dismiss</button>' +
            '<button class="btn btn-sm btn-danger" data-action="' + r.id + '">Take Action</button></div>'
        ).join("");
    },

    renderRecentUsers() {
        const users = JSON.parse(localStorage.getItem("fz_users") || "[]")
            .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt)).slice(0, 10);
        return users.map(u =>
            '<div class="admin-user-item"><div class="post-avatar" style="width:32px;height:32px;font-size:14px;">' + u.name.charAt(0) + '</div>' +
            '<strong>' + u.name + '</strong><span>' + u.email + '</span>' +
            '<span class="post-time">' + Feed.timeAgo(new Date(u.createdAt)) + '</span></div>'
        ).join("");
    }
};
""")
    append_file("css/style.css", """
/* Admin Dashboard */
.admin-dashboard { max-width: 900px; margin: 0 auto; }
.admin-stats { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; margin-bottom: 24px; }
.admin-stat-card { background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
.stat-value { font-size: 28px; font-weight: bold; }
.stat-label { font-size: 12px; color: #999; margin-top: 4px; }
.admin-sections { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.admin-section { background: white; padding: 16px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
.admin-section h3 { margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #eee; }
.admin-report-item, .admin-user-item { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid #f0f0f0; font-size: 13px; }
.report-type { background: #e8f0fe; color: #4a90d9; padding: 2px 8px; border-radius: 4px; font-size: 11px; }
[data-theme="dark"] .admin-stat-card, [data-theme="dark"] .admin-section { background: #242526; }
@media (max-width: 768px) { .admin-sections { grid-template-columns: 1fr; } }
""")
    return "Add admin dashboard with stats, reports, and user management"


# ── STEP 30: Backend friends routes ───────────────────────────────────────
@step
def step_30():
    write_file("backend/routes_friends.py", """\
\"\"\"FriendZone - Friend Routes\"\"\"
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Friendship, User

friends_bp = Blueprint("friends", __name__)


@friends_bp.route("/api/friends", methods=["GET"])
@jwt_required()
def get_friends():
    user_id = int(get_jwt_identity())
    friendships = Friendship.query.filter(
        ((Friendship.requester_id == user_id) | (Friendship.addressee_id == user_id)) &
        (Friendship.status == "accepted")
    ).all()

    friend_ids = []
    for f in friendships:
        friend_ids.append(f.addressee_id if f.requester_id == user_id else f.requester_id)

    friends = User.query.filter(User.id.in_(friend_ids)).all()
    return jsonify([{"id": f.id, "name": f.name, "email": f.email, "bio": f.bio} for f in friends])


@friends_bp.route("/api/friends/request", methods=["POST"])
@jwt_required()
def send_request():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    addressee_id = data["user_id"]

    existing = Friendship.query.filter(
        ((Friendship.requester_id == user_id) & (Friendship.addressee_id == addressee_id)) |
        ((Friendship.requester_id == addressee_id) & (Friendship.addressee_id == user_id))
    ).first()
    if existing:
        return jsonify({"error": "Friend request already exists"}), 400

    friendship = Friendship(requester_id=user_id, addressee_id=addressee_id)
    db.session.add(friendship)
    db.session.commit()
    return jsonify({"status": "pending", "id": friendship.id}), 201


@friends_bp.route("/api/friends/request/<int:request_id>/accept", methods=["POST"])
@jwt_required()
def accept_request(request_id):
    user_id = int(get_jwt_identity())
    friendship = Friendship.query.get(request_id)
    if not friendship or friendship.addressee_id != user_id:
        return jsonify({"error": "Request not found"}), 404
    friendship.status = "accepted"
    db.session.commit()
    return jsonify({"status": "accepted"})


@friends_bp.route("/api/friends/request/<int:request_id>/decline", methods=["POST"])
@jwt_required()
def decline_request(request_id):
    user_id = int(get_jwt_identity())
    friendship = Friendship.query.get(request_id)
    if not friendship or friendship.addressee_id != user_id:
        return jsonify({"error": "Request not found"}), 404
    db.session.delete(friendship)
    db.session.commit()
    return jsonify({"status": "declined"})


@friends_bp.route("/api/friends/pending", methods=["GET"])
@jwt_required()
def get_pending():
    user_id = int(get_jwt_identity())
    pending = Friendship.query.filter_by(addressee_id=user_id, status="pending").all()
    users = User.query.filter(User.id.in_([p.requester_id for p in pending])).all()
    user_map = {u.id: u for u in users}
    return jsonify([{
        "id": p.id,
        "from": {"id": p.requester_id, "name": user_map[p.requester_id].name if p.requester_id in user_map else "Unknown"},
        "created_at": p.created_at.isoformat()
    } for p in pending])
""")
    return "Add backend friend request routes with accept and decline"


# ── STEP 31: Backend messaging routes ─────────────────────────────────────
@step
def step_31():
    write_file("backend/routes_messages.py", """\
\"\"\"FriendZone - Messaging Routes\"\"\"
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Message, User

messages_bp = Blueprint("messages", __name__)


@messages_bp.route("/api/messages/conversations", methods=["GET"])
@jwt_required()
def get_conversations():
    user_id = int(get_jwt_identity())
    sent = Message.query.filter_by(sender_id=user_id).all()
    received = Message.query.filter_by(receiver_id=user_id).all()

    all_messages = sent + received
    convos = {}
    for m in all_messages:
        other_id = m.receiver_id if m.sender_id == user_id else m.sender_id
        if other_id not in convos or m.created_at > convos[other_id]["last_at"]:
            convos[other_id] = {"user_id": other_id, "last_message": m.text, "last_at": m.created_at}

    users = User.query.filter(User.id.in_(convos.keys())).all()
    user_map = {u.id: u.name for u in users}

    return jsonify([{
        "user_id": uid,
        "user_name": user_map.get(uid, "Unknown"),
        "last_message": data["last_message"][:60],
        "last_at": data["last_at"].isoformat()
    } for uid, data in sorted(convos.items(), key=lambda x: x[1]["last_at"], reverse=True)])


@messages_bp.route("/api/messages/<int:other_user_id>", methods=["GET"])
@jwt_required()
def get_thread(other_user_id):
    user_id = int(get_jwt_identity())
    messages = Message.query.filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == other_user_id)) |
        ((Message.sender_id == other_user_id) & (Message.receiver_id == user_id))
    ).order_by(Message.created_at.asc()).all()

    # Mark as read
    for m in messages:
        if m.receiver_id == user_id and not m.read:
            m.read = True
    db.session.commit()

    return jsonify([{
        "id": m.id, "from": m.sender_id, "to": m.receiver_id,
        "text": m.text, "read": m.read, "created_at": m.created_at.isoformat()
    } for m in messages])


@messages_bp.route("/api/messages", methods=["POST"])
@jwt_required()
def send_message():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    msg = Message(sender_id=user_id, receiver_id=data["to"], text=data["text"])
    db.session.add(msg)
    db.session.commit()
    return jsonify({"id": msg.id, "text": msg.text, "created_at": msg.created_at.isoformat()}), 201


@messages_bp.route("/api/messages/unread", methods=["GET"])
@jwt_required()
def unread_count():
    user_id = int(get_jwt_identity())
    count = Message.query.filter_by(receiver_id=user_id, read=False).count()
    return jsonify({"unread": count})
""")
    return "Add backend messaging routes with threads and read receipts"


# ── STEP 32: Backend search & user routes ─────────────────────────────────
@step
def step_32():
    write_file("backend/routes_search.py", """\
\"\"\"FriendZone - Search Routes\"\"\"
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import User, Post

search_bp = Blueprint("search", __name__)


@search_bp.route("/api/search", methods=["GET"])
@jwt_required()
def search():
    q = request.args.get("q", "").strip()
    search_type = request.args.get("type", "all")

    if len(q) < 2:
        return jsonify({"error": "Query must be at least 2 characters"}), 400

    results = {"users": [], "posts": []}

    if search_type in ("all", "users"):
        users = User.query.filter(
            User.name.ilike(f"%{q}%") | User.email.ilike(f"%{q}%")
        ).limit(20).all()
        results["users"] = [{"id": u.id, "name": u.name, "bio": u.bio} for u in users]

    if search_type in ("all", "posts"):
        posts = Post.query.filter(
            Post.content.ilike(f"%{q}%")
        ).order_by(Post.created_at.desc()).limit(20).all()
        results["posts"] = [{
            "id": p.id, "content": p.content, "user_id": p.user_id,
            "author_name": p.author.name, "created_at": p.created_at.isoformat()
        } for p in posts]

    return jsonify(results)


@search_bp.route("/api/users/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    post_count = Post.query.filter_by(user_id=user_id).count()
    return jsonify({
        "id": user.id, "name": user.name, "email": user.email,
        "bio": user.bio, "avatar_url": user.avatar_url,
        "post_count": post_count, "created_at": user.created_at.isoformat()
    })


@search_bp.route("/api/users/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    from flask_jwt_extended import get_jwt_identity
    current_id = int(get_jwt_identity())
    if current_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    from flask import request as req
    data = req.get_json()
    if "name" in data:
        user.name = data["name"]
    if "bio" in data:
        user.bio = data["bio"]
    from models import db
    db.session.commit()
    return jsonify({"id": user.id, "name": user.name, "bio": user.bio})
""")
    return "Add backend search and user profile routes"


# ── STEP 33: Frontend API service ─────────────────────────────────────────
@step
def step_33():
    write_file("js/api.js", """\
// FriendZone - API Service Layer
const API = {
    baseUrl: "http://localhost:5000",
    token: null,

    init() {
        this.token = localStorage.getItem("fz_api_token");
    },

    setToken(token) {
        this.token = token;
        localStorage.setItem("fz_api_token", token);
    },

    clearToken() {
        this.token = null;
        localStorage.removeItem("fz_api_token");
    },

    async request(method, endpoint, data) {
        const headers = { "Content-Type": "application/json" };
        if (this.token) headers["Authorization"] = "Bearer " + this.token;

        const config = { method, headers };
        if (data && (method === "POST" || method === "PUT")) {
            config.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(this.baseUrl + endpoint, config);
            const json = await response.json();
            if (!response.ok) {
                throw new Error(json.error || "Request failed");
            }
            return json;
        } catch (err) {
            console.error("API Error:", err.message);
            throw err;
        }
    },

    // Auth
    async login(email, password) {
        const result = await this.request("POST", "/api/auth/login", { email, password });
        this.setToken(result.token);
        return result;
    },

    async signup(name, email, password) {
        const result = await this.request("POST", "/api/auth/signup", { name, email, password });
        this.setToken(result.token);
        return result;
    },

    async getMe() {
        return this.request("GET", "/api/auth/me");
    },

    // Posts
    async getPosts(page) {
        return this.request("GET", "/api/posts?page=" + (page || 1));
    },

    async createPost(content, imageUrl) {
        return this.request("POST", "/api/posts", { content, image_url: imageUrl });
    },

    async likePost(postId) {
        return this.request("POST", "/api/posts/" + postId + "/like");
    },

    async addComment(postId, text) {
        return this.request("POST", "/api/posts/" + postId + "/comments", { text });
    },

    // Friends
    async getFriends() {
        return this.request("GET", "/api/friends");
    },

    async sendFriendRequest(userId) {
        return this.request("POST", "/api/friends/request", { user_id: userId });
    },

    async acceptFriendRequest(requestId) {
        return this.request("POST", "/api/friends/request/" + requestId + "/accept");
    },

    // Messages
    async getConversations() {
        return this.request("GET", "/api/messages/conversations");
    },

    async getThread(userId) {
        return this.request("GET", "/api/messages/" + userId);
    },

    async sendMessage(toUserId, text) {
        return this.request("POST", "/api/messages", { to: toUserId, text });
    },

    // Search
    async search(query, type) {
        return this.request("GET", "/api/search?q=" + encodeURIComponent(query) + "&type=" + (type || "all"));
    }
};
""")
    return "Add frontend API service layer with auth, posts, friends, and messaging"


# ── STEP 34: Error handling middleware ─────────────────────────────────────
@step
def step_34():
    write_file("backend/middleware.py", """\
\"\"\"FriendZone - Middleware and Error Handlers\"\"\"
from flask import jsonify
from functools import wraps
import logging
import time

logger = logging.getLogger("friendzone")


def setup_error_handlers(app):
    \"\"\"Register error handlers for the Flask app.\"\"\"

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad request", "message": str(error)}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({"error": "Forbidden", "message": "You do not have permission"}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found", "message": "Resource not found"}), 404

    @app.errorhandler(429)
    def rate_limited(error):
        return jsonify({"error": "Rate limited", "message": "Too many requests, please slow down"}), 429

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({"error": "Internal server error", "message": "Something went wrong"}), 500


def request_logger(app):
    \"\"\"Log all incoming requests.\"\"\"
    @app.before_request
    def log_request():
        from flask import request, g
        g.start_time = time.time()
        logger.info(f"{request.method} {request.path}")

    @app.after_request
    def log_response(response):
        from flask import request, g
        duration = time.time() - getattr(g, "start_time", time.time())
        logger.info(f"{request.method} {request.path} -> {response.status_code} ({duration:.3f}s)")
        return response


def validate_json(*required_fields):
    \"\"\"Decorator to validate required JSON fields in request body.\"\"\"
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            from flask import request
            data = request.get_json(silent=True)
            if not data:
                return jsonify({"error": "Request body must be JSON"}), 400
            missing = [field for field in required_fields if field not in data]
            if missing:
                return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400
            return f(*args, **kwargs)
        return wrapper
    return decorator


class RateLimiter:
    \"\"\"Simple in-memory rate limiter.\"\"\"
    def __init__(self, max_requests=100, window_seconds=60):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests = {}

    def is_allowed(self, key):
        now = time.time()
        if key not in self.requests:
            self.requests[key] = []

        # Clean old entries
        self.requests[key] = [t for t in self.requests[key] if now - t < self.window]

        if len(self.requests[key]) >= self.max_requests:
            return False

        self.requests[key].append(now)
        return True
""")
    return "Add backend error handling middleware with rate limiter and logging"


# ── STEP 35: Backend config and CORS ──────────────────────────────────────
@step
def step_35():
    write_file("backend/config.py", """\
\"\"\"FriendZone - Application Configuration\"\"\"
import os


class Config:
    \"\"\"Base configuration.\"\"\"
    SECRET_KEY = os.environ.get("SECRET_KEY", "friendzone-dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///friendzone.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]


class DevelopmentConfig(Config):
    \"\"\"Development configuration.\"\"\"
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    \"\"\"Production configuration.\"\"\"
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    \"\"\"Testing configuration.\"\"\"
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config():
    env = os.environ.get("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)
""")
    return "Add backend configuration classes for dev, prod, and testing"


# ── STEP 36: Password validation and utils ────────────────────────────────
@step
def step_36():
    write_file("js/validation.js", """\
// FriendZone - Form Validation Utilities
const Validation = {
    email(value) {
        const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$/;
        if (!value) return "Email is required";
        if (!re.test(value)) return "Please enter a valid email address";
        return null;
    },

    password(value) {
        if (!value) return "Password is required";
        if (value.length < 8) return "Password must be at least 8 characters";
        if (!/[A-Z]/.test(value)) return "Password must contain at least one uppercase letter";
        if (!/[a-z]/.test(value)) return "Password must contain at least one lowercase letter";
        if (!/[0-9]/.test(value)) return "Password must contain at least one number";
        return null;
    },

    name(value) {
        if (!value || !value.trim()) return "Name is required";
        if (value.trim().length < 2) return "Name must be at least 2 characters";
        if (value.trim().length > 50) return "Name must be less than 50 characters";
        return null;
    },

    postContent(value) {
        if (!value || !value.trim()) return "Post content is required";
        if (value.length > 5000) return "Post must be less than 5000 characters";
        return null;
    },

    bio(value) {
        if (value && value.length > 300) return "Bio must be less than 300 characters";
        return null;
    },

    showError(inputId, message) {
        const input = document.getElementById(inputId);
        if (!input) return;
        let errorEl = input.parentElement.querySelector(".field-error");
        if (!errorEl) {
            errorEl = document.createElement("span");
            errorEl.className = "field-error";
            input.parentElement.appendChild(errorEl);
        }
        errorEl.textContent = message;
        input.classList.add("input-error");
    },

    clearError(inputId) {
        const input = document.getElementById(inputId);
        if (!input) return;
        const errorEl = input.parentElement.querySelector(".field-error");
        if (errorEl) errorEl.remove();
        input.classList.remove("input-error");
    },

    clearAllErrors() {
        document.querySelectorAll(".field-error").forEach(el => el.remove());
        document.querySelectorAll(".input-error").forEach(el => el.classList.remove("input-error"));
    },

    validateForm(rules) {
        let isValid = true;
        this.clearAllErrors();
        Object.entries(rules).forEach(function(entry) {
            const inputId = entry[0];
            const validator = entry[1];
            const input = document.getElementById(inputId);
            if (input) {
                const error = validator(input.value);
                if (error) { Validation.showError(inputId, error); isValid = false; }
            }
        });
        return isValid;
    }
};
""")
    append_file("css/style.css", """
/* Form Validation */
.field-error { display: block; color: #e74c3c; font-size: 12px; margin-top: -8px; margin-bottom: 8px; }
.input-error { border-color: #e74c3c !important; }
.input-error:focus { box-shadow: 0 0 0 2px rgba(231,76,60,0.2); }
""")
    return "Add form validation utilities with error display"


# ── STEP 37: Accessibility improvements ───────────────────────────────────
@step
def step_37():
    write_file("js/accessibility.js", """\
// FriendZone - Accessibility Module
const A11y = {
    init() {
        this.setupKeyboardNav();
        this.setupSkipLink();
        this.setupAriaLive();
        this.setupFocusTrap();
    },

    setupKeyboardNav() {
        document.addEventListener("keydown", function(e) {
            // Escape closes dialogs
            if (e.key === "Escape") {
                const dialog = document.querySelector(".dialog-overlay");
                if (dialog) dialog.remove();
                const storyViewer = document.querySelector(".story-viewer");
                if (storyViewer) storyViewer.remove();
            }

            // Tab trapping in modals
            if (e.key === "Tab") {
                const modal = document.querySelector(".dialog-overlay, .story-viewer");
                if (modal) {
                    const focusable = modal.querySelectorAll("button, input, textarea, select, a[href]");
                    if (focusable.length === 0) return;
                    const first = focusable[0];
                    const last = focusable[focusable.length - 1];
                    if (e.shiftKey && document.activeElement === first) {
                        e.preventDefault();
                        last.focus();
                    } else if (!e.shiftKey && document.activeElement === last) {
                        e.preventDefault();
                        first.focus();
                    }
                }
            }
        });
    },

    setupSkipLink() {
        const skip = document.createElement("a");
        skip.href = "#main-content";
        skip.className = "skip-link";
        skip.textContent = "Skip to main content";
        skip.addEventListener("click", function(e) {
            e.preventDefault();
            var main = document.getElementById("main-content");
            if (main) { main.setAttribute("tabindex", "-1"); main.focus(); }
        });
        document.body.insertBefore(skip, document.body.firstChild);
    },

    setupAriaLive() {
        const live = document.createElement("div");
        live.id = "aria-live-region";
        live.setAttribute("aria-live", "polite");
        live.setAttribute("aria-atomic", "true");
        live.className = "sr-only";
        document.body.appendChild(live);
    },

    announce(message) {
        const region = document.getElementById("aria-live-region");
        if (region) {
            region.textContent = "";
            setTimeout(function() { region.textContent = message; }, 100);
        }
    },

    setupFocusTrap() {
        this._focusTrapElement = null;
    },

    trapFocus(element) {
        this._focusTrapElement = element;
        const focusable = element.querySelectorAll("button, input, textarea, select, a[href]");
        if (focusable.length > 0) focusable[0].focus();
    },

    releaseFocus() {
        this._focusTrapElement = null;
    }
};
""")
    append_file("css/style.css", """
/* Accessibility */
.skip-link {
    position: absolute; top: -40px; left: 0;
    background: #4a90d9; color: white; padding: 8px 16px;
    z-index: 10000; font-size: 14px; text-decoration: none;
    transition: top 0.2s;
}
.skip-link:focus { top: 0; }
.sr-only {
    position: absolute; width: 1px; height: 1px;
    padding: 0; margin: -1px; overflow: hidden;
    clip: rect(0,0,0,0); border: 0;
}
*:focus-visible { outline: 2px solid #4a90d9; outline-offset: 2px; }
""")
    return "Add accessibility features: keyboard nav, skip links, ARIA live regions"


# ── STEP 38: PWA manifest and service worker ──────────────────────────────
@step
def step_38():
    write_file("manifest.json", """\
{
  "name": "FriendZone",
  "short_name": "FriendZone",
  "description": "Connect, share, and stay in touch with your friends.",
  "start_url": "/index.html",
  "display": "standalone",
  "background_color": "#f0f2f5",
  "theme_color": "#4a90d9",
  "orientation": "portrait-primary",
  "categories": ["social"],
  "icons": [
    {
      "src": "icons/icon-72.png",
      "sizes": "72x72",
      "type": "image/png"
    },
    {
      "src": "icons/icon-96.png",
      "sizes": "96x96",
      "type": "image/png"
    },
    {
      "src": "icons/icon-128.png",
      "sizes": "128x128",
      "type": "image/png"
    },
    {
      "src": "icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
""")
    write_file("sw.js", """\
// FriendZone Service Worker
const CACHE_NAME = "friendzone-v1";
const ASSETS = [
    "/index.html",
    "/css/style.css",
    "/js/app.js",
    "/js/auth.js",
    "/js/feed.js",
    "/js/profile.js",
    "/js/friends.js",
    "/js/comments.js",
    "/js/messaging.js",
    "/js/notifications.js",
    "/js/search.js",
    "/js/ui.js",
    "/js/status.js",
    "/js/stories.js",
    "/js/hashtags.js",
    "/js/bookmarks.js",
    "/js/moderation.js",
    "/js/activity.js",
    "/js/groups.js",
    "/js/events.js",
    "/js/polls.js",
    "/js/share.js",
    "/js/admin.js",
    "/js/api.js",
    "/js/validation.js",
    "/js/accessibility.js",
    "/manifest.json"
];

// Install - cache all static assets
self.addEventListener("install", function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            console.log("Caching app assets");
            return cache.addAll(ASSETS);
        })
    );
    self.skipWaiting();
});

// Activate - clean up old caches
self.addEventListener("activate", function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.filter(function(name) { return name !== CACHE_NAME; })
                    .map(function(name) { return caches.delete(name); })
            );
        })
    );
    self.clients.claim();
});

// Fetch - serve from cache, fallback to network
self.addEventListener("fetch", function(event) {
    // Skip non-GET requests
    if (event.request.method !== "GET") return;

    // Skip API requests
    if (event.request.url.includes("/api/")) return;

    event.respondWith(
        caches.match(event.request).then(function(cachedResponse) {
            if (cachedResponse) return cachedResponse;

            return fetch(event.request).then(function(response) {
                // Cache new resources
                if (response.status === 200) {
                    var responseClone = response.clone();
                    caches.open(CACHE_NAME).then(function(cache) {
                        cache.put(event.request, responseClone);
                    });
                }
                return response;
            }).catch(function() {
                // Offline fallback
                if (event.request.headers.get("accept").includes("text/html")) {
                    return caches.match("/index.html");
                }
            });
        })
    );
});
""")
    return "Add PWA manifest and service worker for offline support"


# ── STEP 39: Backend tests ────────────────────────────────────────────────
@step
def step_39():
    write_file("backend/tests/__init__.py", "")
    write_file("backend/tests/test_auth.py", """\
\"\"\"FriendZone - Authentication Tests\"\"\"
import unittest
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app
from models import db, User


class TestAuth(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_signup_success(self):
        response = self.client.post("/api/auth/signup",
            data=json.dumps({"name": "Test User", "email": "test@example.com", "password": "Password123"}),
            content_type="application/json")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", data)
        self.assertEqual(data["user"]["name"], "Test User")

    def test_signup_duplicate_email(self):
        self.client.post("/api/auth/signup",
            data=json.dumps({"name": "User 1", "email": "test@example.com", "password": "Password123"}),
            content_type="application/json")
        response = self.client.post("/api/auth/signup",
            data=json.dumps({"name": "User 2", "email": "test@example.com", "password": "Password456"}),
            content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_login_success(self):
        self.client.post("/api/auth/signup",
            data=json.dumps({"name": "Test User", "email": "test@example.com", "password": "Password123"}),
            content_type="application/json")
        response = self.client.post("/api/auth/login",
            data=json.dumps({"email": "test@example.com", "password": "Password123"}),
            content_type="application/json")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", data)

    def test_login_wrong_password(self):
        self.client.post("/api/auth/signup",
            data=json.dumps({"name": "Test User", "email": "test@example.com", "password": "Password123"}),
            content_type="application/json")
        response = self.client.post("/api/auth/login",
            data=json.dumps({"email": "test@example.com", "password": "WrongPassword"}),
            content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_login_nonexistent_user(self):
        response = self.client.post("/api/auth/login",
            data=json.dumps({"email": "nobody@example.com", "password": "Password123"}),
            content_type="application/json")
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
""")
    write_file("backend/tests/test_posts.py", """\
\"\"\"FriendZone - Post Tests\"\"\"
import unittest
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app
from models import db


class TestPosts(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = app.test_client()
        with app.app_context():
            db.create_all()
        # Create test user and get token
        response = self.client.post("/api/auth/signup",
            data=json.dumps({"name": "Test User", "email": "test@example.com", "password": "Password123"}),
            content_type="application/json")
        self.token = json.loads(response.data)["token"]
        self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_post(self):
        response = self.client.post("/api/posts",
            data=json.dumps({"content": "Hello world!"}),
            headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["content"], "Hello world!")

    def test_get_posts(self):
        self.client.post("/api/posts",
            data=json.dumps({"content": "Post 1"}),
            headers=self.headers)
        self.client.post("/api/posts",
            data=json.dumps({"content": "Post 2"}),
            headers=self.headers)
        response = self.client.get("/api/posts", headers=self.headers)
        data = json.loads(response.data)
        self.assertEqual(len(data["posts"]), 2)

    def test_like_post(self):
        response = self.client.post("/api/posts",
            data=json.dumps({"content": "Likeable post"}),
            headers=self.headers)
        post_id = json.loads(response.data)["id"]
        response = self.client.post(f"/api/posts/{post_id}/like", headers=self.headers)
        data = json.loads(response.data)
        self.assertTrue(data["liked"])

    def test_unlike_post(self):
        response = self.client.post("/api/posts",
            data=json.dumps({"content": "Unlikeable post"}),
            headers=self.headers)
        post_id = json.loads(response.data)["id"]
        self.client.post(f"/api/posts/{post_id}/like", headers=self.headers)
        response = self.client.post(f"/api/posts/{post_id}/like", headers=self.headers)
        data = json.loads(response.data)
        self.assertFalse(data["liked"])

    def test_unauthorized_access(self):
        response = self.client.get("/api/posts")
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
""")
    return "Add backend unit tests for authentication and post endpoints"


# ── STEP 40: Infinite scroll & lazy loading ───────────────────────────────
@step
def step_40():
    write_file("js/infinite_scroll.js", """\
// FriendZone - Infinite Scroll & Lazy Loading
const InfiniteScroll = {
    page: 1,
    loading: false,
    hasMore: true,
    container: null,
    loadFn: null,

    init(containerId, loadFunction) {
        this.page = 1;
        this.loading = false;
        this.hasMore = true;
        this.container = document.getElementById(containerId);
        this.loadFn = loadFunction;

        this._onScroll = this._handleScroll.bind(this);
        window.addEventListener("scroll", this._onScroll);
    },

    destroy() {
        window.removeEventListener("scroll", this._onScroll);
    },

    _handleScroll() {
        if (this.loading || !this.hasMore) return;

        var scrollHeight = document.documentElement.scrollHeight;
        var scrollTop = window.scrollY || document.documentElement.scrollTop;
        var clientHeight = document.documentElement.clientHeight;

        if (scrollHeight - scrollTop - clientHeight < 200) {
            this.loadMore();
        }
    },

    loadMore() {
        if (this.loading || !this.hasMore) return;
        this.loading = true;
        this._showLoader();

        var self = this;
        this.page++;
        this.loadFn(this.page, function(items, hasMore) {
            self.loading = false;
            self.hasMore = hasMore;
            self._hideLoader();
            if (items && self.container) {
                self.container.insertAdjacentHTML("beforeend", items);
                LazyImages.observe();
            }
        });
    },

    _showLoader() {
        if (!this.container) return;
        var loader = document.createElement("div");
        loader.id = "scroll-loader";
        loader.className = "scroll-loader";
        loader.innerHTML = '<div class="spinner" style="width:24px;height:24px;border-width:3px;"></div>';
        this.container.parentElement.appendChild(loader);
    },

    _hideLoader() {
        var loader = document.getElementById("scroll-loader");
        if (loader) loader.remove();
    },

    reset() {
        this.page = 1;
        this.hasMore = true;
        this.loading = false;
    }
};

// Lazy image loading
var LazyImages = {
    observer: null,

    init() {
        if ("IntersectionObserver" in window) {
            this.observer = new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        var img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.removeAttribute("data-src");
                            LazyImages.observer.unobserve(img);
                        }
                    }
                });
            }, { rootMargin: "100px" });
        }
    },

    observe() {
        if (!this.observer) return;
        document.querySelectorAll("img[data-src]").forEach(function(img) {
            LazyImages.observer.observe(img);
        });
    }
};
""")
    append_file("css/style.css", """
/* Infinite Scroll */
.scroll-loader { text-align: center; padding: 20px; }
img[data-src] { opacity: 0; transition: opacity 0.3s; }
img[data-src].loaded, img:not([data-src]) { opacity: 1; }
""")
    return "Add infinite scroll pagination and lazy image loading"


# ── STEP 41: Date/time utilities ──────────────────────────────────────────
@step
def step_41():
    write_file("js/datetime.js", """\
// FriendZone - Date/Time Utilities
const DateTime = {
    formatRelative(dateString) {
        var date = new Date(dateString);
        var now = new Date();
        var diff = Math.floor((now - date) / 1000);

        if (diff < 10) return "just now";
        if (diff < 60) return diff + " seconds ago";
        if (diff < 3600) return Math.floor(diff / 60) + " minutes ago";
        if (diff < 86400) return Math.floor(diff / 3600) + " hours ago";
        if (diff < 604800) return Math.floor(diff / 86400) + " days ago";
        if (diff < 2592000) return Math.floor(diff / 604800) + " weeks ago";
        if (diff < 31536000) return Math.floor(diff / 2592000) + " months ago";
        return Math.floor(diff / 31536000) + " years ago";
    },

    formatFull(dateString) {
        var date = new Date(dateString);
        var months = ["January","February","March","April","May","June",
                      "July","August","September","October","November","December"];
        return months[date.getMonth()] + " " + date.getDate() + ", " + date.getFullYear() +
            " at " + this.formatTime(date);
    },

    formatShort(dateString) {
        var date = new Date(dateString);
        var now = new Date();
        if (date.toDateString() === now.toDateString()) {
            return this.formatTime(date);
        }
        var yesterday = new Date(now);
        yesterday.setDate(yesterday.getDate() - 1);
        if (date.toDateString() === yesterday.toDateString()) {
            return "Yesterday";
        }
        return (date.getMonth() + 1) + "/" + date.getDate() + "/" + date.getFullYear();
    },

    formatTime(date) {
        var hours = date.getHours();
        var minutes = date.getMinutes();
        var ampm = hours >= 12 ? "PM" : "AM";
        hours = hours % 12;
        hours = hours ? hours : 12;
        return hours + ":" + (minutes < 10 ? "0" : "") + minutes + " " + ampm;
    },

    formatDuration(seconds) {
        if (seconds < 60) return seconds + "s";
        if (seconds < 3600) return Math.floor(seconds / 60) + "m";
        if (seconds < 86400) return Math.floor(seconds / 3600) + "h " + Math.floor((seconds % 3600) / 60) + "m";
        return Math.floor(seconds / 86400) + "d " + Math.floor((seconds % 86400) / 3600) + "h";
    },

    getGreeting() {
        var hour = new Date().getHours();
        if (hour < 12) return "Good morning";
        if (hour < 17) return "Good afternoon";
        if (hour < 21) return "Good evening";
        return "Good night";
    },

    isToday(dateString) {
        return new Date(dateString).toDateString() === new Date().toDateString();
    },

    daysUntil(dateString) {
        var target = new Date(dateString);
        var now = new Date();
        var diff = target.getTime() - now.getTime();
        return Math.ceil(diff / 86400000);
    }
};
""")
    return "Add comprehensive date/time utility functions"


# ── STEP 42: Local storage manager ────────────────────────────────────────
@step
def step_42():
    write_file("js/storage.js", """\
// FriendZone - Storage Manager
const StorageManager = {
    prefix: "fz_",

    set(key, value) {
        try {
            localStorage.setItem(this.prefix + key, JSON.stringify(value));
            return true;
        } catch (e) {
            if (e.name === "QuotaExceededError") {
                console.warn("Storage quota exceeded. Cleaning up...");
                this.cleanup();
                try {
                    localStorage.setItem(this.prefix + key, JSON.stringify(value));
                    return true;
                } catch (e2) {
                    console.error("Storage still full after cleanup");
                    return false;
                }
            }
            return false;
        }
    },

    get(key, defaultValue) {
        try {
            var item = localStorage.getItem(this.prefix + key);
            return item ? JSON.parse(item) : (defaultValue !== undefined ? defaultValue : null);
        } catch (e) {
            return defaultValue !== undefined ? defaultValue : null;
        }
    },

    remove(key) {
        localStorage.removeItem(this.prefix + key);
    },

    clear() {
        var keys = Object.keys(localStorage);
        var self = this;
        keys.forEach(function(key) {
            if (key.startsWith(self.prefix)) {
                localStorage.removeItem(key);
            }
        });
    },

    getSize() {
        var total = 0;
        var self = this;
        Object.keys(localStorage).forEach(function(key) {
            if (key.startsWith(self.prefix)) {
                total += localStorage.getItem(key).length;
            }
        });
        return { bytes: total * 2, kb: Math.round(total * 2 / 1024), mb: Math.round(total * 2 / 1048576 * 100) / 100 };
    },

    cleanup() {
        // Remove expired stories
        var stories = this.get("stories", []);
        var now = new Date();
        stories = stories.filter(function(s) { return new Date(s.expiresAt) > now; });
        this.set("stories", stories);

        // Trim old activity logs
        var activity = this.get("activity", []);
        if (activity.length > 200) {
            activity = activity.slice(0, 200);
            this.set("activity", activity);
        }

        // Trim old notifications
        var notifs = this.get("notifications", []);
        if (notifs.length > 100) {
            notifs = notifs.slice(0, 100);
            this.set("notifications", notifs);
        }
    },

    export() {
        var data = {};
        var self = this;
        Object.keys(localStorage).forEach(function(key) {
            if (key.startsWith(self.prefix)) {
                data[key] = localStorage.getItem(key);
            }
        });
        return JSON.stringify(data);
    },

    import(jsonString) {
        try {
            var data = JSON.parse(jsonString);
            Object.entries(data).forEach(function(entry) {
                localStorage.setItem(entry[0], entry[1]);
            });
            return true;
        } catch (e) {
            return false;
        }
    }
};
""")
    return "Add local storage manager with cleanup, export, and import"


# ── Maintenance cycles (rotate after all feature steps) ───────────────────
def _maint_add_analytics(version):
    write_file("js/analytics.js", """\
// FriendZone - Analytics Module v""" + str(version) + """
const Analytics = {
    events: [],

    track(eventName, data) {
        this.events.push({
            event: eventName,
            data: data || {},
            timestamp: new Date().toISOString(),
            sessionId: this.getSessionId()
        });
        this.flush();
    },

    getSessionId() {
        var sid = sessionStorage.getItem("fz_session_id");
        if (!sid) {
            sid = "sess_" + Date.now() + "_" + Math.random().toString(36).substr(2, 9);
            sessionStorage.setItem("fz_session_id", sid);
        }
        return sid;
    },

    flush() {
        var stored = JSON.parse(localStorage.getItem("fz_analytics") || "[]");
        stored = stored.concat(this.events);
        if (stored.length > 1000) stored = stored.slice(-1000);
        localStorage.setItem("fz_analytics", JSON.stringify(stored));
        this.events = [];
    },

    getPageViews(days) {
        days = days || 7;
        var cutoff = new Date(Date.now() - days * 86400000);
        var all = JSON.parse(localStorage.getItem("fz_analytics") || "[]");
        return all.filter(function(e) {
            return e.event === "page_view" && new Date(e.timestamp) > cutoff;
        }).length;
    },

    getTopEvents(limit) {
        limit = limit || 10;
        var all = JSON.parse(localStorage.getItem("fz_analytics") || "[]");
        var counts = {};
        all.forEach(function(e) { counts[e.event] = (counts[e.event] || 0) + 1; });
        return Object.entries(counts)
            .sort(function(a, b) { return b[1] - a[1]; })
            .slice(0, limit)
            .map(function(entry) { return { event: entry[0], count: entry[1] }; });
    },

    getDailyActive(days) {
        days = days || 30;
        var all = JSON.parse(localStorage.getItem("fz_analytics") || "[]");
        var daily = {};
        all.forEach(function(e) {
            var day = e.timestamp.split("T")[0];
            if (!daily[day]) daily[day] = new Set();
            daily[day].add(e.sessionId);
        });
        var result = [];
        Object.entries(daily).forEach(function(entry) {
            result.push({ date: entry[0], users: entry[1].size });
        });
        return result.sort(function(a, b) { return a.date.localeCompare(b.date); }).slice(-days);
    }
};
""")
    return "Add analytics tracking module v" + str(version)


def _maint_add_perf_monitor(version):
    write_file("js/performance.js", """\
// FriendZone - Performance Monitor v""" + str(version) + """
const PerfMonitor = {
    marks: {},

    start(label) {
        this.marks[label] = performance.now();
    },

    end(label) {
        if (!this.marks[label]) return 0;
        var duration = performance.now() - this.marks[label];
        delete this.marks[label];
        this.log(label, duration);
        return duration;
    },

    log(label, duration) {
        var logs = JSON.parse(localStorage.getItem("fz_perf_logs") || "[]");
        logs.push({ label: label, duration: Math.round(duration * 100) / 100, timestamp: new Date().toISOString() });
        if (logs.length > 500) logs = logs.slice(-500);
        localStorage.setItem("fz_perf_logs", JSON.stringify(logs));
    },

    getAverages() {
        var logs = JSON.parse(localStorage.getItem("fz_perf_logs") || "[]");
        var grouped = {};
        logs.forEach(function(l) {
            if (!grouped[l.label]) grouped[l.label] = [];
            grouped[l.label].push(l.duration);
        });
        var result = {};
        Object.entries(grouped).forEach(function(entry) {
            var vals = entry[1];
            result[entry[0]] = {
                avg: Math.round(vals.reduce(function(a, b) { return a + b; }, 0) / vals.length * 100) / 100,
                min: Math.min.apply(null, vals),
                max: Math.max.apply(null, vals),
                count: vals.length
            };
        });
        return result;
    },

    measureRender(fn, label) {
        var self = this;
        self.start(label);
        var result = fn();
        self.end(label);
        return result;
    },

    getMemoryUsage() {
        if (performance.memory) {
            return {
                used: Math.round(performance.memory.usedJSHeapSize / 1048576) + " MB",
                total: Math.round(performance.memory.totalJSHeapSize / 1048576) + " MB",
                limit: Math.round(performance.memory.jsHeapSizeLimit / 1048576) + " MB"
            };
        }
        return null;
    }
};
""")
    return "Add performance monitoring module v" + str(version)


def _maint_update_css_animations(version):
    append_file("css/style.css", """
/* Animation utilities v""" + str(version) + """ */
.fade-in { animation: fadeIn 0.3s ease forwards; }
.fade-out { animation: fadeOut 0.3s ease forwards; }
.slide-up { animation: slideUp 0.3s ease forwards; }
.slide-down { animation: slideDown 0.3s ease forwards; }
.scale-in { animation: scaleIn 0.2s ease forwards; }
.bounce { animation: bounce 0.5s ease; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes fadeOut { from { opacity: 1; } to { opacity: 0; } }
@keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
@keyframes slideDown { from { transform: translateY(-20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
@keyframes scaleIn { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
@keyframes bounce { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }

.skeleton { background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%); background-size: 200% 100%; animation: skeleton 1.5s infinite; border-radius: 4px; }
@keyframes skeleton { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
[data-theme="dark"] .skeleton { background: linear-gradient(90deg, #3a3b3c 25%, #2d2e30 50%, #3a3b3c 75%); background-size: 200% 100%; }
""")
    return "Add CSS animation utilities and skeleton loading v" + str(version)


def _maint_add_keyboard_shortcuts(version):
    write_file("js/shortcuts.js", """\
// FriendZone - Keyboard Shortcuts v""" + str(version) + """
const Shortcuts = {
    bindings: {},
    enabled: true,

    init() {
        var self = this;
        document.addEventListener("keydown", function(e) {
            if (!self.enabled) return;
            if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;

            var key = "";
            if (e.ctrlKey || e.metaKey) key += "ctrl+";
            if (e.shiftKey) key += "shift+";
            if (e.altKey) key += "alt+";
            key += e.key.toLowerCase();

            if (self.bindings[key]) {
                e.preventDefault();
                self.bindings[key]();
            }
        });

        // Default shortcuts
        this.bind("ctrl+k", function() {
            document.getElementById("nav-search") && document.getElementById("nav-search").click();
        });
        this.bind("ctrl+n", function() {
            var postInput = document.getElementById("post-input");
            if (postInput) postInput.focus();
        });
        this.bind("h", function() {
            document.getElementById("nav-home") && document.getElementById("nav-home").click();
        });
        this.bind("p", function() {
            document.getElementById("nav-profile") && document.getElementById("nav-profile").click();
        });
        this.bind("m", function() {
            document.getElementById("nav-messages") && document.getElementById("nav-messages").click();
        });
        this.bind("n", function() {
            document.getElementById("nav-notifs") && document.getElementById("nav-notifs").click();
        });
        this.bind("shift+/", function() { self.showHelp(); });
    },

    bind(key, handler) {
        this.bindings[key.toLowerCase()] = handler;
    },

    unbind(key) {
        delete this.bindings[key.toLowerCase()];
    },

    showHelp() {
        var html = '<div class="dialog-overlay" id="shortcuts-help"><div class="dialog">' +
            '<h3>Keyboard Shortcuts</h3><div class="shortcuts-list">' +
            '<div class="shortcut-item"><kbd>H</kbd> Home</div>' +
            '<div class="shortcut-item"><kbd>P</kbd> Profile</div>' +
            '<div class="shortcut-item"><kbd>M</kbd> Messages</div>' +
            '<div class="shortcut-item"><kbd>N</kbd> Notifications</div>' +
            '<div class="shortcut-item"><kbd>Ctrl+K</kbd> Search</div>' +
            '<div class="shortcut-item"><kbd>Ctrl+N</kbd> New post</div>' +
            '<div class="shortcut-item"><kbd>?</kbd> This help</div>' +
            '<div class="shortcut-item"><kbd>Esc</kbd> Close dialogs</div>' +
            '</div><button class="btn btn-primary" onclick="this.closest(\\'.dialog-overlay\\').remove()">Close</button></div></div>';
        document.body.insertAdjacentHTML("beforeend", html);
    }
};
""")
    append_file("css/style.css", """
/* Keyboard shortcuts help */
.shortcuts-list { text-align: left; margin: 16px 0; }
.shortcut-item { padding: 6px 0; display: flex; align-items: center; gap: 12px; }
kbd { background: #f0f2f5; border: 1px solid #ddd; border-radius: 4px; padding: 2px 8px; font-family: monospace; font-size: 12px; min-width: 50px; text-align: center; }
[data-theme="dark"] kbd { background: #3a3b3c; border-color: #555; }
""")
    return "Add keyboard shortcuts with help overlay v" + str(version)


def _maint_add_export_data(version):
    write_file("js/data_export.js", """\
// FriendZone - Data Export Module v""" + str(version) + """
const DataExport = {
    exportUserData(userId) {
        var users = JSON.parse(localStorage.getItem("fz_users") || "[]");
        var user = users.find(function(u) { return u.id === userId; });
        var posts = JSON.parse(localStorage.getItem("fz_posts") || "[]")
            .filter(function(p) { return p.userId === userId; });
        var messages = JSON.parse(localStorage.getItem("fz_messages") || "[]")
            .filter(function(m) { return m.from === userId || m.to === userId; });

        var data = {
            exportedAt: new Date().toISOString(),
            profile: user,
            posts: posts,
            messages: messages,
            postCount: posts.length,
            messageCount: messages.length
        };

        this.downloadJson(data, "friendzone-data-" + userId + ".json");
    },

    exportPosts(userId) {
        var posts = JSON.parse(localStorage.getItem("fz_posts") || "[]")
            .filter(function(p) { return p.userId === userId; });
        var csv = "id,content,likes,comments,created_at\\n";
        posts.forEach(function(p) {
            var content = p.content.replace(/"/g, '""');
            csv += p.id + ',"' + content + '",' + p.likes.length + ',' + p.comments.length + ',' + p.createdAt + "\\n";
        });
        this.downloadCsv(csv, "friendzone-posts.csv");
    },

    downloadJson(data, filename) {
        var blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
        this._download(blob, filename);
    },

    downloadCsv(csvContent, filename) {
        var blob = new Blob([csvContent], { type: "text/csv" });
        this._download(blob, filename);
    },

    _download(blob, filename) {
        var url = URL.createObjectURL(blob);
        var a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
};
""")
    return "Add data export module with JSON and CSV download v" + str(version)


def _maint_refactor_feed_rendering(version):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    append_file("js/feed.js", """
// Feed rendering optimizations - v""" + str(version) + """ (""" + ts + """)
Feed.renderPostBatch = function(posts, userId, batchSize) {
    batchSize = batchSize || 10;
    var batches = [];
    for (var i = 0; i < posts.length; i += batchSize) {
        batches.push(posts.slice(i, i + batchSize));
    }
    return batches;
};

Feed.debounce = function(fn, delay) {
    var timer = null;
    return function() {
        var args = arguments;
        var context = this;
        clearTimeout(timer);
        timer = setTimeout(function() { fn.apply(context, args); }, delay);
    };
};

Feed.throttle = function(fn, limit) {
    var waiting = false;
    return function() {
        if (!waiting) {
            fn.apply(this, arguments);
            waiting = true;
            setTimeout(function() { waiting = false; }, limit);
        }
    };
};

Feed.virtualScroll = {
    itemHeight: 150,
    buffer: 5,
    getVisibleRange: function(scrollTop, containerHeight, totalItems) {
        var start = Math.max(0, Math.floor(scrollTop / this.itemHeight) - this.buffer);
        var end = Math.min(totalItems, Math.ceil((scrollTop + containerHeight) / this.itemHeight) + this.buffer);
        return { start: start, end: end };
    }
};
""")
    return "Optimize feed rendering with batching and virtual scroll v" + str(version)


def _maint_add_error_boundary(version):
    write_file("js/error_boundary.js", """\
// FriendZone - Error Boundary v""" + str(version) + """
const ErrorBoundary = {
    errors: [],

    init() {
        var self = this;
        window.onerror = function(msg, source, line, col, error) {
            self.capture({ message: msg, source: source, line: line, col: col, stack: error ? error.stack : null });
            return false;
        };

        window.addEventListener("unhandledrejection", function(event) {
            self.capture({ message: "Unhandled promise rejection: " + event.reason, type: "promise" });
        });
    },

    capture(error) {
        error.timestamp = new Date().toISOString();
        error.url = window.location.href;
        error.userAgent = navigator.userAgent;
        this.errors.push(error);

        // Keep last 50 errors
        if (this.errors.length > 50) this.errors = this.errors.slice(-50);
        localStorage.setItem("fz_error_log", JSON.stringify(this.errors));

        console.error("[FriendZone Error]", error.message);
    },

    getErrors() {
        return JSON.parse(localStorage.getItem("fz_error_log") || "[]");
    },

    clearErrors() {
        this.errors = [];
        localStorage.removeItem("fz_error_log");
    },

    renderErrorPage(error) {
        return '<div class="error-page">' +
            '<h2>Something went wrong</h2>' +
            '<p>We encountered an unexpected error. Please try refreshing the page.</p>' +
            '<details><summary>Error details</summary><pre>' + (error.message || "Unknown error") + '</pre></details>' +
            '<button class="btn btn-primary" onclick="location.reload()">Refresh Page</button></div>';
    },

    safeRender(renderFn, fallbackHtml) {
        try {
            return renderFn();
        } catch (e) {
            this.capture({ message: e.message, stack: e.stack, type: "render" });
            return fallbackHtml || '<div class="error-page"><p>Failed to load this section.</p></div>';
        }
    }
};
""")
    append_file("css/style.css", """
/* Error page */
.error-page { text-align: center; padding: 60px 20px; max-width: 500px; margin: 0 auto; }
.error-page h2 { margin-bottom: 12px; color: #e74c3c; }
.error-page details { margin: 16px 0; text-align: left; }
.error-page pre { background: #f5f5f5; padding: 12px; border-radius: 6px; overflow-x: auto; font-size: 12px; }
[data-theme="dark"] .error-page pre { background: #2a2a3e; }
""")
    return "Add error boundary with global error capture v" + str(version)


def _maint_add_link_preview(version):
    write_file("js/link_preview.js", """\
// FriendZone - Link Preview v""" + str(version) + """
const LinkPreview = {
    urlRegex: /(https?:\\/\\/[^\\s<]+)/g,

    extractUrls(text) {
        var matches = text.match(this.urlRegex);
        return matches || [];
    },

    parseContent(text) {
        return text.replace(this.urlRegex, function(url) {
            return '<a href="' + url + '" class="post-link" target="_blank" rel="noopener">' + url + '</a>';
        });
    },

    createPreviewCard(url) {
        var domain = "";
        try { domain = new URL(url).hostname; } catch(e) { domain = url; }
        return '<div class="link-preview">' +
            '<div class="link-preview-body">' +
            '<span class="link-domain">' + domain + '</span>' +
            '<a href="' + url + '" target="_blank" rel="noopener" class="link-title">' + url + '</a>' +
            '</div></div>';
    },

    processPostContent(content) {
        var urls = this.extractUrls(content);
        var html = this.parseContent(content);
        if (urls.length > 0) {
            html += this.createPreviewCard(urls[0]);
        }
        return html;
    }
};
""")
    append_file("css/style.css", """
/* Link Preview */
.link-preview { border: 1px solid #e4e6eb; border-radius: 8px; overflow: hidden; margin-top: 8px; }
.link-preview-body { padding: 12px; }
.link-domain { font-size: 11px; color: #999; text-transform: uppercase; }
.link-title { display: block; color: #1c1e21; font-weight: 600; margin-top: 4px; text-decoration: none; }
.link-title:hover { text-decoration: underline; }
.post-link { color: #4a90d9; }
[data-theme="dark"] .link-preview { border-color: #3a3b3c; }
[data-theme="dark"] .link-title { color: #e4e6eb; }
""")
    return "Add link preview detection and rendering v" + str(version)


def _maint_update_readme(version):
    write_file("README.md", """\
# FriendZone v1.0.""" + str(version) + """

A full-featured social media app to connect with friends.

## Features
- User authentication (login/signup)
- News feed with posts, likes, and comments
- User profiles with bio and stats
- Friend system with requests
- Direct messaging with read receipts
- Notifications
- Search (users and posts)
- Stories with 24h expiry
- Hashtag system with trending topics
- Bookmarks / saved posts
- Content reporting and user blocking
- Activity log with timeline
- Groups and events
- Polls with voting
- Share / repost
- Admin dashboard
- Dark mode
- Image uploads and emoji picker
- Responsive design
- Keyboard shortcuts
- PWA with offline support
- Accessibility (ARIA, skip links, focus management)

## Tech Stack
- Frontend: Vanilla JS, CSS3
- Backend: Flask, SQLAlchemy, JWT
- Storage: LocalStorage (frontend), SQLite (backend)

## Getting Started
1. Open `index.html` in a browser for the frontend
2. Run `pip install -r backend/requirements.txt` for backend deps
3. Run `python backend/app.py` to start the API server

## Project Structure
```
FriendZone/
  css/         - Stylesheets
  js/          - Frontend modules
  backend/     - Flask API server
  icons/       - PWA icons
  sw.js        - Service worker
  manifest.json - PWA manifest
```
""")
    return "Update README with full feature list v" + str(version)


MAINTENANCE_CYCLES = [
    _maint_add_analytics,
    _maint_add_perf_monitor,
    _maint_update_css_animations,
    _maint_add_keyboard_shortcuts,
    _maint_add_export_data,
    _maint_refactor_feed_rendering,
    _maint_add_error_boundary,
    _maint_add_link_preview,
    _maint_update_readme,
]


# ── Read / write step tracker ──────────────────────────────────────────────
def read_step():
    if os.path.exists(STEP_FILE):
        with open(STEP_FILE) as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return 0
    return 0


def write_step(n):
    with open(STEP_FILE, "w") as f:
        f.write(str(n))


# ── GUI App ────────────────────────────────────────────────────────────────
class FriendZoneBuilder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FriendZone Auto-Builder")
        self.root.geometry("620x480")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        self.running = False
        self.thread = None
        self.stop_event = threading.Event()

        self._build_ui()

    # ── UI layout ──────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#4a90d9", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="FriendZone Auto-Builder",
            font=("Segoe UI", 18, "bold"), fg="white", bg="#4a90d9",
        ).pack(expand=True)

        # Body
        body = tk.Frame(self.root, bg="#1e1e2e", padx=20, pady=12)
        body.pack(fill="both", expand=True)

        # Status row
        status_frame = tk.Frame(body, bg="#1e1e2e")
        status_frame.pack(fill="x", pady=(0, 8))
        tk.Label(status_frame, text="Status:", fg="#aaa", bg="#1e1e2e",
                 font=("Segoe UI", 11)).pack(side="left")
        self.status_var = tk.StringVar(value="Stopped")
        self.status_label = tk.Label(
            status_frame, textvariable=self.status_var,
            fg="#e74c3c", bg="#1e1e2e", font=("Segoe UI", 11, "bold"),
        )
        self.status_label.pack(side="left", padx=(6, 0))

        # Step info
        step_frame = tk.Frame(body, bg="#1e1e2e")
        step_frame.pack(fill="x", pady=(0, 8))
        tk.Label(step_frame, text="Current step:", fg="#aaa", bg="#1e1e2e",
                 font=("Segoe UI", 11)).pack(side="left")
        self.step_var = tk.StringVar(value=f"{read_step()} / {len(STEPS)}+")
        tk.Label(step_frame, textvariable=self.step_var, fg="white",
                 bg="#1e1e2e", font=("Segoe UI", 11)).pack(side="left", padx=(6, 0))

        # Progress bar
        self.progress = ttk.Progressbar(body, length=560, mode="determinate",
                                        maximum=max(len(STEPS), 1))
        self.progress.pack(pady=(0, 8))
        self.progress["value"] = min(read_step(), len(STEPS))

        # Interval selector
        interval_frame = tk.Frame(body, bg="#1e1e2e")
        interval_frame.pack(fill="x", pady=(0, 8))
        tk.Label(interval_frame, text="Interval (minutes):", fg="#aaa",
                 bg="#1e1e2e", font=("Segoe UI", 11)).pack(side="left")
        self.interval_var = tk.StringVar(value="60")
        interval_entry = tk.Entry(
            interval_frame, textvariable=self.interval_var, width=6,
            font=("Segoe UI", 11), bg="#2a2a3e", fg="white",
            insertbackground="white", relief="flat",
        )
        interval_entry.pack(side="left", padx=(6, 0))

        # Buttons
        btn_frame = tk.Frame(body, bg="#1e1e2e")
        btn_frame.pack(pady=12)

        self.start_btn = tk.Button(
            btn_frame, text="  START  ", font=("Segoe UI", 13, "bold"),
            bg="#27ae60", fg="white", activebackground="#219a52",
            relief="flat", padx=24, pady=8, cursor="hand2",
            command=self.start,
        )
        self.start_btn.pack(side="left", padx=8)

        self.stop_btn = tk.Button(
            btn_frame, text="  STOP  ", font=("Segoe UI", 13, "bold"),
            bg="#e74c3c", fg="white", activebackground="#c0392b",
            relief="flat", padx=24, pady=8, cursor="hand2",
            command=self.stop, state="disabled",
        )
        self.stop_btn.pack(side="left", padx=8)

        # Log area
        tk.Label(body, text="Log:", fg="#aaa", bg="#1e1e2e",
                 font=("Segoe UI", 10), anchor="w").pack(fill="x")
        self.log = scrolledtext.ScrolledText(
            body, height=8, bg="#12121a", fg="#ccc",
            font=("Consolas", 10), relief="flat", state="disabled",
            insertbackground="white",
        )
        self.log.pack(fill="both", expand=True, pady=(2, 0))

        # Handle window close
        self.root.protocol("WM_DELETE_CLOSE", self.on_close)

    # ── Logging ────────────────────────────────────────────────────────
    def _log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log.configure(state="normal")
        self.log.insert("end", f"[{timestamp}] {msg}\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    # ── Start / Stop ───────────────────────────────────────────────────
    def start(self):
        # Validate git repo
        code, _, _ = git("status")
        if code != 0:
            messagebox.showerror("Error", "No git repository found in:\n" + REPO_DIR +
                                 "\n\nPlease run 'git init' first.")
            return

        try:
            interval_min = int(self.interval_var.get())
            if interval_min < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Interval must be a positive integer (minutes).")
            return

        self.running = True
        self.stop_event.clear()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_var.set("Running")
        self.status_label.configure(fg="#27ae60")
        self._log("Auto-builder started!")

        self.thread = threading.Thread(target=self._run_loop, args=(interval_min * 60,), daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_var.set("Stopped")
        self.status_label.configure(fg="#e74c3c")
        self._log("Stopped by user.")

    # ── Main loop (runs in background thread) ─────────────────────────
    def _run_loop(self, interval_secs):
        while not self.stop_event.is_set():
            step_num = read_step()
            self.root.after(0, lambda s=step_num: self.step_var.set(f"{s} / {len(STEPS)}+"))
            self.root.after(0, lambda s=step_num: self.progress.configure(value=min(s, len(STEPS))))

            # Execute the step
            if step_num < len(STEPS):
                self.root.after(0, lambda: self._log(f"Running step {step_num}..."))
                msg = STEPS[step_num]()
            else:
                # Rotating maintenance updates that write real code
                import re as _re
                version = step_num - len(STEPS) + 1
                cycle = (version - 1) % len(MAINTENANCE_CYCLES)
                msg = MAINTENANCE_CYCLES[cycle](version)
                # Also bump version in package.json
                pkg = os.path.join(REPO_DIR, "package.json")
                if os.path.exists(pkg):
                    with open(pkg, "r", encoding="utf-8") as f:
                        content = f.read()
                    content = _re.sub(r'"version":\s*"[^"]*"', f'"version": "1.0.{version}"', content)
                    with open(pkg, "w", encoding="utf-8") as f:
                        f.write(content)

            # Commit
            success = git_commit(msg)
            new_step = step_num + 1
            write_step(new_step)

            if success:
                self.root.after(0, lambda m=msg: self._log(f"Committed: {m}"))
            else:
                self.root.after(0, lambda: self._log("Nothing new to commit (no changes)."))

            self.root.after(0, lambda s=new_step: self.step_var.set(f"{s} / {len(STEPS)}+"))
            self.root.after(0, lambda s=new_step: self.progress.configure(value=min(s, len(STEPS))))

            # Wait for next interval (check stop_event every second)
            if step_num < len(STEPS):
                remaining = f"feature step"
            else:
                remaining = f"maintenance"
            self.root.after(0, lambda r=remaining, i=interval_secs:
                            self._log(f"Next {r} commit in {i // 60} min. Waiting..."))

            for _ in range(interval_secs):
                if self.stop_event.is_set():
                    return
                time.sleep(1)

    # ── Cleanup ────────────────────────────────────────────────────────
    def on_close(self):
        self.stop_event.set()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


# ── Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = FriendZoneBuilder()
    app.run()
