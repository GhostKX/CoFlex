from django.db import models
from CoFlex_app.models import SubscribedUsers, Locations


# All Bookings table to store all users' bookings
class AllBookings(models.Model):
    user = models.ForeignKey(SubscribedUsers, on_delete=models.CASCADE, related_name='all_bookings')
    location = models.ForeignKey(Locations, on_delete=models.CASCADE, related_name='all_bookings')
    booking_id = models.CharField(unique=True, max_length=12, blank=False, null=False)
    created_date = models.DateField(null=False, blank=False)
    created_time = models.TimeField(null=False, blank=False)

    class Meta:
        verbose_name = 'All Booking'
        verbose_name_plural = 'All Bookings'

    def __str__(self):
        return f"Booking by {self.user.user.email} at {self.location.location_code}"


# All bookings details table
class AllBookingDetails(models.Model):
    all_booking = models.OneToOneField(AllBookings, on_delete=models.CASCADE, related_name='all_booking_details')
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
        ('Canceled', 'Canceled'),
    ], default='Booked')

    class Meta:
        verbose_name = 'All Booking Details'
        verbose_name_plural = 'All Bookings Details'

    def __str__(self):
        return f'All Booking Details of {self.all_booking.user.user.email}'
