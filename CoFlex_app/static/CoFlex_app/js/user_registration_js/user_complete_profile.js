class ProfileCompletion {
    constructor() {
        this.form = document.querySelector('.profile-form');
        this.progressFill = document.getElementById('progressFill');
        this.formFields = document.querySelectorAll('input, textarea');
        this.createModal();

        this.init();
    }

    init() {
        this.updateProgress();

        this.formFields.forEach(field => {
            field.addEventListener('input', () => this.updateProgress());
        });

        this.form.addEventListener('submit', this.handleSubmit.bind(this));
    }

    updateProgress() {
        const totalFields = this.formFields.length;
        const filledFields = Array.from(this.formFields)
            .filter(field => field.value.trim() !== '').length;

        const progress = (filledFields / totalFields) * 100;
        this.progressFill.style.width = `${progress}%`;
    }

    handleSubmit(event) {
        const submitButton = this.form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="material-icons button-icon">hourglass_empty</span> Saving...';
    }

    createModal() {
        // Create modal elements
        const modalOverlay = document.createElement('div');
        modalOverlay.className = 'modal-overlay';

        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        modalContent.innerHTML = `
            <div class="modal-header">
                <span class="material-icons modal-icon">help_outline</span>
                <h3>Skip Profile Completion?</h3>
            </div>
            <div class="modal-body">
                <p>Are you sure you want to skip? Your entries will not be saved.</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="modal-button cancel-modal">
                    <span class="material-icons button-icon">arrow_back</span>
                    <span class="button-text">Continue Editing</span>
                </button>
                <button type="button" class="modal-button confirm-modal">
                    <span class="material-icons button-icon">skip_next</span>
                    <span class="button-text">Skip Anyway</span>
                </button>
            </div>
        `;

        modalOverlay.appendChild(modalContent);
        document.body.appendChild(modalOverlay);

        // Add styles for the modal
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
                color: var(--info-color);
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
                border: none;
            }

            .cancel-modal {
                background-color: #f3f4f6;
                color: var(--text-primary);
                border: 1px solid var(--border-color);
            }

            .cancel-modal:hover {
                background-color: var(--border-color);
            }

            .confirm-modal {
                background-color: var(--info-color);
                color: white;
            }

            .confirm-modal:hover {
                background-color: #0369a1;
                transform: translateY(-1px);
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }

            @media (max-width: 640px) {
                .modal-footer {
                    flex-direction: column-reverse;
                }

                .modal-button {
                    width: 100%;
                }
            }
        `;
        document.head.appendChild(modalStyles);

        // Storing modal elements for later access
        this.modalOverlay = modalOverlay;
        this.redirectUrl = '';

        // Adding event listeners for modal buttons
        modalOverlay.querySelector('.cancel-modal').addEventListener('click', () => {
            this.closeModal();
        });

        modalOverlay.querySelector('.confirm-modal').addEventListener('click', () => {
            window.location.href = this.redirectUrl;
        });

        // Closing modal if clicking outside content
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) {
                this.closeModal();
            }
        });

        // Handling escape key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modalOverlay.style.display === 'flex') {
                this.closeModal();
            }
        });
    }

    openModal(redirectUrl) {
        this.redirectUrl = redirectUrl;
        this.modalOverlay.style.display = 'flex';
        document.body.style.overflow = 'hidden'; // Preventing scrolling
    }

    closeModal() {
        this.modalOverlay.style.display = 'none';
        document.body.style.overflow = ''; // Restoring scrolling
    }
}

// Replacing the original confirmSkip function with our modal version
window.confirmSkip = function(redirectUrl) {
    const hasData = Array.from(document.querySelectorAll('input, textarea'))
        .some(field => field.value.trim() !== '');

    if (hasData) {
        // Opening modal if there's data in the form
        window.profileCompletionInstance.openModal(redirectUrl);
    } else {
        // If no data, redirecting immediately
        window.location.href = redirectUrl;
    }
};

document.addEventListener('DOMContentLoaded', () => {
    window.profileCompletionInstance = new ProfileCompletion();

    const messages = document.querySelector('.messages');
    if (messages) {
        setTimeout(() => {
            messages.style.transition = 'opacity 1s ease';
            messages.style.opacity = '0';
            setTimeout(() => messages.remove(), 500);
        }, 3000);
    }
});