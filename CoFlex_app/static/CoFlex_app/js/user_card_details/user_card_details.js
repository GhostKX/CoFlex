class CardDetailsForm {
    constructor() {
        this.form = document.getElementById('card-details-form');
        this.submitButton = document.getElementById('submit-card-details');
        
        this.init();
    }

    init() {
        this.addInputFormatting();
        this.addSubmitListener();
        this.handleAutoRemoveMessages();
    }

    addInputFormatting() {
        const cardNumberInput = this.form.querySelector('input[name="card_number"]');
        const expiryDateInput = this.form.querySelector('input[name="expiry_date"]');
        const cvvInput = this.form.querySelector('input[name="cvv"]');

        // Card Number Formatting
        cardNumberInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            value = value.replace(/(\d{4})(?=\d)/g, '$1 ');
            e.target.value = value.slice(0, 19);
        });

        // Expiry Date Formatting
        expiryDateInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 2) {
                value = value.slice(0, 2) + '/' + value.slice(2, 4);
            }
            e.target.value = value.slice(0, 5);
        });

        // CVV Formatting
        cvvInput.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/\D/g, '').slice(0, 3);
        });
    }

    addSubmitListener() {
        this.form.addEventListener('submit', (e) => {
            this.disableSubmitButton();
        });
    }

    disableSubmitButton() {
        this.submitButton.disabled = true;
        this.submitButton.innerHTML = `
            <span class="material-icons button-icon">pending</span>
            Processing Payment
        `;
    }

    handleAutoRemoveMessages() {
        const messages = document.querySelector('.messages');
        if (messages) {
            setTimeout(() => {
                messages.style.transition = 'opacity 1s ease';
                messages.style.opacity = '0';
                setTimeout(() => messages.remove(), 1000);
            }, 3000);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new CardDetailsForm();
});