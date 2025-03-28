import re
from django import forms
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy
from ..models import (VerifiedUsers, VerifiedUsersPasswordVerificationCode)


class UserForgotPasswordEmailForm(forms.Form):
    """
       Form for users to request a password reset via email.
    """
    email = forms.EmailField(widget=forms.EmailInput(), required=True, label='Email')

    class Meta:
        fields = ['email']
        widgets = {
            'email': forms.EmailInput,
        }

    # Validation for the email field
    def clean_email(self):
        email = self.cleaned_data.get('email').strip()
        if not email:
            raise forms.ValidationError('Email cannot be empty!')

        pattern = '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'

        if pattern and not re.match(pattern, email):
            raise forms.ValidationError("Enter a valid email address!")

        # Checking if user with this email exists
        try:
            user = VerifiedUsers.objects.get(email=email)
        except Exception as e:
            print(e)
            raise forms.ValidationError('No user found with this email!')

        self.cleaned_data['user'] = user

        return email


class UserForgotPasswordVerificationCodeForm(forms.Form):
    """
        Form for users to verify their identity using a verification code.
    """

    verification_code = forms.CharField(max_length=6, required=True)

    # Storing the user instance
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    # Validation for the Verification code field
    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code')

        verification_entry = VerifiedUsersPasswordVerificationCode.objects.filter(user=self.user).first()

        if not verification_entry:
            raise forms.ValidationError('No verification code found for this user.')

        if verification_entry.is_expired():
            raise forms.ValidationError('The verification code has expired!')

        if verification_entry.verification_code != verification_code:
            raise forms.ValidationError('Invalid verification code.')

        return verification_code


class UserForgotPasswordResetPasswordForm(forms.ModelForm):
    """
       Form for users to reset their password after verification.
    """

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': gettext_lazy('Enter your new password')}),
        required=True,
        label=gettext_lazy('New Password'),
        help_text=gettext_lazy('Your password must be at least 8 characters long, and not entirely numeric.'),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': gettext_lazy('Confirm your new password')}),
        required=True,
        label=gettext_lazy('Confirm Password'),
    )

    class Meta:
        model = VerifiedUsers
        fields = []

    # Validation of the form's fields
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        # Ensuring both passwords are provided
        if not password1 or not password2:
            raise forms.ValidationError(gettext_lazy('Both password fields are required.'))

        # Ensuring passwords match
        if password1 != password2:
            self.add_error('password2', gettext_lazy('Passwords do not match.'))

        return cleaned_data

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        # Password strength check
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not re.match(pattern, password1):
            raise forms.ValidationError(
                gettext_lazy("Password must be at least 8 characters long and include at least: "
                  "one uppercase letter, one lowercase letter, one digit, and one special character.")
            )

        # Django's built-in password validators to check for the common passwords
        try:
            validate_password(password1)
        except forms.ValidationError as e:
            raise forms.ValidationError(e.messages)

        return password1
