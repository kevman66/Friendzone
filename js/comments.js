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
