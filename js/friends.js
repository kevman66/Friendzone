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
