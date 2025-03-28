from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.timezone import now


# Custom User Manager to handle user creation and superuser creation
class CustomUserManager(BaseUserManager):
    def get_by_natural_key(self, email):
        """
            Overriding the django's function
             to let the user to login using email instead of the username.
        """
        return self.get(email=self.normalize_email(email))

    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        """
            Creating and returning a regular user.
        """
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)

        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        """
            Creating and returning a superuser.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, first_name, last_name, password, **extra_fields)


# Table for storing Unverified users data
class UnverifiedUsers(AbstractBaseUser):
    first_name = models.CharField(max_length=150, null=False, blank=False)
    last_name = models.CharField(max_length=150, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    registered_datetime = models.DateTimeField(default=now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Unverified User'
        verbose_name_plural = 'Unverified Users'

    def __str__(self):
        return self.email


# Verification Code table for unverified Users
class UnverifiedUsersVerificationCode(models.Model):
    user = models.OneToOneField(UnverifiedUsers, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    is_code_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = 'Unverified User Verification Code'
        verbose_name_plural = 'Unverified Users Verification Codes'

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = now() + timedelta(minutes=1)
        super().save(*args, **kwargs)

    def is_expired(self):
        return self.expires_at < now()

    def __str__(self):
        return f'Verification code for {self.user.email}'


# Verified Users table for storing verified users details
class VerifiedUsers(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=150, null=False, blank=False)
    last_name = models.CharField(max_length=150, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    registered_datetime = models.DateTimeField(default=now)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name="verified_users",  # Related name for grouping the users to separate users from the staffs
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name="verified_permissions",  # naming users permissons
        blank=True
    )

    objects = CustomUserManager()  # Using the Custom Manager for the user creation

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Verified User'
        verbose_name_plural = 'Verified Users'

    def __str__(self):
        return self.email


# Verified Users Profile details table
class Profile(models.Model):
    user = models.OneToOneField(VerifiedUsers, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(null=True, blank=True, max_length=150)
    phone_number = models.CharField(null=True, blank=True, max_length=13)
    address = models.TextField(null=True, blank=True, max_length=250)

    class Meta:
        verbose_name = "Verified User Profile"
        verbose_name_plural = "Verified Users Profiles"

    def __str__(self):
        return f'Profile of {self.user.email}'


# Verified Users details table
class UserDetails(models.Model):
    user = models.OneToOneField(VerifiedUsers, on_delete=models.CASCADE, related_name='user_details')
    is_active = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=True)
    is_subscribed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Verified User Detail"
        verbose_name_plural = "Verified Users Details"

    def __str__(self):
        return f'Profile of {self.user.email}'


# Verified Users extra details table
class UserExtraDetails(models.Model):
    user = models.OneToOneField(VerifiedUsers, on_delete=models.CASCADE, related_name='user_extra_details')
    bio = models.TextField(null=True, blank=True, max_length=150)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(null=True, blank=True, max_length=6)
    age = models.CharField(null=True, blank=True, max_length=3)
    website = models.CharField(null=True, blank=True, max_length=250)

    class Meta:
        verbose_name = 'Verified User Extra Details'
        verbose_name_plural = 'Verified Users Extra Details'

    def __str__(self):
        return f"Extra Details of {self.user.email}"


# Verified Users extra contact details table
class UserExtraContactDetails(models.Model):
    user = models.OneToOneField(VerifiedUsers, on_delete=models.CASCADE, related_name='user_extra_contact_details')
    second_email = models.EmailField(null=True, blank=True)
    second_phone_number = models.CharField(null=True, blank=True, max_length=13)
    second_address = models.TextField(null=True, blank=True, max_length=250)

    class Meta:
        verbose_name = 'Verified User Extra Contact Details'
        verbose_name_plural = 'Verified Users Extra Contact Details'

    def __str__(self):
        return f"Extra Contact Details of {self.user.email}"


# Verified Users Photo details table
class UserPhotoDetails(models.Model):
    user = models.OneToOneField(VerifiedUsers, on_delete=models.CASCADE, related_name='user_photo_details')
    profile_photo = models.ImageField(blank=True, null=True, upload_to=f'profile_images/')
    photo_path = models.CharField(blank=True, null=True, max_length=300)
    uploaded_time = models.DateTimeField(default=now, blank=True, null=True)

    class Meta:
        verbose_name = 'Verified User Photo Details'
        verbose_name_plural = 'Verified Users Photo Details'

    def __str__(self):
        return f"Profile photo of {self.user.email}"


# Verified Users password verification table
class VerifiedUsersPasswordVerificationCode(models.Model):
    user = models.OneToOneField(VerifiedUsers, on_delete=models.CASCADE, related_name='verified_user_verification')
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    is_code_used = models.BooleanField(default=False, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Verified User Password Verification Code'
        verbose_name_plural = 'Verified Users Password Verification Codes'

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = now() + timedelta(minutes=1)
        super().save(*args, **kwargs)

    def is_expired(self):
        return self.expires_at < now()

    def __str__(self):
        return f'Verification code for {self.user.email}'