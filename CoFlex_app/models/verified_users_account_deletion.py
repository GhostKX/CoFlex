from datetime import timedelta
from django.db import models
from django.utils.timezone import now
from .verified_user_profile_details import VerifiedUsers


# User's Second Email verification code table
class SecondEmailVerificationCode(models.Model):
    user = models.OneToOneField(VerifiedUsers, on_delete=models.CASCADE, related_name='second_email_verification_code')
    second_email = models.EmailField(null=True, blank=True)
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    is_code_used = models.BooleanField(default=False, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Verified User Second Email Verification Code'
        verbose_name_plural = 'Verified Users Second Emails Verification Codes'

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = now() + timedelta(minutes=1)
        super().save(*args, **kwargs)

    def is_expired(self):
        return self.expires_at < now()

    def __str__(self):
        return f'Verification code for {self.user.second_email_verification_code.second_email}'


# User's main email table for storing user's new email table
class UserEditMainEmail(models.Model):
    user = models.OneToOneField(VerifiedUsers, on_delete=models.CASCADE, related_name='user_edit_main_email')
    new_email = models.EmailField(null=True, blank=True)
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    is_code_used = models.BooleanField(default=False, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Verified User Edit Main Email Verification Code'
        verbose_name_plural = 'Verified Users Edit Main Emails Verification Codes'

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = now() + timedelta(minutes=1)
        super().save(*args, **kwargs)

    def is_expired(self):
        return self.expires_at < now()

    def __str__(self):
        return f'Verification code for {self.user.email}'


# Table for storing user's account's deletion attempts table
class UserAccountDeletion(models.Model):
    user = models.OneToOneField(VerifiedUsers, on_delete=models.CASCADE, related_name='user_account_deletion')
    deletion_time = models.DateTimeField(blank=True, null=True)
    deletion_details = models.CharField(blank=True, null=True, max_length=100)
    is_deleted = models.BooleanField(default=False)
    deletion_attempts = models.IntegerField(default=0, blank=True, null=True)
    is_blocked = models.BooleanField(default=False, blank=True, null=True)

    class Meta:
        verbose_name = 'Verified User Account Deletion'
        verbose_name_plural = 'Verified Users Accounts Deletions'

    def __str__(self):
        return f'Account deletion of {self.user.email}'


# Table for storing user's account's restoration attempts table
class UserAccountRestoration(models.Model):
    user = models.OneToOneField(VerifiedUsers, on_delete=models.CASCADE, related_name='user_account_restoration')
    restoration_email = models.EmailField(null=True, blank=True)
    restoration_details = models.CharField(max_length=250, null=True, blank=True)
    restoration_time = models.DateTimeField(default=now, blank=True, null=True)

    class Meta:
        verbose_name = 'User Account Restoration'
        verbose_name_plural = 'Users Accounts Restorations'

    def __str__(self):
        return f'Account restoration of {self.user.email}'


# Table for storing user's account's restoration code table
class UserAccountRecoveryCode(models.Model):
    user = models.OneToOneField(VerifiedUsers, on_delete=models.CASCADE, related_name='user_account_recovery_code')
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    is_code_used = models.BooleanField(default=False, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'User Account Recovery Code'
        verbose_name_plural = 'Users Accounts Recovery Codes'

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = now() + timedelta(minutes=1)
        super().save(*args, **kwargs)

    def is_expired(self):
        return self.expires_at < now()

    def __str__(self):
        return f'Verification code for {self.user.email}'


# Main information of the user who has deleted their account table
class DeletedAccountsMainInfo(models.Model):
    first_name = models.CharField(max_length=150, null=False, blank=False)
    last_name = models.CharField(max_length=150, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    registered_datetime = models.DateTimeField(null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_subscribed = models.BooleanField(default=False)

    password = models.CharField(max_length=300, null=False, blank=False)

    class Meta:
        verbose_name = 'Deleted User'
        verbose_name_plural = 'Deleted Users'

    def __str__(self):
        return self.email


# Details of the user who has deleted their account profile table
class DeletedAccountsProfile(models.Model):
    user = models.OneToOneField(DeletedAccountsMainInfo, on_delete=models.CASCADE, related_name='deleted_profile')
    username = models.CharField(null=True, blank=True, max_length=150)
    phone_number = models.CharField(null=True, blank=True, max_length=13)
    address = models.TextField(null=True, blank=True, max_length=250)

    class Meta:
        verbose_name = 'Deleted User Profile'
        verbose_name_plural = 'Deleted Users Profiles'

    def __str__(self):
        return self.user.email


# Details of the user who has deleted their account table
class DeletedAccountsDetails(models.Model):
    user = models.OneToOneField(DeletedAccountsMainInfo, on_delete=models.CASCADE, related_name='deleted_details')
    bio = models.TextField(null=True, blank=True, max_length=150)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(null=True, blank=True, max_length=6)
    age = models.CharField(null=True, blank=True, max_length=3)
    website = models.CharField(null=True, blank=True, max_length=250)

    class Meta:
        verbose_name = 'Deleted User Details'
        verbose_name_plural = 'Deleted Users Details'

    def __str__(self):
        return self.user.email


# Extra Details of the user who has deleted their accounts
class DeletedAccountsExtraDetails(models.Model):
    user = models.OneToOneField(DeletedAccountsMainInfo, on_delete=models.CASCADE, related_name='deleted_extra_details')
    second_email = models.EmailField(null=True, blank=True)
    second_phone_number = models.CharField(null=True, blank=True, max_length=13)
    second_address = models.TextField(null=True, blank=True, max_length=250)

    class Meta:
        verbose_name = 'Deleted User Extra Details'
        verbose_name_plural = 'Deleted Users Extra Details'

    def __str__(self):
        return self.user.email


# Deleted users profile photos
class DeletedAccountsPhoto(models.Model):
    user = models.OneToOneField(DeletedAccountsMainInfo, on_delete=models.CASCADE, related_name='deleted_photo')
    profile_photo = models.ImageField(blank=True, null=True, upload_to=f'deleted_profile_images/')
    photo_path = models.CharField(blank=True, null=True, max_length=300)
    uploaded_time = models.DateTimeField(default=now, blank=True, null=True)

    class Meta:
        verbose_name = 'Deleted User Photo'
        verbose_name_plural = 'Deleted Users Photos'

    def __str__(self):
        return self.user.email


# Deleted users deletion specifics
class DeletedAccountsSpecifics(models.Model):
    user = models.OneToOneField(DeletedAccountsMainInfo, on_delete=models.CASCADE, related_name='deleted_account_specifics')
    deletion_time = models.DateTimeField(blank=True, null=True)
    deletion_details = models.CharField(blank=True, null=True, max_length=100)
    is_deleted = models.BooleanField(default=False)
    deletion_attempts = models.IntegerField(default=0, blank=True, null=True)
    is_blocked = models.BooleanField(default=False, blank=True, null=True)

    class Meta:
        verbose_name = 'Deleted User Specifics'
        verbose_name_plural = 'Deleted Users Specifics'

    def __str__(self):
        return self.user.email