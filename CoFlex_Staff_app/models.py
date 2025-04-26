from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta


# Custom Manager for creating staff account
class StaffAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


# All staff accounts table
class StaffAccounts(AbstractBaseUser, PermissionsMixin):
    staff_first_name = models.CharField(max_length=100, null=False, blank=False)
    staff_last_name = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    staff_email = models.EmailField(unique=True, null=False, blank=False)
    location_code = models.CharField(null=False, blank=False, max_length=100)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name="staff_users",  # Change the related_name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name="staff_permissions",  # Change the related_name
        blank=True
    )

    objects = StaffAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['staff_first_name', 'staff_last_name']

    class Meta:
        verbose_name = 'Staff Account'
        verbose_name_plural = 'Staff Accounts'
        constraints = [
            models.UniqueConstraint(fields=['email', 'location_code'], name='unique_staff_per_location')
        ]

    def __str__(self):
        return self.email


# All staff accounts profiles table
class StaffAccountsProfiles(models.Model):
    staff = models.OneToOneField(StaffAccounts, on_delete=models.CASCADE, related_name='staff_profiles')
    staff_username = models.CharField(unique=True, null=False, blank=False, max_length=100)
    phone_number = models.CharField(null=False, blank=False, max_length=13)
    address = models.TextField(null=False, blank=False, max_length=250)

    class Meta:
        verbose_name = "Staff Profile"
        verbose_name_plural = "Staff Profiles"

    def __str__(self):
        return f'Profile of {self.staff.email}'


# All staff accounts details table
class StaffPhotoDetails(models.Model):
    staff = models.OneToOneField(StaffAccounts, on_delete=models.CASCADE, related_name='staff_photo_details')
    profile_photo = models.ImageField(blank=True, null=True, upload_to=f'staff_profile_images/')
    photo_path = models.CharField(blank=True, null=True, max_length=300)
    uploaded_time = models.DateTimeField(default=now, blank=True, null=True)

    class Meta:
        verbose_name = 'Staff Photo Details'
        verbose_name_plural = 'Staff Photo Details'

    def __str__(self):
        return f"Profile photo of {self.staff.email}"


# All staff accounts edit main email table
class StaffEditMainEmail(models.Model):
    staff = models.OneToOneField(StaffAccounts, on_delete=models.CASCADE, related_name='staff_edit_main_email')
    new_email = models.EmailField(null=True, blank=True)
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    is_code_used = models.BooleanField(default=False, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Staff Edit Main Email Verification Code'
        verbose_name_plural = 'Staffs Edit Main Emails Verification Codes'

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = now() + timedelta(minutes=1)
        super().save(*args, **kwargs)

    def is_expired(self):
        return self.expires_at < now()

    def __str__(self):
        return f'Verification code for {self.staff.staff_email}'


# All staff accounts sign up, login and logout activities table
class StaffSignUpLoginLogoutActivity(models.Model):
    ACTION_CHOICES = [
        ('Sign Up', 'Sign Up'),
        ('Login', 'Login'),
        ('Logout', 'Logout'),
    ]

    staff = models.ForeignKey(StaffAccounts, on_delete=models.CASCADE)
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
        verbose_name = 'Staff SignUp-Login-Logout Activity'
        verbose_name_plural = 'Staff SignUp-Login-Logout Activities'

    def __str__(self):
        return self.staff.staff_email


# All staff accounts device activities table
class StaffDeviceActivities(models.Model):
    staff_session = models.ForeignKey(StaffSignUpLoginLogoutActivity, on_delete=models.CASCADE,related_name='staff_device_activities')
    activity_type = models.CharField(max_length=250, null=True, blank=True)
    activity_details = models.JSONField(null=True, blank=True)
    date_time = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Staff Device Activity'
        verbose_name_plural = 'Staff Device Activities'

    def __str__(self):
        return self.staff_session.staff.staff_email


# Locations table storing the data of all locations
class StaffLocations(models.Model):
    location_name = models.CharField(null=False, blank=False, max_length=250)
    location_code = models.CharField(unique=True, null=False, blank=False, max_length=100)
    location_latitude = models.FloatField(null=False, blank=False)
    location_longitude = models.FloatField(null=False, blank=False)
    # icon_path = models.CharField(null=False, blank=False, max_length=250, default='/static/CoFlex_app/icons/bb.png')

    class Meta:
        verbose_name = 'Staff Location'
        verbose_name_plural = 'Staff Locations'

    def __str__(self):
        return self.location_code


# Location Details table storing details of the locations
class StaffLocationDetails(models.Model):
    location = models.OneToOneField(StaffLocations, on_delete=models.CASCADE, related_name='staff_location_details')
    address = models.CharField(null=False, blank=False, max_length=250)
    contact_phone = models.CharField(null=False, blank=False, max_length=250)
    working_hours = models.CharField(null=False, blank=False, max_length=250)
    # image_path = models.CharField( null=False, blank=False, max_length=250, default='/static/CoFlex_app/location_images/bb.jpg')
    website = models.URLField(null=False, blank=False, max_length=250)
    default_availability = models.IntegerField(null=False, blank=False)

    class Meta:
        verbose_name = 'Staff Location Detail'
        verbose_name_plural = 'Staff Locations Details'

    def __str__(self):
        return f'Location Details of {self.location.location_code}'


# Location Availability table storing availability of the locations
class StaffLocationAvailability(models.Model):
    location = models.ForeignKey(StaffLocations, on_delete=models.CASCADE, related_name='staff_location_availability')
    date = models.DateField(blank=False, null=False)
    availability = models.IntegerField(blank=False, null=True, default=0)

    class Meta:
        verbose_name = 'Staff Location Availability'
        verbose_name_plural = 'Staff Locations Availabilities'
        unique_together = ('location', 'date')  # Preventing duplicate location and date a pair of variables

    def __str__(self):
        return f'Location Availability of {self.location.location_code}'


# All Locations Bookings
class All_Locations_Bookings(models.Model):
    user_first_name = models.CharField(max_length=100, null=False, blank=False)
    user_last_name = models.CharField(max_length=100, null=False, blank=False)
    user_email = models.EmailField(null=False, blank=False)
    user_phone_number = models.CharField(null=True, blank=True, max_length=13)

    booking_id = models.CharField(unique=True, max_length=12, blank=False, null=False)

    location = models.ForeignKey(StaffLocations, on_delete=models.CASCADE, related_name='location_bookings')
    location_code = models.CharField(null=False, blank=False, max_length=100)
    location_name = models.CharField(null=False, blank=False, max_length=250)

    created_date = models.DateField(null=False, blank=False)
    created_time = models.TimeField(null=False, blank=False)

    class Meta:
        verbose_name = 'All Locations Booking'
        verbose_name_plural = 'All Locations Bookings'

    def __str__(self):
        return self.booking_id


# All Locations Bookings Details
class All_Locations_Bookings_Details(models.Model):
    location_booking = models.OneToOneField(All_Locations_Bookings, on_delete=models.CASCADE,
                                            related_name='booking_details')
    start_date = models.DateField(null=False, blank=False)
    start_time = models.TimeField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)
    end_time = models.TimeField(null=False, blank=False)

    duration = models.DecimalField(null=True, blank=True, max_digits=3, decimal_places=2)
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)

    special_requests = models.CharField(null=False, blank=False, max_length=250, default='No Requests')
    status = models.CharField(max_length=20, choices=[
        ('Booked', 'Booked'),
        ('In Progress', 'In Progress'),
        ('Finished', 'Finished'),
        ('Due Out', 'Due Out'),
        ('Cancelled', 'Cancelled'),
    ], default='Booked')

    class Meta:
        verbose_name = 'All Locations Bookings Detail'
        verbose_name_plural = 'All Locations Bookings Details'

    def __str__(self):
        return f'Booking Details of {self.location_booking.booking_id}'
