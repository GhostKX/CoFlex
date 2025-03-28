document.addEventListener('DOMContentLoaded', function() {
    // Getting DOM elements
    const oldPasswordInput = document.getElementById('old_password');
    const newPasswordInput = document.getElementById('new_password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const submitButton = document.getElementById('submit-btn');
    const strengthIndicator = document.getElementById('password-strength');

    // Password validation patterns
    const patterns = {
        minLength: password => password.length >= 8,
        uppercase: password => /[A-Z]/.test(password),
        lowercase: password => /[a-z]/.test(password),
        number: password => /[0-9]/.test(password),
        special: password => /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };

    // Requirement messages
    const requirements = {
        minLength: 'Minimum 8 characters',
        uppercase: 'At least one uppercase letter (A-Z)',
        lowercase: 'At least one lowercase letter (a-z)',
        number: 'At least one number (0-9)',
        special: 'At least one special character (!@#$%^&*(),.?":{}|<>)'
    };

    // Check if the password meets all requirements
    function checkPasswordRequirements(password) {
        const checks = {
            minLength: patterns.minLength(password),
            uppercase: patterns.uppercase(password),
            lowercase: patterns.lowercase(password),
            number: patterns.number(password),
            special: patterns.special(password)
        };

        updateRequirementsDisplay(checks);

        return Object.values(checks).every(Boolean);
    }

    function updateRequirementsDisplay(checks) {
        strengthIndicator.innerHTML = Object.entries(checks)
            .map(([requirement, isMet]) => `
                <div class="requirement ${isMet ? 'met' : 'unmet'}">
                    <span class="material-icons">
                        ${isMet ? 'check_circle' : 'cancel'}
                    </span>
                    ${requirements[requirement]}
                </div>
            `).join('');
    }

    oldPasswordInput.addEventListener('input', function() {
        const meetsRequirements = checkPasswordRequirements(this.value);
        newPasswordInput.disabled = !meetsRequirements;
        confirmPasswordInput.disabled = !meetsRequirements;
        validateForm();
    });

    newPasswordInput.addEventListener('input', function() {
        checkPasswordRequirements(this.value);
        validateForm();
    });

    confirmPasswordInput.addEventListener('input', function() {
        validateForm();
    });

    function validateForm() {
        const oldPasswordValid = checkPasswordRequirements(oldPasswordInput.value);
        const newPasswordValid = checkPasswordRequirements(newPasswordInput.value);
        const passwordsMatch = newPasswordInput.value === confirmPasswordInput.value
            && newPasswordInput.value !== '';

        submitButton.disabled = !(oldPasswordValid && newPasswordValid && passwordsMatch);
    }

    checkPasswordRequirements('');
});



