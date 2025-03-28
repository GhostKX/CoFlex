import re
from django import forms
from ..models import (VerifiedUsers, UserExtraContactDetails, UserEditMainEmail)


class UserEditMainEmailForm(forms.Form):
    """
        A form to update the user's main email address.
    """

    new_email = forms.EmailField(widget=forms.EmailInput(), required=True, label='New Email')
    confirm_email = forms.EmailField(widget=forms.EmailInput(), required=True, label='Confirm New Email')

    class Meta:
        fields = ['new_email', 'confirm_email']
        widgets = {
            'new_email': forms.EmailInput,
            'confirm_email': forms.EmailInput,
        }

    # Storing user instance
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    # Validation for the form's fields
    def clean(self):
        cleaned_data = super().clean()
        new_email = self.cleaned_data.get('new_email', '').strip()
        confirm_email = self.cleaned_data.get('confirm_email', '').strip()

        if not new_email:
            raise forms.ValidationError('Email field should not be empty!')

        if not confirm_email:
            raise forms.ValidationError('Email field should not be empty!')

        if new_email != confirm_email:
            raise forms.ValidationError('The new email fields do not match!')

        pattern = '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'

        if pattern and not re.match(pattern, new_email):
            raise forms.ValidationError("Enter a valid email address!")

        second_email_table = UserExtraContactDetails.objects.filter(second_email=new_email).first()
        if second_email_table and second_email_table.second_email:
            raise forms.ValidationError('An email is already in use!')

        if self.user and self.user.email == new_email:
            raise forms.ValidationError('The new email address cannot be the same as your current email!')

        email_check = VerifiedUsers.objects.exclude(email=self.user.email).filter(email=new_email).first()
        if email_check:
            raise forms.ValidationError('This email address is already registered with another account!')

        return cleaned_data


class UserEditMainEmailCodeForm(forms.Form):
    """
        A form for verifying the email change using a verification code.
    """

    verification_code = forms.CharField(max_length=6, required=True)

    # Storing the user instance
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    # Validation of the verification code field
    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code')

        verification_entry = UserEditMainEmail.objects.filter(user=self.user).first()

        if not verification_entry:
            raise forms.ValidationError('No verification code found for this user.')

        if verification_entry.is_expired():
            raise forms.ValidationError('The verification code has expired!')

        if verification_entry.verification_code != verification_code:
            raise forms.ValidationError('Invalid verification code.')

        return verification_code
