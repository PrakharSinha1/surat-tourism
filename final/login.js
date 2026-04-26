// API variable is defined in api-config.js (loaded in HTML)
let isLogin = true;

function toggleMode() {
    isLogin = !isLogin;
    document.getElementById("formTitle").innerText = isLogin ? "Login ✨" : "Register 🚀";
    document.getElementById("authBtn").innerText = isLogin ? "Login" : "Register";
    document.getElementById("toggleText").innerText = isLogin ? "New here?" : "Already have an account?";
}

async function handleAuth() {
    const email    = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const isAdmin  = document.getElementById("adminToggle")?.checked || false;

    if (!email || !password) {
        alert("Please enter email & password");
        return;
    }

    const url = isLogin
        ? `${API}/login`
        : `${API}/register`;

    try {
        const res = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password, is_admin: isAdmin })
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.error || "Error occurred");
            return;
        }

        // Store session
        localStorage.setItem("userEmail", email);
        if (isAdmin || data.is_admin) {
            localStorage.setItem("isAdmin", "true");
        } else {
            localStorage.removeItem("isAdmin");
        }

        alert(isLogin ? "Login Successful 🚀" : "Account Created ✅");

        // Redirect admin to dashboard, users to home
        if (isAdmin || data.is_admin) {
            window.location.href = "dashboard.html";
        } else {
            window.location.href = "index.html";
        }

    } catch (err) {
        console.error(err);
        // Offline fallback for demo
        if (isAdmin && email === "admin@surat.com" && password === "admin123@") {
            localStorage.setItem("userEmail", email);
            localStorage.setItem("isAdmin", "true");
            alert("Admin Login (Demo Mode) ✅");
            window.location.href = "dashboard.html";
        } else if (!isAdmin) {
            localStorage.setItem("userEmail", email);
            localStorage.removeItem("isAdmin");
            alert("Login (Demo Mode) ✅\nNote: Backend not connected.");
            window.location.href = "index.html";
        } else {
            alert("Admin credentials incorrect or server not running ❌");
        }
    }
}