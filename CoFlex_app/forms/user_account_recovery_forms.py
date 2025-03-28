import re
from django import forms
from django.utils.timezone import now
from ..models import (VerifiedUsers, UserAccountRestoration, UserAccountRecoveryCode)


class UserRestoreAccountForm(forms.ModelForm):
    """
        Form for users to request account restoration.

        restoration_email: Email associated with the deleted account.
        restoration_details: Reason for requesting account restoration.
     """

    restoration_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email...'}),
        required=True,
        label='Email'
    )
    restoration_details = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Why do you want to restore your account?'}),
        max_length=250,
        required=True,
        label='Reason for restoration'
    )

    class Meta:
        model = UserAccountRestoration
        fields = ['restoration_email', 'restoration_details']

    # Validation for the email
    def clean_restoration_email(self):
        restoration_email = self.cleaned_data.get('restoration_email').strip()
        if not restoration_email:
            raise forms.ValidationError('Email can not be empty!')

        pattern = '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'

        if not re.match(pattern, restoration_email):
            raise forms.ValidationError("Enter a valid email address!")

        checking_user = VerifiedUsers.objects.filter(email=restoration_email).first()
        if not checking_user:
            raise forms.ValidationError("No account found with this email!")

        if checking_user.is_active:
            raise forms.ValidationError('This email is already registered and active!')

        if not checking_user.user_account_deletion.is_deleted:
            raise forms.ValidationError("No deletion record found for this user!")

        deletion_time = now() - checking_user.user_account_deletion.deletion_time
        hours_passed = deletion_time.total_seconds() // 3600

        days_passed = deletion_time.days
        days_left = 30 - days_passed

        if hours_passed < 24:
            raise forms.ValidationError(
                f'You can only restore your account 24 hours after deletion. '
                f'Please wait {int(24 - hours_passed)} more hours before trying again.'
            )

        if days_passed > 30:
            raise forms.ValidationError(
                "The restoration period has expired. You can no longer restore this account.")

        if checking_user.user_account_deletion.is_blocked:
            raise forms.ValidationError(
                f'Your account has been blocked! You must wait {days_left} more days before reactivating. Please contact support'
            )

        return restoration_email

    # Validation for the details
    def clean_restoration_details(self):
        restoration_details = self.cleaned_data.get('restoration_details').strip()
        if not restoration_details:
            raise forms.ValidationError('This field can not be empty!')

        if len(restoration_details) >= 250:
            raise forms.ValidationError('You have exceeded maximum number of characters!')

        return restoration_details


class UserRestoreAccountCodeForm(forms.Form):
    """
        Form to validate the user's account restoration verification code.

        verification_code: 6-digit code sent to the user's email.
    """
    verification_code = forms.CharField(max_length=6, required=True)

    # Passing the user as an instance to use in the validation
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    # Validation for the verification code field
    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code')

        verification_entry = UserAccountRecoveryCode.objects.filter(user=self.user).first()

        if not verification_entry:
            raise forms.ValidationError('No verification code found for this user.')

        if verification_entry.is_expired():
            raise forms.ValidationError('The verification code has expired!')

        if verification_entry.verification_code != verification_code:
            raise forms.ValidationError('Invalid verification code.')

        return verification_code
