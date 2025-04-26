import re
from django import forms
from django.utils.timezone import now
from cryptography.fernet import Fernet
from django.conf import settings
from ..models import SubscribedUsers, SubscribedUserCardDetails, SubscribedUsersVerificationCode


class VerifiedUserCardDetails_SubscribedUsersVerificationCode_Forms(forms.Form):
    """
        Form for users to enter their payment card details and verification code.

        card_number: Field for the credit/debit card number.
        expiry_date: Expiry date in MM/YY format.
        cvv: 3 or 4-digit CVV security code.
        card_holder_name: Full name as it appears on the card.
        verification_code: 6-digit code sent to the user.
    """

    card_number = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Card number (16 digits)'}),
        required=True,
        label='Card number')
    expiry_date = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'MM/YY'}),
        required=True,
        label='Expiry date')
    cvv = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'cvv'}),
        required=True,
        label='CVV')
    card_holder_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Cardholder Name'}),
        required=True,
        label='Cardholder Name'
    )
    verification_code = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Verification Code'}),
        max_length=6,
        required=True,
        label='Verification Code'
    )

    # Passing the user as an instance for the further validation
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    # Validation for the card number
    def clean_card_number(self):
        card_number = self.cleaned_data.get('card_number', '').strip()

        if not card_number:
            raise forms.ValidationError('Card Number can not be empty!')

        # Remove any spaces or dashes
        card_number = card_number.replace(' ', '').replace('-', '')

        if not card_number.isdigit():
            raise forms.ValidationError('Card number must contain only digits!')

        if not re.match(r'^\d{16}$', card_number):
            raise forms.ValidationError('Invalid card number. Please enter a valid card number.')

        if not self.luhn_check(card_number):
            raise forms.ValidationError('Invalid card number. Please check and try again.')

        print(card_number)

        return card_number

    # Luhn Algorithm check for card number validity.
    def luhn_check(self, card_number):
        """Validates a card number using the Luhn Algorithm."""
        total = 0
        reverse_digits = card_number[::-1]

        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:  # Doubling every second digit
                n *= 2
                if n > 9:
                    n -= 9  # Subtracting 9 if the number is greater than 9
            total += n

        return total % 10 == 0

    # Validation for the card number's expiry date
    def clean_expiry_date(self):
        expiry_date = self.cleaned_data.get('expiry_date').strip()

        if not expiry_date:
            raise forms.ValidationError('Expiry date can not be empty!')

        # Ensure format is MM/YY
        if not re.match(r'^\d{2}/\d{2}$', expiry_date):
            raise forms.ValidationError('Invalid format! Expiry date must be in MM/YY format.')

        # Extract month and year
        try:
            month, year = expiry_date.split('/')
            month = int(month)
            year = int(year) + 2000  # Convert YY to YYYY format
        except ValueError:
            raise forms.ValidationError('Invalid expiry date format!')

        if month < 1 or month > 12:
            raise forms.ValidationError('Invalid month! It should be between 01 and 12.')

        current_month = now().month
        current_year = now().year

        if current_year > year or (current_year == year and current_month > month):
            raise forms.ValidationError('Your card has expired. Please use a valid expiry date.')

        print(expiry_date)

        return expiry_date

    # Validation for the card number's cvv code
    def clean_cvv(self):
        cvv = self.cleaned_data.get('cvv')

        if not cvv:
            raise forms.ValidationError('CVV can not be empty!')

        if not cvv.isdigit():
            raise forms.ValidationError('CVV must contain only numbers!')

        # Ensure CVV length is either 3 or 4 digits
        if not re.match(r'^\d{3,4}$', cvv):
            raise forms.ValidationError('Invalid CVV! It must be 3 or 4 digits.')

        print(cvv)

        return cvv

    # Validation for the card number's cardholder Name
    def clean_card_holder_name(self):
        card_holder_name = self.cleaned_data.get('card_holder_name', '').strip()

        if not card_holder_name:
            raise forms.ValidationError('Cardholder Name can not be empty')

        # Remove extra spaces between words
        card_holder_name = re.sub(r'\s+', ' ', card_holder_name)

        # Ensure name contains only letters and spaces
        if not re.match(r'^[A-Za-z ]+$', card_holder_name):
            raise forms.ValidationError('Cardholder name must contain only letters and spaces!')

        # Ensure at least two words (first and last name)
        if len(card_holder_name.split()) < 2:
            raise forms.ValidationError('Please enter the full name (first and last name).')

        # Ensure name is within a reasonable length
        if len(card_holder_name) < 3 or len(card_holder_name) > 50:
            raise forms.ValidationError('Cardholder name must be between 3 and 50 characters.')

        print(card_holder_name)

        return card_holder_name

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code')

        # Fetching the verification entry for the user
        verification_entry = SubscribedUsersVerificationCode.objects.filter(user=self.user).first()

        if not verification_entry:
            raise forms.ValidationError('No verification code found for this user.')

        if verification_entry.is_expired():
            raise forms.ValidationError('The verification code has expired!')

        f_code = Fernet(settings.FERNET_KEY_VERIFICATION_CODE)
        db_verification_code = (f_code.decrypt(verification_entry.verification_code.encode())).decode()

        if db_verification_code != verification_code:
            raise forms.ValidationError('Invalid verification code.')

        print(verification_code)

        return verification_code

    # Validation for the form
    def clean(self):
        cleaned_data = super().clean()
        if SubscribedUsers.objects.filter(user=self.user, is_subscribed=True, is_active=True).exists():
            raise forms.ValidationError('This user already has an active subscription.')

        print(cleaned_data)
        return cleaned_data



