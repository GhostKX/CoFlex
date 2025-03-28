import re
from django import forms
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from django.utils.timezone import now
from ..models import (VerifiedUsers)
from CoFlex_Staff_app.models import StaffAccounts


class UserLoginForm(forms.Form):
    """
        Login Form for authenticating users and staff members.
    """

    email = forms.EmailField(widget=forms.EmailInput(), required=True, label='Email')
    password = forms.CharField(widget=forms.PasswordInput(), required=True, label='Password')

    class Meta:
        fields = ['email', 'password']
        widgets = {
            'password': forms.PasswordInput,
            'email': forms.EmailInput,
        }

    # Validation of the email field
    def clean_email(self):
        email = self.cleaned_data.get('email')
        email = email.strip()
        if not email:
            raise forms.ValidationError('Email cannot be empty!')

        pattern = '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'

        if pattern and not re.match(pattern, email):
            raise forms.ValidationError("Enter a valid email address!")

        try:
            user = StaffAccounts.objects.get(email=email)
            self.cleaned_data['user'] = user
            self.cleaned_data['user_type'] = 'staff'
            return email
        except StaffAccounts.DoesNotExist:
            pass

        # Checking if user with the email exists
        try:
            user = VerifiedUsers.objects.get(email=email)
            self.cleaned_data['user'] = user
            self.cleaned_data['user_type'] = 'user'

            if not user.is_active:
                days_since_deletion = (now() - user.user_account_deletion.deletion_time).days

                restore_link = reverse('restore_account')
                raise forms.ValidationError(
                    f'Your account has been deleted! You can restore it within next {30 - days_since_deletion} days.'
                    f' <a href="{restore_link}">Click here</a> to restore your account.')

            return email
        except VerifiedUsers.DoesNotExist:
            raise forms.ValidationError('No user found with this email!')

    # Validation of the password field
    def clean_password(self):
        password = self.cleaned_data.get('password').strip()
        if not password:
            raise forms.ValidationError('Password cannot be empty!')

        user = self.cleaned_data.get('user')

        # Checking if the password matches the user's stored password
        if user and check_password(password, user.password):
            return password
        else:
            raise forms.ValidationError('Incorrect password! Please try again.')
