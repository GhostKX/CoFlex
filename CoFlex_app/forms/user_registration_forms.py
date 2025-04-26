import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy
from ..models import (UnverifiedUsers, UnverifiedUsersVerificationCode,
                      VerifiedUsers, Profile, UserAccountDeletion)


class BaseUserForm(UserCreationForm):
    """
        Form for the user registration
    """

    first_name = forms.CharField(max_length=150, required=True, label='First Name')
    last_name = forms.CharField(max_length=150, required=True, label='Last Name')
    email = forms.EmailField(widget=forms.EmailInput(), required=True, label='Email')
    password1 = forms.CharField(widget=forms.PasswordInput(), required=True, label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput(), required=True, label='Confirm Password')

    class Meta:
        model = UnverifiedUsers
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'password1': forms.PasswordInput,
            'password2': forms.PasswordInput,
            'email': forms.EmailInput,
        }

    # Validation of the user first name field
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        first_name = first_name.strip().capitalize()
        if not first_name:
            raise forms.ValidationError('First Name can not be empty!')

        if not first_name.isalpha():
            raise forms.ValidationError('First Name must contain only letters')

        return first_name

    # Validation of the user last name field
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        last_name = last_name.strip().capitalize()
        if not last_name:
            raise forms.ValidationError('Last Name can not be empty!')

        if not last_name.isalpha():
            raise forms.ValidationError('Last Name must contain only letters')

        return last_name

    # Validation of the user email field
    def clean_email(self):
        email = self.cleaned_data.get('email').strip()
        if not email:
            raise forms.ValidationError('Email can not be empty!')

        pattern = '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'

        if not pattern and re.match(pattern, email):
            raise forms.ValidationError("Enter a valid email address!")

        deleted_user = UserAccountDeletion.objects.filter(user__email=email, is_deleted=True,
                                                          user__is_active=False).exists()
        if deleted_user:
            deleted_user = VerifiedUsers.objects.get(email=email)
            days_since_deletion = (now() - deleted_user.user_account_deletion.deletion_time).days
            restore_link = reverse('restore_account')
            if days_since_deletion < 30:
                raise forms.ValidationError(
                    f'Your account has been deleted!'
                    f' You can restore your account within'
                    f' the next {30 - days_since_deletion} days by clicking'
                    f'<a href="{restore_link}">Click here.</a> '
                    f'Or use a different email to create a new account now.'
                )

        if VerifiedUsers.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this Email Address already exists!')

        if UnverifiedUsers.objects.filter(email=email).exists():
            unverified_user_account = UnverifiedUsers.objects.get(email=email)
            unverified_user_account.delete()

        return email

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

    # Validation of the password field
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        # Password strength check
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not re.match(pattern, password1):
            raise forms.ValidationError(
                gettext_lazy("Password must be at least 8 characters long and include at least: "
                  "one uppercase letter, one lowercase letter, one digit, and one special character.")
            )

        # Django's built-in password validator to check for the common passwords
        try:
            validate_password(password1)
        except forms.ValidationError as e:
            raise forms.ValidationError(e.messages)

        return password1


class UserRegistrationForm(BaseUserForm):
    """
        Form for unverified user registration
    """

    class Meta(BaseUserForm.Meta):
        model = UnverifiedUsers
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']


class UserVerificationForm(forms.Form):
    """
        Form for verifying email of the registered users via code
    """

    verification_code = forms.CharField(max_length=6, required=True)

    # Storing the user instance
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    # Validation of the verification code
    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code')

        # Fetching the verification entry for the user
        verification_entry = UnverifiedUsersVerificationCode.objects.filter(user=self.user).first()

        if not verification_entry:
            raise forms.ValidationError('No verification code found for this user.')

        if verification_entry.is_expired():
            raise forms.ValidationError('The verification code has expired!')

        if verification_entry.verification_code != verification_code:
            raise forms.ValidationError('Invalid verification code.')

        return verification_code


class UserVerifiedRegistrationForm(BaseUserForm):
    """
        Form for verified user registration
    """

    class Meta(BaseUserForm.Meta):
        model = VerifiedUsers
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']


class UserProfileForm(forms.ModelForm):
    """
        Form for the user profile details:

        username: Field of the user's username
        phone_number: Field of the user's phone_number
        address: Field of the user's address
    """

    username = forms.CharField(max_length=150, required=False, label='Username')
    phone_number = forms.CharField(max_length=13, required=False, label='Phone Number')
    address = forms.CharField(max_length=250, required=False, label='Address')

    class Meta:
        model = Profile
        fields = ['username', 'phone_number', 'address']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'placeholder': 'Address'}),
        }

    # Validation of the username field
    def clean_username(self):
        username = self.cleaned_data.get('username')
        username = username.strip()
        if username == '':
            return None

        if Profile.objects.filter(username=username).exists():
            raise forms.ValidationError('A user with this Username already exists!')

        return username

    # Validation of the phone number field
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')

        # Regex to check if phone number is in the format +998XXXXXXXXX
        pattern = r'^\+998(9[0-9]{2}|3[0-9]{2}|5[0-9]{2}|6[0-9]{2})[0-9]{6}$'

        if phone_number == '':
            return None

        if phone_number and not re.match(pattern, phone_number):
            raise forms.ValidationError("Enter a valid Uzbekistan phone number in the format ( +998XXXXXXXXX ) ")

        if Profile.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('A user with this Phone Number already exists!')

        return phone_number

    # Validation of the address field
    def clean_address(self):
        address = self.cleaned_data.get('address')
        address = address.strip()

        if len(address) > 250:
            raise forms.ValidationError('Address can be maximum 250 characters long!')

        return address