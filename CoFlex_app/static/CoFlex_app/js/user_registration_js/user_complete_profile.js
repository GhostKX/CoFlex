class ProfileCompletion {
    constructor() {
        this.form = document.querySelector('.profile-form');
        this.progressFill = document.getElementById('progressFill');
        this.formFields = document.querySelectorAll('input, textarea');

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
        submitButton.innerHTML = 'Saving...';
    }
}

window.confirmSkip = function(redirectUrl) {
    const hasData = Array.from(document.querySelectorAll('input, textarea'))
        .some(field => field.value.trim() !== '');

    if (hasData) {
        const confirmed = confirm(
            'You have entered some information. Are you sure you want to skip? Your entries will not be saved.'
        );
        if (!confirmed) {
            return;
        }
    }

    window.location.href = redirectUrl;
};

document.addEventListener('DOMContentLoaded', () => {
    new ProfileCompletion();

    const messages = document.querySelector('.messages');
    if (messages) {
        setTimeout(() => {
            messages.style.transition = 'opacity 1s ease';
            messages.style.opacity = '0';
            setTimeout(() => messages.remove(), 500);
        }, 3000);
    }
});
