document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    const form = document.querySelector('.login-form');
    const emailInput = form.querySelector('input[type="email"]');
    const passwordInput = form.querySelector('input[type="password"]');

    // Form submission handler
    form.addEventListener('submit', function(e) {
        let isValid = true;

        // Reset previous error states
        removeErrorState(emailInput);
        removeErrorState(passwordInput);

        // Email validation
        if (!emailInput.value.trim()) {
            addErrorState(emailInput, 'Email is required');
            isValid = false;
        } else if (!isValidEmail(emailInput.value)) {
            addErrorState(emailInput, 'Please enter a valid email address');
            isValid = false;
        }

        // Password validation
        if (!passwordInput.value) {
            addErrorState(passwordInput, 'Password is required');
            isValid = false;
        }

        // Prevent form submission if validation fails
        if (!isValid) {
            e.preventDefault();
        }
    });

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function addErrorState(input, message) {
        const formGroup = input.closest('.form-group');
        input.classList.add('input--error');

        if (!formGroup.querySelector('.error-message')) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = message;
            formGroup.appendChild(errorDiv);
        }
    }

    function removeErrorState(input) {
        const formGroup = input.closest('.form-group');
        input.classList.remove('input--error');

        const errorMessage = formGroup.querySelector('.error-message');
        if (errorMessage) {
            errorMessage.remove();
        }
    }

    emailInput.addEventListener('input', () => {
        if (emailInput.value.trim()) {
            removeErrorState(emailInput);
        }
    });

    passwordInput.addEventListener('input', () => {
        if (passwordInput.value) {
            removeErrorState(passwordInput);
        }
    });

    const messages = document.querySelector('.messages');
    if (messages) {
        setTimeout(() => {
            messages.style.transition = 'opacity 1s ease';
            messages.style.opacity = '0';
            setTimeout(() => messages.remove(), 1000);
        }, 3000);
    }
});
