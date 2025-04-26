class EnhancedPaymentVerification {
    constructor() {
        // Form elements
        this.form = document.getElementById('card-details-form');

        // Card input fields
        this.cardNumberInput = document.querySelector('input[name="card_number"]');
        this.expiryDateInput = document.querySelector('input[name="expiry_date"]');
        this.cvvInput = document.querySelector('input[name="cvv"]');
        this.cardHolderInput = document.querySelector('input[name="card_holder_name"]');
        this.termsCheckbox = document.getElementById('terms_agreement');
        this.termsError = document.getElementById('terms-error');

        // Section elements
        this.cardDetailsSection = document.querySelector('.card-details-section');
        this.verificationSection = document.querySelector('.verification-section');

        // Buttons
        this.cancelPaymentButton = document.getElementById('cancel-payment');
        this.verifyPaymentButton = document.getElementById('verify-payment-button');
        this.cancelVerificationButton = document.getElementById('cancel-verification');
        this.confirmPaymentButton = document.getElementById('submit-card-details');
        this.resendCodeButton = document.getElementById('resend-code-button');

        // Verification code elements
        this.verificationCodeInput = document.querySelector('input[name="verification_code"]');
        this.timerElement = document.getElementById('resend-timer');
        this.timerDisplay = document.querySelector('#resend-timer span');
        this.resendForm = document.getElementById('resend-form');

        // Validation state
        this.fieldStates = {
            cardNumber: false,
            expiryDate: false,
            cvv: false,
            cardHolder: false,
            terms: false,
            verificationCode: false
        };

        // Form submission state
        this.verificationCodeSent = false;
        this.resendTimerInterval = null;
        this.messageTimeout = null;

        // Store card data to persist through transitions
        this.cardData = {};

        this.init();
    }

    init() {
        // Set initial state - card details active, verification section disabled
        this.setupInitialState();

        // Setup input formatting and validation
        this.setupInputFormatting();

        // Setup event listeners for buttons
        this.setupButtonListeners();

        // Setup form submission
        this.setupFormSubmission();

        // Auto-hide any existing messages
        this.handleAutoHideMessages();

        // Add custom styles for validation states
        this.addCustomStyles();
    }

    setupInitialState() {
        // Initially disable verification section
        this.verificationSection.classList.add('disabled-section');
        this.verificationSection.style.opacity = '0.5';
        this.verificationSection.style.transform = 'translateY(20px)';
        this.verificationSection.style.pointerEvents = 'none';

        // Disable verification section inputs and button
        const verificationInputs = this.verificationSection.querySelectorAll('input, button');
        verificationInputs.forEach(input => input.disabled = true);

        // Initialize verify button state
        this.updateVerifyButtonState();
    }

    setupInputFormatting() {
        // Card Number formatting
        this.cardNumberInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            value = value.replace(/(\d{4})(?=\d)/g, '$1 ');
            e.target.value = value.slice(0, 19); // 16 digits + 3 spaces
            this.validateCardNumber();
        });

        // Expiry Date formatting
        this.expiryDateInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 2) {
                value = value.slice(0, 2) + '/' + value.slice(2, 4);
            }
            e.target.value = value.slice(0, 5);
            this.validateExpiryDate();
        });

        // CVV formatting
        this.cvvInput.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/\D/g, '').slice(0, 4);
            this.validateCvv();
        });

        // Cardholder Name formatting
        this.cardHolderInput.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/[^A-Za-z ]/g, '');
            this.validateCardHolder();
        });

        // Terms checkbox
        this.termsCheckbox.addEventListener('change', () => {
            this.validateTerms();
        });

        // Verification Code formatting
        this.verificationCodeInput.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/\D/g, '').slice(0, 6);
            this.validateVerificationCode();

            // Auto-focus submit button when 6 digits entered
            if (e.target.value.length === 6) {
                this.confirmPaymentButton.focus();
                this.updateConfirmButtonState();
            }
        });

        // Add blur event listeners for more complete validation messages
        this.cardNumberInput.addEventListener('blur', () => this.validateCardNumber(true));
        this.expiryDateInput.addEventListener('blur', () => this.validateExpiryDate(true));
        this.cvvInput.addEventListener('blur', () => this.validateCvv(true));
        this.cardHolderInput.addEventListener('blur', () => this.validateCardHolder(true));
        this.verificationCodeInput.addEventListener('blur', () => this.validateVerificationCode(true));
    }

    setupButtonListeners() {
        // Cancel payment button (Go back)
        if (this.cancelPaymentButton) {
            this.cancelPaymentButton.addEventListener('click', () => {
                window.history.back();
            });
        }

        // Verify payment button (Send verification code)
        if (this.verifyPaymentButton) {
            this.verifyPaymentButton.addEventListener('click', () => {
                if (this.validateAllCardFields()) {
                    // Storing card data before sending verification code
                    this.storeCardData();
                    this.handleVerificationCode(false);
                }
            });
        }

        // Canceling verification button (Return to card details)
        if (this.cancelVerificationButton) {
            this.cancelVerificationButton.addEventListener('click', () => {
                this.transitionToCardDetailsSection();
            });
        }

        // Confirming payment button
        if (this.confirmPaymentButton) {
            this.confirmPaymentButton.addEventListener('click', () => {
                // Fixed: Only submit form after verification
                if (this.verificationCodeSent && this.validateVerificationCode(true)) {
                    // Showing loading state
                    this.confirmPaymentButton.disabled = true;
                    this.confirmPaymentButton.innerHTML = `
                        <span class="material-icons button-icon loading">pending</span> Processing...
                    `;
                    this.animateLoadingIcon(this.confirmPaymentButton.querySelector('.loading'));

                    // Adding card data to form before submission
                    this.addCardDataToForm();

                    // Submitting the form
                    setTimeout(() => this.form.submit(), 500);
                }
            });
        }

        // Resending verification code button
        console.log('Resend code button:', this.resendCodeButton);
        if (this.resendCodeButton) {

            console.log('Adding click event to resend button');
            this.resendCodeButton.removeEventListener('click', this._resendClickHandler);

            this.resendCodeButton.addEventListener('click', () => {
                console.log('Resend button clicked');
                this.handleVerificationCode(true);
            });

            // Adding the listener
            this.resendCodeButton.addEventListener('click', this._resendClickHandler);

        }  else {
              console.error('Resend button not found in DOM!');
        }
    }

    setupFormSubmission() {
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();

            // If in verification mode, validate verification code
            if (this.verificationCodeSent) {
                if (this.validateVerificationCode(true)) {
                    // Show loading state on button
                    this.confirmPaymentButton.disabled = true;
                    this.confirmPaymentButton.innerHTML = `
                        <span class="material-icons button-icon loading">pending</span> Processing...
                    `;
                    this.animateLoadingIcon(this.confirmPaymentButton.querySelector('.loading'));

                    // Add card data to form before submission
                    this.addCardDataToForm();

                    // Submit the form
                    setTimeout(() => this.form.submit(), 500);
                }
            } else {
                // If in card details mode, validate card fields and send verification code
                if (this.validateAllCardFields()) {
                    // Store card data before sending verification code
                    this.storeCardData();
                    this.handleVerificationCode(false);
                }
            }
        });
    }

    // Adding a new method to add card data to form
    addCardDataToForm() {
        if (Object.keys(this.cardData).length > 0) {
            // Check if hidden inputs already exist
            let cardNumberInput = this.form.querySelector('input[name="card_number"]');
            let expiryDateInput = this.form.querySelector('input[name="expiry_date"]');
            let cvvInput = this.form.querySelector('input[name="cvv"]');
            let cardHolderInput = this.form.querySelector('input[name="card_holder_name"]');

            // If hidden inputs don't exist (they might be disabled or hidden), create them
            if (!cardNumberInput.value) {
                cardNumberInput.value = this.cardData.cardNumber || '';
            }

            if (!expiryDateInput.value) {
                expiryDateInput.value = this.cardData.expiryDate || '';
            }

            if (!cvvInput.value) {
                cvvInput.value = this.cardData.cvv || '';
            }

            if (!cardHolderInput.value) {
                cardHolderInput.value = this.cardData.cardHolder || '';
            }
        }
    }

    // Storing card data before transitioning to verification section
    storeCardData() {
        this.cardData = {
            cardNumber: this.cardNumberInput.value,
            expiryDate: this.expiryDateInput.value,
            cvv: this.cvvInput.value,
            cardHolder: this.cardHolderInput.value,
            terms: this.termsCheckbox.checked
        };
    }

    // Restoring card data before form submission
    restoreCardData() {
        if (Object.keys(this.cardData).length > 0) {
            this.cardNumberInput.value = this.cardData.cardNumber || '';
            this.expiryDateInput.value = this.cardData.expiryDate || '';
            this.cvvInput.value = this.cardData.cvv || '';
            this.cardHolderInput.value = this.cardData.cardHolder || '';
            this.termsCheckbox.checked = this.cardData.terms || false;
        }
    }

    validateCardNumber(showFullError = false) {
        const cardNumber = this.cardNumberInput.value.replace(/\s/g, '').trim();
        const formGroup = this.cardNumberInput.closest('.form-group');
        const errorContainer = formGroup.querySelector('.error-message') || this.createErrorContainer(formGroup);

        // Resetting states
        formGroup.classList.remove('form-group--error', 'form-group--success');
        errorContainer.style.display = 'none';

        if (!cardNumber) {
            if (showFullError) {
                this.showError(formGroup, errorContainer, 'Card Number cannot be empty');
            }
            this.fieldStates.cardNumber = false;
            return false;
        }

        if (!/^\d+$/.test(cardNumber)) {
            if (showFullError) {
                this.showError(formGroup, errorContainer, 'Card number must contain only digits');
            }
            this.fieldStates.cardNumber = false;
            return false;
        }

        if (cardNumber.length !== 16) {
            if (showFullError) {
                this.showError(formGroup, errorContainer, 'Card number must be 16 digits');
            }
            this.fieldStates.cardNumber = false;
            return false;
        }

        if (!this.luhnCheck(cardNumber)) {
            if (showFullError) {
                this.showError(formGroup, errorContainer, 'Invalid card number. Please check and try again');
            }
            this.fieldStates.cardNumber = false;
            return false;
        }

        // Valid card number
        formGroup.classList.add('form-group--success');
        this.fieldStates.cardNumber = true;
        this.updateVerifyButtonState();
        return true;
    }

    validateExpiryDate(showFullError = false) {
        const expiryDate = this.expiryDateInput.value.trim();
        const formGroup = this.expiryDateInput.closest('.form-group');
        const errorContainer = formGroup.querySelector('.error-message') || this.createErrorContainer(formGroup);

        // Resetting states
        formGroup.classList.remove('form-group--error', 'form-group--success');
        errorContainer.style.display = 'none';

        if (!expiryDate) {
            if (showFullError) {
                this.showError(formGroup, errorContainer, 'Expiry date cannot be empty');
            }
            this.fieldStates.expiryDate = false;
            return false;
        }

        // Ensuring format is MM/YY
        if (!/^\d{2}\/\d{2}$/.test(expiryDate)) {
            if (showFullError) {
                this.showError(formGroup, errorContainer, 'Invalid format! Use MM/YY');
            }
            this.fieldStates.expiryDate = false;
            return false;
        }

        // Extracting month and year
        try {
            const [month, yearStr] = expiryDate.split('/');
            const monthNum = parseInt(month, 10);
            const yearNum = parseInt(yearStr, 10) + 2000; // Converting YY to YYYY format

            if (monthNum < 1 || monthNum > 12) {
                if (showFullError) {
                    this.showError(formGroup, errorContainer, 'Month must be between 01 and 12');
                }
                this.fieldStates.expiryDate = false;
                return false;
            }

            const currentDate = new Date();
            const currentMonth = currentDate.getMonth() + 1; // getMonth() is 0-based
            const currentYear = currentDate.getFullYear();

            if (yearNum < currentYear || (yearNum === currentYear && monthNum < currentMonth)) {
                if (showFullError) {
                    this.showError(formGroup, errorContainer, 'Card has expired');
                }
                this.fieldStates.expiryDate = false;
                return false;
            }
        } catch (e) {
            if (showFullError) {
                this.showError(formGroup, errorContainer, 'Invalid expiry date format');
            }
            this.fieldStates.expiryDate = false;
            return false;
        }

        // Valid expiry date
        formGroup.classList.add('form-group--success');
        this.fieldStates.expiryDate = true;
        this.updateVerifyButtonState();
        return true;
    }

    validateCvv(showFullError = false) {
        const cvv = this.cvvInput.value.trim();
        const formGroup = this.cvvInput.closest('.form-group');
        const errorContainer = formGroup.querySelector('.error-message') || this.createErrorContainer(formGroup);

        // Resetting states
        formGroup.classList.remove('form-group--error', 'form-group--success');
        errorContainer.style.display = 'none';

        if (!cvv) {
            if (showFullError) {
                this.showError(formGroup, errorContainer, 'CVV cannot be empty');
            }
            this.fieldStates.cvv = false;
            return false;
        }

        if (!/^\d+$/.test(cvv)) {
            if (showFullError) {
                this.showError(formGroup, errorContainer, 'CVV must contain only numbers');
            }
            this.fieldStates.cvv = false;
            return false;
        }

        // Ensuring CVV length is either 3 or 4 digits
        if (!/^\d{3,4}$/.test(cvv)) {
            if (showFullError) {
                this.showError(formGroup, errorContainer, 'CVV must be 3 or 4 digits');
            }
            this.fieldStates.cvv = false;
            return false;
        }

        // Valid CVV
        formGroup.classList.add('form-group--success');
        this.fieldStates.cvv = true;
        this.updateVerifyButtonState();
        return true;
    }

    validateCardHolder(showFullError = false) {
        const cardHolder = this.cardHolderInput.value.trim();
        const formGroup = this.cardHolderInput.closest('.form-group');
        const errorContainer = formGroup.querySelector('.error-message') || this.createErrorContainer(formGroup);

        // Resetting states
        formGroup.classList.remove('form-group--error', 'form-group--success');
        errorContainer.style.display = 'none';

        if (!cardHolder) {
            if (showFullError) {
                this.showError(formGroup, errorContainer, 'Cardholder name cannot be empty');
            }
            this.fieldStates.cardHolder = false;
            return false;
        }

        // Ensuring name contains only letters and spaces
        if (!/^[A-Za-z ]+$/.test(cardHolder)) {
            if (showFullError) {
                this.showError(formGroup, errorContainer, 'Name must contain only letters and spaces');
            }
            this.fieldStates.cardHolder = false;
            return false;
        }

        // Ensuring at least two words (first and last name)
        if (cardHolder.split(/\s+/).filter(word => word.length > 0).length < 2) {
            if (showFullError) {
                this.showError(formGroup, errorContainer, 'Please enter full name (first & last)');
            }
            this.fieldStates.cardHolder = false;
            return false;
        }

        // Ensuring name is within a reasonable length
        if (cardHolder.length < 3 || cardHolder.length > 50) {
            if (showFullError) {
                this.showError(formGroup, errorContainer, 'Name must be between 3 and 50 characters');
            }
            this.fieldStates.cardHolder = false;
            return false;
        }

        // Valid card holder name
        formGroup.classList.add('form-group--success');
        this.fieldStates.cardHolder = true;
        this.updateVerifyButtonState();
        return true;
    }

    validateTerms() {
        const isChecked = this.termsCheckbox.checked;

        if (!isChecked) {
            this.termsError.style.display = 'flex';
            this.fieldStates.terms = false;
        } else {
            this.termsError.style.display = 'none';
            this.fieldStates.terms = true;
        }

        this.updateVerifyButtonState();
        return isChecked;
    }

    validateVerificationCode(showFullError = false) {
        // Skipping validation if verification hasn't been sent
        if (!this.verificationCodeSent) return true;

        const code = this.verificationCodeInput.value.trim();
        const codeGroup = this.verificationCodeInput.closest('.verification-code');
        const errorContainer = codeGroup.querySelector('.error-message') || this.createErrorContainer(codeGroup);

        // Resetting error state
        errorContainer.style.display = 'none';

        if (!code) {
            if (showFullError) {
                this.showError(codeGroup, errorContainer, 'Verification code cannot be empty');
            }
            this.fieldStates.verificationCode = false;
            return false;
        }

        if (!/^\d{6}$/.test(code)) {
            if (showFullError) {
                this.showError(codeGroup, errorContainer, 'Code must be 6 digits');
            }
            this.fieldStates.verificationCode = false;
            return false;
        }

        // Valid verification code
        this.fieldStates.verificationCode = true;
        this.updateConfirmButtonState();
        return true;
    }

    validateAllCardFields() {
        const isCardNumberValid = this.validateCardNumber(true);
        const isExpiryDateValid = this.validateExpiryDate(true);
        const isCvvValid = this.validateCvv(true);
        const isCardHolderValid = this.validateCardHolder(true);
        const isTermsChecked = this.validateTerms();

        return isCardNumberValid && isExpiryDateValid && isCvvValid && isCardHolderValid && isTermsChecked;
    }

    updateVerifyButtonState() {
        const allValid =
            this.fieldStates.cardNumber &&
            this.fieldStates.expiryDate &&
            this.fieldStates.cvv &&
            this.fieldStates.cardHolder &&
            this.fieldStates.terms;

        this.verifyPaymentButton.disabled = !allValid;

        // Applying visual states
        if (allValid) {
            this.verifyPaymentButton.classList.add('btn-active');
            this.verifyPaymentButton.classList.remove('btn-disabled');
        } else {
            this.verifyPaymentButton.classList.remove('btn-active');
            this.verifyPaymentButton.classList.add('btn-disabled');
        }
    }

    updateConfirmButtonState() {
        const isValid = this.fieldStates.verificationCode;
        this.confirmPaymentButton.disabled = !isValid;

        // Applying visual states
        if (isValid) {
            this.confirmPaymentButton.classList.add('btn-active');
            this.confirmPaymentButton.classList.remove('btn-disabled');
        } else {
            this.confirmPaymentButton.classList.remove('btn-active');
            this.confirmPaymentButton.classList.add('btn-disabled');
        }
    }

    createErrorContainer(parentElement) {
        const errorContainer = document.createElement('div');
        errorContainer.className = 'error-message';

        const errorIcon = document.createElement('span');
        errorIcon.className = 'material-icons error-icon';
        errorIcon.textContent = 'error_outline';

        const errorText = document.createElement('span');
        errorText.className = 'error-text';

        errorContainer.appendChild(errorIcon);
        errorContainer.appendChild(errorText);
        parentElement.appendChild(errorContainer);

        return errorContainer;
    }

    showError(formGroup, errorContainer, message) {
        formGroup.classList.add('form-group--error');
        formGroup.classList.remove('form-group--success');

        const errorText = errorContainer.querySelector('.error-text');
        if (errorText) {
            errorText.textContent = message;
        }

        errorContainer.style.display = 'flex';

        // Adding subtle animation to error message
        errorContainer.style.animation = 'errorShake 0.4s ease-in-out';
        setTimeout(() => {
            errorContainer.style.animation = '';
        }, 400);
    }

    luhnCheck(cardNumber) {
        let sum = 0;
        let shouldDouble = false;

        // Looping through values starting from the rightmost digit
        for (let i = cardNumber.length - 1; i >= 0; i--) {
            let digit = parseInt(cardNumber.charAt(i));

            if (shouldDouble) {
                digit *= 2;
                if (digit > 9) {
                    digit -= 9;
                }
            }

            sum += digit;
            shouldDouble = !shouldDouble;
        }

        return (sum % 10) === 0;
    }

    // UNIFIED FUNCTION for sending and resending verification codes
    handleVerificationCode(isResend = false) {
        // Determine which button to update with loading state
        const button = isResend ? this.resendCodeButton : this.verifyPaymentButton;

        if (!button) {
            console.error(`Button not found: ${isResend ? 'resendCodeButton' : 'verifyPaymentButton'}`);
            return;
        }

        const originalButtonHtml = button.innerHTML;

        // Display loading state in the button
        button.disabled = true;
        button.innerHTML = `
            <span class="material-icons button-icon loading">pending</span> ${isResend ? 'Sending...' : 'Sending Code...'}
        `;
        this.animateLoadingIcon(button.querySelector('.loading'));

        // Making AJAX request to send verification code (same endpoint for both send and resend)
        fetch(`/dashboard/user_home/${userId}/card_details/subscription/verification_code/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to send verification code');
            }
            return response.json();
        })
        .then(data => {
            // Marking verification code as sent
            this.verificationCodeSent = true;

            // Showing success message - using the exact message from backend
            this.showMessage('A verification code has been sent to your email!', 'success');

            if (!isResend) {
                // Only transition to verification section on initial send, not resend
                this.transitionToVerificationSection();
            } else {
                // For resend, reset the verification code input and focus it
                if (this.verificationCodeInput) {
                    this.verificationCodeInput.value = '';
                    this.fieldStates.verificationCode = false;
                    this.updateConfirmButtonState();
                    this.verificationCodeInput.focus();
                }
            }

            // Starting the resend timer for both initial send and resend
            this.startResendTimer(59); // 59 seconds timer
        })
        .catch(error => {
            console.error('Error:', error);
            this.showMessage('Failed to send verification code. Please try again.', 'error');
        })
        .finally(() => {
            // Resetting button state
            button.disabled = false;
            button.innerHTML = originalButtonHtml;

            if (!isResend) {
                this.updateVerifyButtonState();
            }
        });
    }

    transitionToVerificationSection() {
        // Setup transitions
        this.cardDetailsSection.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        this.verificationSection.style.transition = 'opacity 0.5s ease, transform 0.5s ease';

        // First step: start fading out card details and prepare verification section
        this.cardDetailsSection.style.opacity = '0.5';
        this.cardDetailsSection.style.transform = 'translateX(-20px)';

        // Storing card data before transition
        this.storeCardData();

        setTimeout(() => {
            // Second step: disabling card details completely and prepare verification section
            this.disableCardDetailsSection();

            this.verificationSection.style.transform = 'translateY(20px)';
            this.verificationSection.style.opacity = '0';
            this.verificationSection.style.pointerEvents = 'auto';

            // Enabling verification inputs
            const verificationInputs = this.verificationSection.querySelectorAll('input');
            verificationInputs.forEach(input => input.disabled = false);
            this.confirmPaymentButton.disabled = true;
            this.cancelVerificationButton.disabled = false;

            // Third step: animating in the verification section
            setTimeout(() => {
                this.verificationSection.style.opacity = '1';
                this.verificationSection.style.transform = 'translateY(0)';
                this.verificationSection.classList.remove('disabled-section');

                // Focusing on the verification code input
                if (this.verificationCodeInput) {
                    this.verificationCodeInput.focus();
                }
            }, 150);
        }, 300);
    }

    transitionToCardDetailsSection() {
        // Setup transitions
        this.cardDetailsSection.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        this.verificationSection.style.transition = 'opacity 0.5s ease, transform 0.5s ease';

        // First step: start fading out verification section
        this.verificationSection.style.opacity = '0.5';
        this.verificationSection.style.transform = 'translateY(20px)';

        setTimeout(() => {
            // Second step: disable verification section
            this.disableVerificationSection();

            // Third step: animate in the card details section
            this.cardDetailsSection.style.opacity = '1';
            this.cardDetailsSection.style.transform = 'translateX(0)';

            // Enabling card inputs
            const cardInputs = this.cardDetailsSection.querySelectorAll('input');
            cardInputs.forEach(input => input.disabled = false);
            this.verifyPaymentButton.disabled = false;
            this.updateVerifyButtonState();
            this.cardDetailsSection.style.pointerEvents = 'auto';

            // Resetting verification code state
            this.verificationCodeSent = false;

            // Clearing any running timer
            if (this.resendTimerInterval) {
                clearInterval(this.resendTimerInterval);
                this.resendTimerInterval = null;
            }

            // Restoring card data to form fields
            this.restoreCardData();
        }, 300);
    }

    disableCardDetailsSection() {
        this.cardDetailsSection.classList.add('disabled-section');
        this.cardDetailsSection.style.pointerEvents = 'none';

        // Disabling all inputs
        const inputs = this.cardDetailsSection.querySelectorAll('input, button');
        inputs.forEach(input => input.disabled = false);
    }

    disableVerificationSection() {
        this.verificationSection.classList.add('disabled-section');
        this.verificationSection.style.opacity = '0.5';
        this.verificationSection.style.pointerEvents = 'none';

        // Disabling all inputs
        const inputs = this.verificationSection.querySelectorAll('input, button');
        inputs.forEach(input => input.disabled = true);
    }

    // Updated to accept custom duration parameter
    startResendTimer(duration = 59) {
        let timeLeft = duration;

        // Resetting any existing timer
        if (this.resendTimerInterval) {
            clearInterval(this.resendTimerInterval);
        }

        // Showing timer, hide resend form
        if (this.timerElement) this.timerElement.style.display = 'block';
        if (this.resendForm) this.resendForm.style.display = 'none';

        // Updating timer text
        if (this.timerDisplay) {
            this.timerDisplay.textContent = timeLeft;
            this.timerDisplay.style.color = '';
        }

        this.resendTimerInterval = setInterval(() => {
            timeLeft--;

            if (this.timerDisplay) {
                this.timerDisplay.textContent = timeLeft;

                // Adding visual feedback when time is running low
                if (timeLeft <= 10) {
                    this.timerDisplay.style.color = '#f44336';
                    this.timerDisplay.style.fontWeight = 'bold';
                }
            }

            if (timeLeft <= 0) {
                clearInterval(this.resendTimerInterval);

                if (this.timerElement) {
                    this.timerElement.style.display = 'none';

                    // Resetting timer display styling
                    if (this.timerDisplay) {
                        this.timerDisplay.style.color = '';
                        this.timerDisplay.style.fontWeight = '';
                    }
                }

                if (this.resendForm) {
                    // Adding fade-in animation for resend button
                    this.resendForm.style.opacity = '0';
                    this.resendForm.style.display = 'block';

                    // IMPORTANT: Make sure the button is enabled
                    if (this.resendCodeButton) {
                        this.resendCodeButton.disabled = false;
                        console.log('Resend button enabled');
                    }

                    setTimeout(() => {
                        this.resendForm.style.transition = 'opacity 0.3s ease';
                        this.resendForm.style.opacity = '1';
                    }, 10);
                }
            }
        }, 1000);
    }

    // Optimized message handling system
    showMessage(message, type) {
        // Clearing any existing timeout
        if (this.messageTimeout) {
            clearTimeout(this.messageTimeout);
        }

        // Finding or create messages container
        let messagesContainer = document.querySelector('.messages');
        if (!messagesContainer) {
            messagesContainer = document.createElement('div');
            messagesContainer.className = 'messages';
            messagesContainer.setAttribute('role', 'alert');
            messagesContainer.setAttribute('aria-live', 'polite');
            document.querySelector('.checkout-container').insertBefore(messagesContainer, document.querySelector('.checkout-container').firstChild);
        }

        // Clearing existing messages
        messagesContainer.innerHTML = '';

        // Creating new message
        const messageElement = document.createElement('div');
        messageElement.className = `message message--${type}`;

        // Adding icon based on message type
        const icon = document.createElement('span');
        icon.className = 'material-icons message-icon';
        icon.textContent = type === 'success' ? 'check_circle' : 'error_outline';

        // Adding message text
        const messageText = document.createElement('span');
        messageText.className = 'message-text';
        messageText.textContent = message;

        // Assembling message element
        messageElement.appendChild(icon);
        messageElement.appendChild(messageText);
        messagesContainer.appendChild(messageElement);

        // Sliding in animation
        messageElement.style.transform = 'translateY(-20px)';
        messageElement.style.opacity = '0';

        setTimeout(() => {
            messageElement.style.transition = 'transform 0.3s ease, opacity 0.3s ease';
            messageElement.style.transform = 'translateY(0)';
            messageElement.style.opacity = '1';
        }, 10);

        // Auto-hide message after 5 seconds
        this.messageTimeout = setTimeout(() => {
            messageElement.style.transform = 'translateY(-20px)';
            messageElement.style.opacity = '0';

            // Removing message after animation completes
            setTimeout(() => {
                if (messagesContainer.contains(messageElement)) {
                    messagesContainer.removeChild(messageElement);
                }
            }, 300);
        }, 5000);
    }

    handleAutoHideMessages() {
        // Finding any existing messages and add auto-hide behavior
        const messages = document.querySelectorAll('.message');
        messages.forEach(message => {
            setTimeout(() => {
                message.style.transition = 'transform 0.3s ease, opacity 0.3s ease';
                message.style.transform = 'translateY(-20px)';
                message.style.opacity = '0';

                // Removing message after animation completes
                setTimeout(() => {
                    if (message.parentNode) {
                        message.parentNode.removeChild(message);
                    }
                }, 300);
            }, 5000);
        });
    }

    animateLoadingIcon(iconElement) {
        if (!iconElement) return;

        // Adding rotation animation
        iconElement.style.animation = 'spin 1.5s linear infinite';
    }

    addCustomStyles() {
        // Adding any custom styles needed for animations
        const styleSheet = document.createElement('style');
        styleSheet.innerHTML = `
            @keyframes errorShake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-5px); }
                75% { transform: translateX(5px); }
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .form-group--success input {
                border-color: #4CAF50 !important;
            }

            .form-group--error input {
                border-color: #f44336 !important;
            }

            .error-message {
                display: none;
                align-items: center;
                color: #f44336;
                margin-top: 5px;
                font-size: 0.8rem;
            }

            .error-icon {
                font-size: 16px;
                margin-right: 4px;
            }

            .loading {
                display: inline-block;
            }

            .message {
                display: flex;
                align-items: center;
                padding: 12px 16px;
                margin-bottom: 15px;
                border-radius: 4px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }

            .message--success {
                background-color: #e8f5e9;
                color: #2e7d32;
            }

            .message--error {
                background-color: #fdecea;
                color: #d32f2f;
            }

            .message-icon {
                margin-right: 8px;
                font-size: 20px;
            }
        `;
        document.head.appendChild(styleSheet);
    }
    }

    // Initializing the payment verification system when the DOM is loaded
    document.addEventListener('DOMContentLoaded', () => {

        // Adding a small delay to ensure all elements are properly initialized
        setTimeout(() => {
            window.paymentVerification = new EnhancedPaymentVerification();
            console.log('Payment verification system initialized');
        }, 100);

    });
