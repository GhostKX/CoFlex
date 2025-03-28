import datetime
import os
import re
from django import forms
from ..models import (VerifiedUsers, Profile, UserExtraContactDetails, UserPhotoDetails,
                      SecondEmailVerificationCode)


class UserExtraDetailsForm(forms.Form):
    """
        A form to collect additional user details:

        bio: Biography of the user
        date of birth: Date field for the date of birth
        gender: Gender of the user
        age: Age of the user
        website: Website that user want to share
        address: Address of the user
    """

    GENDER_CHOICES = [
        ('', 'Select Gender'),
        ('Male', 'Male'),
        ('Female', 'Female')
    ]

    bio = forms.CharField(max_length=150, required=False, label='Bio')
    dob = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False)
    age = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter your age'}),
        required=False, max_length=2, label='Age')
    website = forms.URLField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., https://www.yourwebsite.com'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 123 Main St, City, Country'})
    )

    # Storing the user instance
    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance

    # Validation of the age field
    def clean_age(self):
        age = self.cleaned_data.get('age')
        age = age.strip()
        if age and (not age.isdigit() or int(age) < 0 or int(age) > 99):
            raise forms.ValidationError('Age must be a number between 0 and 99')
        return age

    # Validation of the date of birth field
    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        if dob:
            today = datetime.date.today()
            min_date = today.replace(year=today.year - 120)
            if dob > today:
                raise forms.ValidationError('Date of Birth can not be in the future!')

            if dob < min_date:
                raise forms.ValidationError('Date of birth cannot indicate an age greater than 120 years.')

        return dob

    # Validation of the website field
    def clean_website(self):
        website = self.cleaned_data.get('website')
        website = website.strip()

        if len(website) > 250:
            raise forms.ValidationError('Website must be maximum 250 characters long!')

        return website

    # Validation of the address field
    def clean_address(self):
        address = self.cleaned_data.get('address')
        address = address.strip()

        if len(address) > 250:
            raise forms.ValidationError('Address can be maximum 250 characters long!')

        return address


class UserExtraContactDetailsForm(forms.ModelForm):
    """
       A form to manage additional user contact details:

        second email: Second contact email of the user
        second phone number: Second phone number of the user
        second address: Second address of the user
    """
    second_email = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'example@email.com'}),
        required=False, label='Second Email')
    second_phone_number = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'}),
        max_length=13, required=False, label='Second Phone Number')
    second_address = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 123 Main St, City, Country'}),
        max_length=250, required=False, label='Second Address')

    class Meta:
        model = UserExtraContactDetails
        fields = ['second_email', 'second_phone_number', 'second_address']
        widgets = {
            'second_email': forms.EmailInput(),
            'second_phone_number': forms.TextInput(),
            'second_address': forms.Textarea()
        }

    # Validation of the second email
    def clean_second_email(self):
        second_email = self.cleaned_data.get('second_email', '').strip()

        if second_email:
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

            if second_email and not re.match(email_regex, second_email):
                raise forms.ValidationError("Please enter a valid email address!")

            if VerifiedUsers.objects.filter(email=second_email).exists():
                raise forms.ValidationError('An email address is already in use!')

            if UserExtraContactDetails.objects.exclude(user=self.instance).filter(second_email=second_email).exists():
                raise forms.ValidationError('A user with this Email Address already exists!')

        return second_email

    # Validation of the second phone number
    def clean_second_phone_number(self):
        second_phone_number = self.cleaned_data.get('second_phone_number', '').strip()

        if second_phone_number:
            # Regex to check if phone number is in the format +998XXXXXXXXX
            pattern = r'^\+998(9[0-9]{2}|3[0-9]{2}|5[0-9]{2}|6[0-9]{2})[0-9]{6}$'

            if second_phone_number and not re.match(pattern, second_phone_number):
                raise forms.ValidationError("Enter a valid Uzbekistan phone number in the format ( +998XXXXXXXXX ) ")

            if Profile.objects.filter(phone_number=second_phone_number).exists():
                raise forms.ValidationError('A phone number is already in use!')

            if UserExtraContactDetails.objects.exclude(user=self.instance).filter(
                    second_phone_number=second_phone_number).exists():
                raise forms.ValidationError('A user with this Phone Number already exists!')

        return second_phone_number

    # Validation of the second address
    def clean_second_address(self):
        second_address = self.cleaned_data.get('second_address', '').strip()

        if second_address:
            if len(second_address) > 250:
                raise forms.ValidationError('Address can be maximum 250 characters long!')

        return second_address


class UserProfilePhotoDetailsForm(forms.ModelForm):
    """
       A form to manage additional user contact details:

        profile_photo: File field to store the user's photos
    """

    class Meta:
        model = UserPhotoDetails
        fields = ['profile_photo']
        widgets = {
            'profile_photo': forms.ClearableFileInput()
        }

    # Validation for the user's profile photo
    def clean_profile_photo(self):
        profile_photo = self.cleaned_data.get('profile_photo')

        if profile_photo:

            content_type = profile_photo.content_type
            if content_type not in ['image/jpeg', 'image/png', 'image/gif']:
                raise forms.ValidationError(
                    "Invalid content type. Allowed types are: image/jpeg, image/png, image/gif."
                )

            if profile_photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("The image file is too large. Maximum size is 5MB.")

            # Validating type of the file
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            ext = os.path.splitext(profile_photo.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError("Invalid file extension. Allowed extensions are: .jpg, .jpeg, .png, .gif.")

        return profile_photo


class UserEditBasicInfoForm(forms.Form):
    """
        A form to edit basic user information:
        First Name , Last Name, Username, and Phone Number.
    """

    first_name = forms.CharField(max_length=150, required=True, label='First Name')
    last_name = forms.CharField(max_length=150, required=True, label='Last Name')
    username = forms.CharField(max_length=150, required=False, label='Username')
    phone_number = forms.CharField(max_length=13, required=False, label='Phone Number')

    # Storing the user instance
    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance

    # Validation for the user first name field
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        first_name = first_name.strip().capitalize()
        if not first_name:
            raise forms.ValidationError('First Name can not be empty!')

        if not first_name.isalpha():
            raise forms.ValidationError('First Name must contain only letters')

        return first_name

    # Validation for the user last name field
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        last_name = last_name.strip().capitalize()
        if not last_name:
            raise forms.ValidationError('Last Name can not be empty!')

        if not last_name.isalpha():
            raise forms.ValidationError('Last Name must contain only letters')

        return last_name

    # Validation for the user username field
    def clean_username(self):
        username = self.cleaned_data.get('username')
        username = username.strip()

        if username == '':
            self.cleaned_data['username'] = None
            return None

        if Profile.objects.exclude(user=self.instance).filter(username=username).exists():
            raise forms.ValidationError('A user with this Username already exists!')

        return username

    # Validation for the user phone number field
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        phone_number = phone_number.strip()

        # Regex to check if phone number is in the format +998XXXXXXXXX
        pattern = r'^\+998(9[0-9]{2}|3[0-9]{2}|5[0-9]{2}|6[0-9]{2})[0-9]{6}$'

        if phone_number == '':
            self.cleaned_data['phone_number'] = None
            return None

        if phone_number and not re.match(pattern, phone_number):
            raise forms.ValidationError("Enter a valid Uzbekistan phone number in the format ( +998XXXXXXXXX ) ")

        if Profile.objects.exclude(user=self.instance).filter(phone_number=phone_number).exists():
            raise forms.ValidationError('A user with this Phone Number already exists!')

        return phone_number


class SecondEmailVerificationCodeForm(forms.Form):
    """
        A form for verifying a user's second email address using a verification code.
    """
    verification_code = forms.CharField(max_length=6, required=True)

    # Storing the user instance
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    # Validation of the verification code field
    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code')

        verification_entry = SecondEmailVerificationCode.objects.filter(user=self.user).first()

        if not verification_entry:
            raise forms.ValidationError('No verification code found for this user.')

        if verification_entry.is_expired():
            raise forms.ValidationError('The verification code has expired!')

        if verification_entry.verification_code != verification_code:
            raise forms.ValidationError('Invalid verification code.')

        return verification_code
