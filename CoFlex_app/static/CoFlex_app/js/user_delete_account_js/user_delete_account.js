document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('deleteAccountForm');
    const password1Input = document.getElementById('password1');
    const password2Input = document.getElementById('password2');
    const confirmCheckbox = document.getElementById('confirmDelete');
    const deleteButton = document.querySelector('.delete-button');

    function validateForm() {
        const isValid = password1Input.value.length > 0 &&
                       password2Input.value.length > 0 &&
                       confirmCheckbox.checked &&
                       password1Input.value === password2Input.value;
        deleteButton.disabled = !isValid;

        if (password1Input.value && password2Input.value &&
            password1Input.value !== password2Input.value) {
            addErrorState(password2Input, 'Passwords do not match');
        } else {
            removeErrorState(password2Input);
        }
    }

    password1Input.addEventListener('input', validateForm);
    password2Input.addEventListener('input', validateForm);
    confirmCheckbox.addEventListener('change', validateForm);

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        if (password1Input.value !== password2Input.value) {
            addErrorState(password2Input, 'Passwords do not match');
            return;
        }

        const confirmed = confirm(
            'Are you absolutely sure you want to delete your account? ' +
            'This action cannot be undone and all your data will be permanently deleted.'
        );

        if (confirmed) {
            deleteButton.disabled = true;
            const originalText = deleteButton.innerHTML;
            deleteButton.innerHTML = `
                <span class="material-icons button-icon">hourglass_empty</span>
                <span class="button-text">Deleting...</span>
            `;

            this.submit();
        }
    });

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

    password1Input.addEventListener('input', () => {
        if (password1Input.value.trim()) {
            removeErrorState(password1Input);
        }
    });

    password2Input.addEventListener('input', () => {
        if (password2Input.value.trim()) {
            removeErrorState(password2Input);
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