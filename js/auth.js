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
