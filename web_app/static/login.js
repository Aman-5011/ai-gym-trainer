document.addEventListener("DOMContentLoaded", () => {
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const loginButton = document.getElementById("login-button");
    const loginFeedback = document.getElementById("login-feedback");
    const togglePasswordBtn = document.getElementById("toggle-password");

    /**
     * Checks if both inputs have values and updates UI accordingly.
     */
    const validateForm = () => {
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        if (username === "" || password === "") {
            loginFeedback.textContent = "Username and password are required.";
            loginFeedback.style.color = "#ff4d4d";
            loginButton.disabled = true;
            loginButton.style.opacity = "0.5";
            loginButton.style.cursor = "not-allowed";
        } else {
            loginFeedback.textContent = "";
            loginButton.disabled = false;
            loginButton.style.opacity = "1";
            loginButton.style.cursor = "pointer";
        }
    };

    // Listen for input changes
    usernameInput.addEventListener("input", validateForm);
    passwordInput.addEventListener("input", validateForm);

    // Initial check in case of browser autofill
    validateForm();

    // Toggle password visibility feature
    if (togglePasswordBtn) {
        togglePasswordBtn.addEventListener("click", (e) => {
            e.preventDefault();
            const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
            passwordInput.setAttribute("type", type);
            
            // Optional: update button text/icon if needed
            togglePasswordBtn.textContent = type === "password" ? "👁" : "🙈";
        });
    }
});