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
                        ${liked ? '\u2764\uFE0F' : '\uD83E\uDD0D'} ${post.likes.length}</button>
                    <button class="btn-comment" data-id="${post.id}">
                        \uD83D\uDCAC ${post.comments.length}</button>
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
