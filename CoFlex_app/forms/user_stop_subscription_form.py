from django import forms
from django.contrib.auth.hashers import check_password
from django.utils.translation import gettext_lazy
import re


class UserStopSubscriptionForm(forms.Form):
    """
        Form for user account deletion:

        password1: User's current password for verification
        password2: Confirmation field to ensure correctness
    """

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': gettext_lazy('Enter your password')}),
        required=True,
        label=gettext_lazy('Password'),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': gettext_lazy('Confirm your password')}),
        required=True,
        label=gettext_lazy('Confirm Password'),
    )

    # Storing the user instance
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    # Validation for the password fields
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

    # Validation for the Password1 field
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        # Password strength validation
        if len(password1) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')

        if not re.search(r'[A-Z]', password1):
            raise forms.ValidationError('Password must contain at least one uppercase letter.')

        if not re.search(r'[a-z]', password1):
            raise forms.ValidationError('Password must contain at least one lowercase letter.')

        if not re.search(r'\d', password1):
            raise forms.ValidationError('Password must contain at least one digit.')

        if not re.search(r'[!@#$%^&*()\-_+=\[\]{}|;:\'",.<>?/]', password1):
            raise forms.ValidationError('Password must contain at least one special character.')

        # Check if the password matches the user's stored password
        if self.user and check_password(password1, self.user.password):
            return password1
        else:
            raise forms.ValidationError('Incorrect password! Please try again.')


