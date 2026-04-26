// Shared avatar dropdown logic - include at bottom of every page
(function() {
    const email = localStorage.getItem("userEmail");
    const loginLink = document.getElementById("loginLink");
    const avatarWrapper = document.getElementById("avatarWrapper");
    const avatarBtn = document.getElementById("avatarBtn");
    const userDropdown = document.getElementById("userDropdown");
    const dropdownEmail = document.getElementById("dropdownEmail");
    const logoutBtn = document.getElementById("logoutBtn");

    if (!avatarWrapper) return;

    if (email) {
        if (loginLink) loginLink.style.display = "none";
        avatarWrapper.style.display = "inline-block";
        if (dropdownEmail) dropdownEmail.textContent = email;
    } else {
        if (loginLink) loginLink.style.display = "inline";
        avatarWrapper.style.display = "none";
    }

    if (avatarBtn) {
        avatarBtn.addEventListener("click", function(e) {
            e.stopPropagation();
            userDropdown.classList.toggle("open");
        });
    }

    document.addEventListener("click", function() {
        if (userDropdown) userDropdown.classList.remove("open");
    });

    if (logoutBtn) {
        logoutBtn.addEventListener("click", function() {
            localStorage.removeItem("userEmail");
            window.location.href = "index.html";
        });
    }
})();
