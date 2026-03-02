document.addEventListener("DOMContentLoaded", () => {
    // Mapping inputs to their respective error display elements
    const fields = {
        name: {
            input: document.getElementById("full_name"),
            error: document.getElementById("name-error"),
            validate: (val) => {
                const nameRegex = /^[a-zA-Z\s]+$/;
                if (!val) return ""; // Don't show error if empty
                if (val.length < 2 || val.length > 30) return "Name must be 2–30 characters.";
                if (!nameRegex.test(val)) return "Only letters and spaces allowed.";
                return "";
            }
        },
        age: {
            input: document.getElementById("age"),
            error: document.getElementById("age-error"),
            validate: (val) => {
                const ageVal = parseInt(val);
                if (!val) return "";
                if (isNaN(ageVal) || ageVal < 10 || ageVal > 80) return "Age must be 10–80.";
                return "";
            }
        },
        height: {
            input: document.getElementById("height"),
            error: document.getElementById("height-error"),
            validate: (val) => {
                const hVal = parseFloat(val);
                if (!val) return "";
                if (isNaN(hVal) || hVal < 100 || hVal > 250) return "Height must be 100–250 cm.";
                return "";
            }
        },
        weight: {
            input: document.getElementById("weight"),
            error: document.getElementById("weight-error"),
            validate: (val) => {
                const wVal = parseFloat(val);
                if (!val) return "";
                if (isNaN(wVal) || wVal < 30 || wVal > 250) return "Weight must be 30–250 kg.";
                return "";
            }
        }
    };

    const submitBtn = document.getElementById("complete-button");
    const goalSelect = document.getElementById("goal");
    const levelSelect = document.getElementById("fitness_level");

    /**
     * Updates the UI for a specific field and returns if it is valid.
     */
    const checkField = (key) => {
        const field = fields[key];
        const errorMessage = field.validate(field.input.value.trim());
        
        field.error.textContent = errorMessage;
        field.error.style.color = "#ff4d4d";
        
        // Return true if no error message exists
        return errorMessage === "";
    };

    /**
     * Checks all fields to enable/disable the submit button.
     */
    const updateButtonState = () => {
        const isNameValid = checkField("name");
        const isAgeValid = checkField("age");
        const isHeightValid = checkField("height");
        const isWeightValid = checkField("weight");

        // Ensure dropdowns are also selected
        const dropdownsSelected = goalSelect.value !== "" && levelSelect.value !== "";
        
        // Ensure required text fields aren't just "valid" (empty), but actually filled
        const allFilled = Object.values(fields).every(f => f.input.value.trim() !== "");

        if (isNameValid && isAgeValid && isHeightValid && isWeightValid && dropdownsSelected && allFilled) {
            submitBtn.disabled = false;
            submitBtn.style.opacity = "1";
            submitBtn.style.cursor = "pointer";
        } else {
            submitBtn.disabled = true;
            submitBtn.style.opacity = "0.5";
            submitBtn.style.cursor = "not-allowed";
        }
    };

    // Add event listeners for real-time validation
    Object.keys(fields).forEach(key => {
        fields[key].input.addEventListener("input", () => {
            checkField(key);      // Show/hide error for THIS field only
            updateButtonState();  // Update button globally
        });
    });

    // Listen for dropdown changes
    [goalSelect, levelSelect].forEach(select => {
        select.addEventListener("change", updateButtonState);
    });

    // Run once on load to set initial button state
    updateButtonState();
});