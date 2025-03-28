import os
import re
from django import forms
from .models import StaffAccounts, StaffAccountsProfiles, StaffPhotoDetails, StaffEditMainEmail


class StaffProfilePhotoDetailsForm(forms.ModelForm):
    class Meta:
        model = StaffPhotoDetails
        fields = ['profile_photo']
        widgets = {
            'profile_photo': forms.ClearableFileInput()
        }

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

            # File validation
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            ext = os.path.splitext(profile_photo.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError("Invalid file extension. Allowed extensions are: .jpg, .jpeg, .png, .gif.")

        return profile_photo


class StaffEditProfileDetailsForm(forms.Form):
    staff_first_name = forms.CharField(max_length=150, required=True, label='First Name')
    staff_last_name = forms.CharField(max_length=150, required=True, label='Last Name')
    staff_email = forms.EmailField(widget=forms.EmailInput(), required=True, label='Email')
    staff_username = forms.CharField(max_length=100, required=True, label='Username')
    phone_number = forms.CharField(max_length=13, required=True, label='Phone Number')
    address = forms.CharField(required=True, widget=forms.TextInput(), label='Address')

    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance

    def clean_staff_first_name(self):
        staff_first_name = self.cleaned_data.get('staff_first_name')
        staff_first_name = staff_first_name.strip().capitalize()
        if not staff_first_name:
            raise forms.ValidationError('First Name can not be empty!')

        if not staff_first_name.isalpha():
            raise forms.ValidationError('First Name must contain only letters')

        return staff_first_name

    def clean_staff_last_name(self):
        staff_last_name = self.cleaned_data.get('staff_last_name')
        staff_last_name = staff_last_name.strip().capitalize()
        if not staff_last_name:
            raise forms.ValidationError('Last Name can not be empty!')

        if not staff_last_name.isalpha():
            raise forms.ValidationError('Last Name must contain only letters')

        return staff_last_name

    def clean_staff_email(self):
        staff_email = self.cleaned_data.get('staff_email', '').strip()

        if staff_email:
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

            if staff_email and not re.match(email_regex, staff_email):
                raise forms.ValidationError("Please enter a valid email address!")

            email_check = StaffAccounts.objects.exclude(staff_email=self.instance.staff_email).filter(staff_email=staff_email).first()
            if email_check:
                raise forms.ValidationError('This email address is already registered with another account!')

        return staff_email

    def clean_staff_username(self):
        staff_username = self.cleaned_data.get('staff_username')
        staff_username = staff_username.strip()

        if staff_username == '':
            self.cleaned_data['staff_username'] = None
            return None

        if StaffAccountsProfiles.objects.exclude(staff=self.instance).filter(staff_username=staff_username).exists():
            raise forms.ValidationError('A staff with this Username already exists!')

        return staff_username

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

        if StaffAccountsProfiles.objects.exclude(staff=self.instance).filter(phone_number=phone_number).exists():
            raise forms.ValidationError('A staff with this Phone Number already exists!')

        return phone_number

    def clean_address(self):
        address = self.cleaned_data.get('address')
        address = address.strip()

        if len(address) > 250:
            raise forms.ValidationError('Address can be maximum 250 characters long!')

        return address


class StaffEditEmailVerificationCodeForm(forms.Form):
    verification_code = forms.CharField(max_length=6, required=True)

    def __init__(self, *args, **kwargs):
        self.staff = kwargs.pop('staff', None)
        super().__init__(*args, **kwargs)

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code')

        verification_entry = StaffEditMainEmail.objects.filter(staff=self.staff).first()

        if not verification_entry:
            raise forms.ValidationError('No verification code found for this staff.')

        if verification_entry.is_expired():
            raise forms.ValidationError('The verification code has expired!')

        if verification_entry.verification_code != verification_code:
            raise forms.ValidationError('Invalid verification code.')

        return verification_code


class StaffCalendarDateChoosingForm(forms.Form):
    selected_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'MM/DD/YYYY'}),
        required=False,
        label="Choose a Date"
    )

    def clean_selected_date(self):
        selected_date = self.cleaned_data.get("selected_date")
        if not selected_date:
            raise forms.ValidationError("The calendar field cannot be empty!")

        return selected_date


class StaffBookingDetailsViewForms(forms.Form):
    STATUS_CHOICES = [
        ('Booked', 'Booked'),
        ('In Progress', 'In Progress'),
        ('Finished', 'Finished'),
        ('Due Out', 'Due Out'),
        ('Cancelled', 'Cancelled')
    ]

    status = forms.ChoiceField(choices=STATUS_CHOICES)





