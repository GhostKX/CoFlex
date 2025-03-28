from django.db import models
from .sand_subscribed_users import SubscribedUsers


# Locations table storing the data of all locations
class Locations(models.Model):
    location_name = models.CharField(null=False, blank=False, max_length=250)
    location_code = models.CharField(unique=True, null=False, blank=False, max_length=100)
    location_latitude = models.FloatField(null=False, blank=False)
    location_longitude = models.FloatField(null=False, blank=False)
    icon_path = models.CharField(null=False, blank=False, max_length=250, default='/static/CoFlex_app/icons/bb.png')

    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    def __str__(self):
        return self.location_code


# Location Details table storing details of the locations
class LocationDetails(models.Model):
    location = models.OneToOneField(Locations, on_delete=models.CASCADE, related_name='location_details')
    address = models.CharField(null=False, blank=False, max_length=250)
    contact_phone = models.CharField(null=False, blank=False, max_length=250)
    working_hours = models.CharField(null=False, blank=False, max_length=250)
    image_path = models.CharField( null=False, blank=False, max_length=250, default='/static/CoFlex_app/location_images/bb.jpg')
    website = models.URLField(null=False, blank=False, max_length=250)
    default_availability = models.IntegerField(null=False, blank=False)

    class Meta:
        verbose_name = 'Location Detail'
        verbose_name_plural = 'Locations Details'

    def __str__(self):
        return f'Location Details of {self.location.location_code}'


# Location Availability table storing availability of the locations
class LocationAvailability(models.Model):
    location = models.ForeignKey(Locations, on_delete=models.CASCADE, related_name='location_availability')
    date = models.DateField(blank=False, null=False)
    availability = models.IntegerField(blank=False, null=True, default=0)

    class Meta:
        verbose_name = 'Location Availability'
        verbose_name_plural = 'Locations Availabilities'
        unique_together = ('location', 'date')  # Preventing duplicate location and date a pair of variables

    def __str__(self):
        return f'Location Availability of {self.location.location_code}'


# Booking table storing the bookings of the users
class Booking(models.Model):
    user = models.ForeignKey(SubscribedUsers, on_delete=models.CASCADE, related_name='booking')
    location = models.ForeignKey(Locations, on_delete=models.CASCADE)
    booking_id = models.CharField(unique=True, max_length=12, blank=False, null=False)
    created_date = models.DateField(null=False, blank=False)
    created_time = models.TimeField(null=False, blank=False)

    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'

    def __str__(self):
        return self.booking_id


# Details of the bookings
class BookingDetails(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='booking_details')
    start_date = models.DateField(null=False, blank=False)
    start_time = models.TimeField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)
    end_time = models.TimeField(null=False, blank=False)

    duration = models.DecimalField(null=True, blank=True, max_digits=3, decimal_places=2)
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)

    special_requests = models.CharField(null=False, blank=False, max_length=150, default='No Requests')
    status = models.CharField(max_length=20, choices=[
        ('Booked', 'Booked'),
        ('In Progress', 'In Progress'),
        ('Finished', 'Finished'),
        ('Due Out', 'Due Out'),
        ('Cancelled', 'Cancelled'),
    ], default='Booked')

    class Meta:
        verbose_name = 'Booking Details'
        verbose_name_plural = 'Bookings Details'

    def __str__(self):
        return self.booking.booking_id