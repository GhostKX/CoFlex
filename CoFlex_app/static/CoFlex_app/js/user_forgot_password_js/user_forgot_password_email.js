document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('resetForm');
    const submitButton = form.querySelector('.submit-btn');
    const emailInput = document.getElementById('id_email');

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const errorMessage = form.querySelector('.error-message');
        if (errorMessage) {
            errorMessage.remove();
        }
        emailInput.parentElement.classList.remove('has-error');

        if (!emailInput.value) {
            showError('Please enter your email address');
            return;
        }

        if (!isValidEmail(emailInput.value)) {
            showError('Please enter a valid email address');
            return;
        }

        setLoadingState(true);

        try {
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            showSuccess();

        } catch (error) {
            showError('An error occurred. Please try again later.');
        } finally {
            setLoadingState(false);
        }
    });

    function showError(message) {
        emailInput.parentElement.classList.add('has-error');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.role = 'alert';
        errorDiv.textContent = message;
        emailInput.parentElement.appendChild(errorDiv);
        emailInput.focus();
    }

    function showSuccess() {
        const successMessage = document.createElement('div');
        successMessage.className = 'alert';
        successMessage.style.backgroundColor = 'var(--success-color)';
        successMessage.style.color = 'white';
        successMessage.style.padding = '1rem';
        successMessage.style.borderRadius = '0.5rem';
        successMessage.style.marginTop = '1rem';
        successMessage.innerHTML = `
            <span class="material-icons">check_circle</span>
            <p>Password reset link has been sent to your email address. Please check your inbox.</p>
        `;
        form.innerHTML = '';
        form.appendChild(successMessage);
    }

    function setLoadingState(isLoading) {
        if (isLoading) {
            submitButton.classList.add('loading');
            submitButton.disabled = true;
            const icon = submitButton.querySelector('.material-icons');
            icon.textContent = 'loop';
        } else {
            submitButton.classList.remove('loading');
            submitButton.disabled = false;
            const icon = submitButton.querySelector('.material-icons');
            icon.textContent = 'send';
        }
    }
});