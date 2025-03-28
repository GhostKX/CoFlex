from django.db import models
from .verified_user_profile_details import VerifiedUsers
from django.utils import timezone


# User Recent Actions table for storing user's sign up, login and logout details
class UserSignUpLoginLogoutActivity(models.Model):

    ACTION_CHOICES = [
        ('Sign Up', 'Sign Up'),
        ('Login', 'Login'),
        ('Logout', 'Logout'),
    ]

    user = models.ForeignKey(VerifiedUsers, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=255, null=False, blank=False)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_type = models.CharField(max_length=150, null=True, blank=True)
    browser = models.CharField(max_length=150, null=True, blank=True)
    operating_system = models.CharField(max_length=150, null=True, blank=True)
    device_name = models.CharField(max_length=150, null=True, blank=True)
    organization = models.CharField(max_length=250, null=True, blank=True)

    city = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    date_time = models.DateTimeField(default=timezone.now)

    is_Logged_in = models.BooleanField(default=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)

    class Meta:
        verbose_name = 'User SignUp-Login-Logout Activity'
        verbose_name_plural = 'User SignUp-Login-Logout Activities'

    def __str__(self):
        return self.user.email


# User Recent Actions table for storing actions that were done while the user is logged in
class UserDeviceActivities(models.Model):
    user_session = models.ForeignKey(UserSignUpLoginLogoutActivity, on_delete=models.CASCADE, related_name='user_device_activities')
    activity_type = models.CharField(max_length=250, null=True, blank=True)
    activity_details = models.JSONField(null=True, blank=True)
    date_time = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'User Device Activity'
        verbose_name_plural = 'User Device Activities'

    def __str__(self):
        return self.user_session.user.email

