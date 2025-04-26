document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('stopSubscriptionForm');
    const password1Input = document.getElementById('password1');
    const password2Input = document.getElementById('password2');
    const confirmCheckbox = document.getElementById('confirmStop');
    const stopButton = document.querySelector('.stop-button');

    // Creating modal elements
    const modalOverlay = document.createElement('div');
    modalOverlay.className = 'modal-overlay';

    const modalContent = document.createElement('div');
    modalContent.className = 'modal-content';
    modalContent.innerHTML = `
        <div class="modal-header">
            <span class="material-icons modal-icon">warning</span>
            <h3>Confirm Subscription Pause</h3>
        </div>
        <div class="modal-body">
            <p>Are you sure you want to stop your subscription?</p>
        </div>
        <div class="modal-footer">
            <button type="button" class="modal-button cancel-modal">
                <span class="material-icons button-icon">close</span>
                <span class="button-text">No, Cancel</span>
            </button>
            <button type="button" class="modal-button confirm-modal">
                <span class="material-icons button-icon">pause_circle_outline</span>
                <span class="button-text">Yes, Pause</span>
            </button>
        </div>
    `;

    modalOverlay.appendChild(modalContent);
    document.body.appendChild(modalOverlay);

    // Adding styles for the modal
    const modalStyles = document.createElement('style');
    modalStyles.textContent = `
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes slideIn {
            from { transform: translateY(-20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        .modal-content {
            background-color: #ffffff;
            border-radius: 1rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
            width: 90%;
            max-width: 480px;
            padding: 1.5rem;
            animation: slideIn 0.3s ease;
        }

        .modal-header {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }

        .modal-icon {
            font-size: 1.75rem;
            color: var(--warning-color);
            margin-right: 0.75rem;
        }

        .modal-header h3 {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
            margin: 0;
        }

        .modal-body {
            margin-bottom: 1.5rem;
        }

        .modal-body p {
            color: var(--text-secondary);
            font-size: 0.938rem;
            margin-bottom: 0.5rem;
        }

        .modal-footer {
            display: flex;
            justify-content: flex-end;
            gap: 0.75rem;
        }

        .modal-button {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1rem;
            border-radius: 0.5rem;
            font-size: 0.938rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .cancel-modal {
            background-color: var(--bg-secondary);
            color: var(--text-primary);
            border: 1.5px solid var(--border-color);
        }

        .cancel-modal:hover {
            background-color: var(--border-color);
        }

        .confirm-modal {
            background-color: var(--warning-color);
            color: white;
            border: none;
        }

        .confirm-modal:hover {
            background-color: #b45309;
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }
    `;
    document.head.appendChild(modalStyles);

    // Modal functionality
    const openModal = () => {
        modalOverlay.style.display = 'flex';
        document.body.style.overflow = 'hidden'; // Preventing scrolling
    };

    const closeModal = () => {
        modalOverlay.style.display = 'none';
        document.body.style.overflow = '';
    };

    // Form validation functions
    function validateForm() {
        const isValid = password1Input.value.length > 0 &&
                       password2Input.value.length > 0 &&
                       confirmCheckbox.checked &&
                       password1Input.value === password2Input.value;
        stopButton.disabled = !isValid;

        if (password1Input.value && password2Input.value &&
            password1Input.value !== password2Input.value) {
            addErrorState(password2Input, 'Passwords do not match');
        } else {
            removeErrorState(password2Input);
        }
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

    // Event listeners
    password1Input.addEventListener('input', validateForm);
    password2Input.addEventListener('input', validateForm);
    confirmCheckbox.addEventListener('change', validateForm);

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

    // Form submission handling
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        if (password1Input.value !== password2Input.value) {
            addErrorState(password2Input, 'Passwords do not match');
            return;
        }

        // Showing custom modal instead of the browser confirm
        openModal();
    });

    // Modal button handlers
    document.querySelector('.cancel-modal').addEventListener('click', closeModal);

    document.querySelector('.confirm-modal').addEventListener('click', () => {
        stopButton.disabled = true;
        stopButton.innerHTML = `
            <span class="material-icons button-icon">hourglass_empty</span>
            <span class="button-text">Processing...</span>
        `;

        closeModal();
        form.submit();
    });

    // Closing modal if clicking outside content
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) {
            closeModal();
        }
    });

    // Handling escape key to close modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modalOverlay.style.display === 'flex') {
            closeModal();
        }
    });

    // Hiding messages
    const messages = document.querySelector('.messages');
    if (messages) {
        setTimeout(() => {
            messages.style.transition = 'opacity 1s ease';
            messages.style.opacity = '0';
            setTimeout(() => messages.remove(), 1000);
        }, 3000);
    }
});