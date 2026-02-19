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
