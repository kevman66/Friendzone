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
