document.addEventListener("DOMContentLoaded", () => {
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const usernameFeedback = document.getElementById("username-feedback");
    const passwordFeedback = document.getElementById("password-feedback");

    /**
     * Updates the feedback element with a message and color.
     */
    const setFeedback = (element, message, isValid) => {
        element.textContent = message;
        element.style.color = isValid ? "#00ff88" : "#ff4d4d";
    };

    // Username Real-time Validation
    usernameInput.addEventListener("input", () => {
        const value = usernameInput.value;
        const usernameRegex = /^[a-zA-Z0-9_]+$/;

        if (value.length === 0) {
            setFeedback(usernameFeedback, "", true);
        } else if (value.length < 4 || value.length > 20) {
            setFeedback(usernameFeedback, "Username must be 4–20 characters.", false);
        } else if (!usernameRegex.test(value)) {
            setFeedback(usernameFeedback, "Username can only contain letters, numbers, and underscores.", false);
        } else {
            setFeedback(usernameFeedback, "Username is valid.", true);
        }
    });

    // Password Real-time Validation
    passwordInput.addEventListener("input", () => {
        const value = passwordInput.value;
        const hasNumber = /\d/.test(value);
        const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(value);

        if (value.length === 0) {
            setFeedback(passwordFeedback, "", true);
        } else if (value.length < 8) {
            setFeedback(passwordFeedback, "Password must be at least 8 characters long.", false);
        } else if (!hasNumber) {
            setFeedback(passwordFeedback, "Password must contain at least one number.", false);
        } else if (!hasSpecial) {
            setFeedback(passwordFeedback, "Password must contain at least one special character.", false);
        } else {
            setFeedback(passwordFeedback, "Strong password!", true);
        }
    });
});