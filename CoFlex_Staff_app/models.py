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


# C-Space Yunusabad
class C_Space_Yunusabad_Bookings(models.Model):
    user_first_name = models.CharField(max_length=100, null=False, blank=False)
    user_last_name = models.CharField(max_length=100, null=False, blank=False)
    user_email = models.EmailField(null=False, blank=False)
    user_phone_number = models.CharField(null=True, blank=True, max_length=13)

    booking_id = models.CharField(unique=True, max_length=12, blank=False, null=False)
    location_code = models.CharField(null=False, blank=False, max_length=100)
    location_name = models.CharField(null=False, blank=False, max_length=250)

    created_date = models.DateField(null=False, blank=False)
    created_time = models.TimeField(null=False, blank=False)

    class Meta:
        verbose_name = 'C-Space Yunusabad Booking'
        verbose_name_plural = 'C-Space Yunusabad Bookings'

    def __str__(self):
        return self.booking_id


class C_Space_Yunusabad_Bookings_Details(models.Model):
    location_booking = models.OneToOneField(C_Space_Yunusabad_Bookings, on_delete=models.CASCADE,
                                            related_name='c_space_yunusabad_bookings_details')
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
        verbose_name = 'C-Space Yunusabad Bookings Detail'
        verbose_name_plural = 'C-Space Yunusabad Bookings Details'

    def __str__(self):
        return f'Location Booking Details of {self.location_booking.booking_id}'


# C-Space Modera
class C_Space_Modera_Bookings(models.Model):
    user_first_name = models.CharField(max_length=100, null=False, blank=False)
    user_last_name = models.CharField(max_length=100, null=False, blank=False)
    user_email = models.EmailField(null=False, blank=False)
    user_phone_number = models.CharField(null=True, blank=True, max_length=13)

    booking_id = models.CharField(unique=True, max_length=12, blank=False, null=False)
    location_code = models.CharField(null=False, blank=False, max_length=100)
    location_name = models.CharField(null=False, blank=False, max_length=250)

    created_date = models.DateField(null=False, blank=False)
    created_time = models.TimeField(null=False, blank=False)

    class Meta:
        verbose_name = 'C-Space Modera Booking'
        verbose_name_plural = 'C-Space Modera Bookings'

    def __str__(self):
        return self.booking_id


class C_Space_Modera_Bookings_Details(models.Model):
    location_booking = models.OneToOneField(C_Space_Modera_Bookings, on_delete=models.CASCADE,
                                            related_name='c_space_modera_bookings_details')
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
        verbose_name = 'C-Space Modera Bookings Detail'
        verbose_name_plural = 'C-Space Modera Bookings Details'

    def __str__(self):
        return f'Location Booking Details of {self.location_booking.booking_id}'


# C-Space Labzak
class C_Space_Labzak_Bookings(models.Model):
    user_first_name = models.CharField(max_length=100, null=False, blank=False)
    user_last_name = models.CharField(max_length=100, null=False, blank=False)
    user_email = models.EmailField(null=False, blank=False)
    user_phone_number = models.CharField(null=True, blank=True, max_length=13)

    booking_id = models.CharField(unique=True, max_length=12, blank=False, null=False)
    location_code = models.CharField(null=False, blank=False, max_length=100)
    location_name = models.CharField(null=False, blank=False, max_length=250)

    created_date = models.DateField(null=False, blank=False)
    created_time = models.TimeField(null=False, blank=False)

    class Meta:
        verbose_name = 'C-Space Labzak Booking'
        verbose_name_plural = 'C-Space Labzak Bookings'

    def __str__(self):
        return self.booking_id


class C_Space_Labzak_Bookings_Details(models.Model):
    location_booking = models.OneToOneField(C_Space_Modera_Bookings, on_delete=models.CASCADE,
                                            related_name='c_space_labzak_bookings_details')
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
        verbose_name = 'C-Space Labzak Bookings Detail'
        verbose_name_plural = 'C-Space Labzak Bookings Details'

    def __str__(self):
        return f'Location Booking Details of {self.location_booking.booking_id}'


# C-Space Airport
class C_Space_Airport_Bookings(models.Model):
    user_first_name = models.CharField(max_length=100, null=False, blank=False)
    user_last_name = models.CharField(max_length=100, null=False, blank=False)
    user_email = models.EmailField(null=False, blank=False)
    user_phone_number = models.CharField(null=True, blank=True, max_length=13)

    booking_id = models.CharField(unique=True, max_length=12, blank=False, null=False)
    location_code = models.CharField(null=False, blank=False, max_length=100)
    location_name = models.CharField(null=False, blank=False, max_length=250)

    created_date = models.DateField(null=False, blank=False)
    created_time = models.TimeField(null=False, blank=False)

    class Meta:
        verbose_name = 'C-Space Airport Booking'
        verbose_name_plural = 'C-Space Airport Bookings'

    def __str__(self):
        return self.booking_id


class C_Space_Airport_Bookings_Details(models.Model):
    location_booking = models.OneToOneField(C_Space_Modera_Bookings, on_delete=models.CASCADE,
                                            related_name='c_space_airport_bookings_details')
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
        verbose_name = 'C-Space Airport Bookings Detail'
        verbose_name_plural = 'C-Space Airport Bookings Details'

    def __str__(self):
        return f'Location Booking Details of {self.location_booking.booking_id}'


# C-Space Chust
class C_Space_Chust_Bookings(models.Model):
    user_first_name = models.CharField(max_length=100, null=False, blank=False)
    user_last_name = models.CharField(max_length=100, null=False, blank=False)
    user_email = models.EmailField(null=False, blank=False)
    user_phone_number = models.CharField(null=True, blank=True, max_length=13)

    booking_id = models.CharField(unique=True, max_length=12, blank=False, null=False)
    location_code = models.CharField(null=False, blank=False, max_length=100)
    location_name = models.CharField(null=False, blank=False, max_length=250)

    created_date = models.DateField(null=False, blank=False)
    created_time = models.TimeField(null=False, blank=False)

    class Meta:
        verbose_name = 'C-Space Chust Booking'
        verbose_name_plural = 'C-Space Chust Bookings'

    def __str__(self):
        return self.booking_id


class C_Space_Chust_Bookings_Details(models.Model):
    location_booking = models.OneToOneField(C_Space_Modera_Bookings, on_delete=models.CASCADE,
                                            related_name='c_space_chust_bookings_details')
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
        verbose_name = 'C-Space Chust Bookings Detail'
        verbose_name_plural = 'C-Space Chust Bookings Details'

    def __str__(self):
        return f'Location Booking Details of {self.location_booking.booking_id}'


# C-Space Elbek
class C_Space_Elbek_Bookings(models.Model):
    user_first_name = models.CharField(max_length=100, null=False, blank=False)
    user_last_name = models.CharField(max_length=100, null=False, blank=False)
    user_email = models.EmailField(null=False, blank=False)
    user_phone_number = models.CharField(null=True, blank=True, max_length=13)

    booking_id = models.CharField(unique=True, max_length=12, blank=False, null=False)
    location_code = models.CharField(null=False, blank=False, max_length=100)
    location_name = models.CharField(null=False, blank=False, max_length=250)

    created_date = models.DateField(null=False, blank=False)
    created_time = models.TimeField(null=False, blank=False)

    class Meta:
        verbose_name = 'C-Space Elbek Booking'
        verbose_name_plural = 'C-Space Elbek Bookings'

    def __str__(self):
        return self.booking_id


class C_Space_Elbek_Bookings_Details(models.Model):
    location_booking = models.OneToOneField(C_Space_Modera_Bookings, on_delete=models.CASCADE,
                                            related_name='c_space_elbek_bookings_details')
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
        verbose_name = 'C-Space Elbek Bookings Detail'
        verbose_name_plural = 'C-Space Elbek Bookings Details'

    def __str__(self):
        return f'Location Booking Details of {self.location_booking.booking_id}'


# Ground Zero Minor
class Ground_Zero_Minor_Bookings(models.Model):
    user_first_name = models.CharField(max_length=100, null=False, blank=False)
    user_last_name = models.CharField(max_length=100, null=False, blank=False)
    user_email = models.EmailField(null=False, blank=False)
    user_phone_number = models.CharField(null=True, blank=True, max_length=13)

    booking_id = models.CharField(unique=True, max_length=12, blank=False, null=False)
    location_code = models.CharField(null=False, blank=False, max_length=100)
    location_name = models.CharField(null=False, blank=False, max_length=250)

    created_date = models.DateField(null=False, blank=False)
    created_time = models.TimeField(null=False, blank=False)

    class Meta:
        verbose_name = 'Ground Zero Minor Booking'
        verbose_name_plural = 'Ground Zero Minor Bookings'

    def __str__(self):
        return self.booking_id


class Ground_Zero_Minor_Bookings_Details(models.Model):
    location_booking = models.OneToOneField(C_Space_Modera_Bookings, on_delete=models.CASCADE,
                                            related_name='ground_zero_minor_bookings_details')
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
        verbose_name = 'Ground Zero Minor Bookings Detail'
        verbose_name_plural = 'Ground Zero Minor Bookings Details'

    def __str__(self):
        return f'Location Booking Details of {self.location_booking.booking_id}'


# Ground Zero Sharq
class Ground_Zero_Sharq_Bookings(models.Model):
    user_first_name = models.CharField(max_length=100, null=False, blank=False)
    user_last_name = models.CharField(max_length=100, null=False, blank=False)
    user_email = models.EmailField(null=False, blank=False)
    user_phone_number = models.CharField(null=True, blank=True, max_length=13)

    booking_id = models.CharField(unique=True, max_length=12, blank=False, null=False)
    location_code = models.CharField(null=False, blank=False, max_length=100)
    location_name = models.CharField(null=False, blank=False, max_length=250)

    created_date = models.DateField(null=False, blank=False)
    created_time = models.TimeField(null=False, blank=False)

    class Meta:
        verbose_name = 'Ground Zero Sharq Booking'
        verbose_name_plural = 'Ground Zero Sharq Bookings'

    def __str__(self):
        return self.booking_id


class Ground_Zero_Sharq_Bookings_Details(models.Model):
    location_booking = models.OneToOneField(C_Space_Modera_Bookings, on_delete=models.CASCADE,
                                            related_name='ground_zero_sharq_bookings_details')
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
        verbose_name = 'Ground Zero Sharq Bookings Detail'
        verbose_name_plural = 'Ground Zero Sharq Bookings Details'

    def __str__(self):
        return f'Location Booking Details of {self.location_booking.booking_id}'


# Ground Zero Kitob Olami
class Ground_Zero_Kitob_Olami_Bookings(models.Model):
    user_first_name = models.CharField(max_length=100, null=False, blank=False)
    user_last_name = models.CharField(max_length=100, null=False, blank=False)
    user_email = models.EmailField(null=False, blank=False)
    user_phone_number = models.CharField(null=True, blank=True, max_length=13)

    booking_id = models.CharField(unique=True, max_length=12, blank=False, null=False)
    location_code = models.CharField(null=False, blank=False, max_length=100)
    location_name = models.CharField(null=False, blank=False, max_length=250)

    created_date = models.DateField(null=False, blank=False)
    created_time = models.TimeField(null=False, blank=False)

    class Meta:
        verbose_name = 'Ground Zero Kitob Olami Booking'
        verbose_name_plural = 'Ground Zero Kitob Olami Bookings'

    def __str__(self):
        return self.booking_id


class Ground_Zero_Kitob_Olami_Bookings_Details(models.Model):
    location_booking = models.OneToOneField(C_Space_Modera_Bookings, on_delete=models.CASCADE,
                                            related_name='ground_zero_kitob_olami_bookings_details')
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
        verbose_name = 'Ground Zero Kitob Olami Bookings Detail'
        verbose_name_plural = 'Ground Zero Kitob Olami Bookings Details'

    def __str__(self):
        return f'Location Booking Details of {self.location_booking.booking_id}'


# U-Enter
class U_Enter_Bookings(models.Model):
    user_first_name = models.CharField(max_length=100, null=False, blank=False)
    user_last_name = models.CharField(max_length=100, null=False, blank=False)
    user_email = models.EmailField(null=False, blank=False)
    user_phone_number = models.CharField(null=True, blank=True, max_length=13)

    booking_id = models.CharField(unique=True, max_length=12, blank=False, null=False)
    location_code = models.CharField(null=False, blank=False, max_length=100)
    location_name = models.CharField(null=False, blank=False, max_length=250)

    created_date = models.DateField(null=False, blank=False)
    created_time = models.TimeField(null=False, blank=False)

    class Meta:
        verbose_name = 'U-Enter Booking'
        verbose_name_plural = 'U-Enter Bookings'

    def __str__(self):
        return self.booking_id


class U_Enter_Bookings_Details(models.Model):
    location_booking = models.OneToOneField(C_Space_Modera_Bookings, on_delete=models.CASCADE,
                                            related_name='u_enter_bookings_details')
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
        verbose_name = 'U-Enter Bookings Detail'
        verbose_name_plural = 'U-Enter Bookings Details'

    def __str__(self):
        return f'Location Booking Details of {self.location_booking.booking_id}'


# Impact Coworking
class Impact_Coworking_Bookings(models.Model):
    user_first_name = models.CharField(max_length=100, null=False, blank=False)
    user_last_name = models.CharField(max_length=100, null=False, blank=False)
    user_email = models.EmailField(null=False, blank=False)
    user_phone_number = models.CharField(null=True, blank=True, max_length=13)

    booking_id = models.CharField(unique=True, max_length=12, blank=False, null=False)
    location_code = models.CharField(null=False, blank=False, max_length=100)
    location_name = models.CharField(null=False, blank=False, max_length=250)

    created_date = models.DateField(null=False, blank=False)
    created_time = models.TimeField(null=False, blank=False)

    class Meta:
        verbose_name = 'Impact Coworking Booking'
        verbose_name_plural = 'Impact Coworking Bookings'

    def __str__(self):
        return self.booking_id


class Impact_Coworking_Bookings_Details(models.Model):
    location_booking = models.OneToOneField(C_Space_Modera_Bookings, on_delete=models.CASCADE,
                                            related_name='impact_coworking_bookings_details')
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
        verbose_name = 'Impact Coworking Bookings Detail'
        verbose_name_plural = 'Impact Coworking Bookings Details'

    def __str__(self):
        return f'Location Booking Details of {self.location_booking.booking_id}'


# Impulse Coworking
class Impulse_Coworking_Bookings(models.Model):
    user_first_name = models.CharField(max_length=100, null=False, blank=False)
    user_last_name = models.CharField(max_length=100, null=False, blank=False)
    user_email = models.EmailField(null=False, blank=False)
    user_phone_number = models.CharField(null=True, blank=True, max_length=13)

    booking_id = models.CharField(unique=True, max_length=12, blank=False, null=False)
    location_code = models.CharField(null=False, blank=False, max_length=100)
    location_name = models.CharField(null=False, blank=False, max_length=250)

    created_date = models.DateField(null=False, blank=False)
    created_time = models.TimeField(null=False, blank=False)

    class Meta:
        verbose_name = 'Impulse Coworking Booking'
        verbose_name_plural = 'Impulse Coworking Bookings'

    def __str__(self):
        return self.booking_id


class Impulse_Coworking_Bookings_Details(models.Model):
    location_booking = models.OneToOneField(C_Space_Modera_Bookings, on_delete=models.CASCADE,
                                            related_name='impulse_coworking_bookings_details')
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
        verbose_name = 'Impulse Coworking Bookings Detail'
        verbose_name_plural = 'Impulse Coworking Bookings Details'

    def __str__(self):
        return f'Location Booking Details of {self.location_booking.booking_id}'


# HUB Coworking
class Hub_Coworking_Bookings(models.Model):
    user_first_name = models.CharField(max_length=100, null=False, blank=False)
    user_last_name = models.CharField(max_length=100, null=False, blank=False)
    user_email = models.EmailField(null=False, blank=False)
    user_phone_number = models.CharField(null=True, blank=True, max_length=13)

    booking_id = models.CharField(unique=True, max_length=12, blank=False, null=False)
    location_code = models.CharField(null=False, blank=False, max_length=100)
    location_name = models.CharField(null=False, blank=False, max_length=250)

    created_date = models.DateField(null=False, blank=False)
    created_time = models.TimeField(null=False, blank=False)

    class Meta:
        verbose_name = 'HUB Coworking Booking'
        verbose_name_plural = 'HUB Coworking Bookings'

    def __str__(self):
        return self.booking_id


class Hub_Coworking_Bookings_Details(models.Model):
    location_booking = models.OneToOneField(C_Space_Modera_Bookings, on_delete=models.CASCADE,
                                            related_name='hub_coworking_bookings_details')
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
        verbose_name = 'HUB Coworking Bookings Detail'
        verbose_name_plural = 'HUB Coworking Bookings Details'

    def __str__(self):
        return f'Location Booking Details of {self.location_booking.booking_id}'


# BB Works
class Bb_Works_Bookings(models.Model):
    user_first_name = models.CharField(max_length=100, null=False, blank=False)
    user_last_name = models.CharField(max_length=100, null=False, blank=False)
    user_email = models.EmailField(null=False, blank=False)
    user_phone_number = models.CharField(null=True, blank=True, max_length=13)

    booking_id = models.CharField(unique=True, max_length=12, blank=False, null=False)
    location_code = models.CharField(null=False, blank=False, max_length=100)
    location_name = models.CharField(null=False, blank=False, max_length=250)

    created_date = models.DateField(null=False, blank=False)
    created_time = models.TimeField(null=False, blank=False)

    class Meta:
        verbose_name = 'BB Works Booking'
        verbose_name_plural = 'BB Works Bookings'

    def __str__(self):
        return self.booking_id


class Bb_Works_Bookings_Details(models.Model):
    location_booking = models.OneToOneField(C_Space_Modera_Bookings, on_delete=models.CASCADE,
                                            related_name='Bb_works_bookings_details')
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
        verbose_name = 'BB Works Bookings Detail'
        verbose_name_plural = 'BB Works Bookings Details'

    def __str__(self):
        return f'Location Booking Details of {self.location_booking.booking_id}'


# Wiut
class Wiut_Bookings(models.Model):
    user_first_name = models.CharField(max_length=100, null=False, blank=False)
    user_last_name = models.CharField(max_length=100, null=False, blank=False)
    user_email = models.EmailField(null=False, blank=False)
    user_phone_number = models.CharField(null=True, blank=True, max_length=13)

    booking_id = models.CharField(unique=True, max_length=12, blank=False, null=False)
    location_code = models.CharField(null=False, blank=False, max_length=100)
    location_name = models.CharField(null=False, blank=False, max_length=250)

    created_date = models.DateField(null=False, blank=False)
    created_time = models.TimeField(null=False, blank=False)

    class Meta:
        verbose_name = 'Wiut Booking'
        verbose_name_plural = 'Wiut Bookings'

    def __str__(self):
        return self.booking_id


class Wiut_Bookings_Details(models.Model):
    location_booking = models.OneToOneField(C_Space_Modera_Bookings, on_delete=models.CASCADE,
                                            related_name='wiut_bookings_details')
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
        verbose_name = 'Wiut Bookings Detail'
        verbose_name_plural = 'Wiut Bookings Details'

    def __str__(self):
        return f'Location Booking Details of {self.location_booking.booking_id}'
