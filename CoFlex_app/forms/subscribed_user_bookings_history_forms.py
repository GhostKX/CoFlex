from django import forms
from django.utils.timezone import localtime, localdate, make_aware
import datetime
from datetime import timedelta
from ..models import SubscribedUsers, Booking, BookingDetails, LocationAvailability
from .subscribed_user_booking_location_forms import ThirtyMinuteTimeInput


class SubscribedUserBookingDetailsForm(forms.ModelForm):
    """
        Form for editing booking details:

        start_date: Date when the booking is planned
        start_time: Check in time of the booking
        end_time: Check out time of the booking
        special_requests: Field for the requests from the user
    """

    start_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    start_time = forms.TimeField(
        required=True,
        widget=ThirtyMinuteTimeInput(attrs={'class': 'form-control'})
    )
    end_time = forms.TimeField(
        required=True,
        widget=ThirtyMinuteTimeInput(attrs={'class': 'form-control'})
    )

    special_requests = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional requests'}),
    )

    # Getting user, location and booking as instances for the further fields validation
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.location = kwargs.pop('location')
        self.booking = kwargs.pop('booking')
        super().__init__(*args, **kwargs)

    class Meta:
        model = BookingDetails
        fields = ['start_date', 'start_time', 'end_time', 'special_requests']

    # Validation for the date of the booking
    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')

        original_start_date = self.booking.booking_details.start_date

        if not start_date:
            raise forms.ValidationError("Date can not be empty!")

        if start_date != original_start_date and start_date <= localdate() + timedelta(days=1):
            raise forms.ValidationError("You can only change the start date at least 24 hours before!")

        if start_date < localdate():
            raise forms.ValidationError('Booking Date cannot be in the past!')

        if self.user:
            try:
                subscribed_user = SubscribedUsers.objects.get(user=self.user)
            except Exception as e:
                raise forms.ValidationError('Error, Only Subscribed Users can edit booking details!')

            if subscribed_user:
                existing_booking = Booking.objects.filter(user=subscribed_user,
                                                          booking_details__start_date=start_date).exclude(id=self.booking.id).exclude(booking_details__status__in=['Due Out', 'Cancelled']).exists()
                if existing_booking:
                    raise forms.ValidationError(
                        'You already have a booking on this date. Only one booking per day is allowed!')

                # Getting the availability record or creating one if there is none
                location_availability_table, created = LocationAvailability.objects.get_or_create(
                    location=self.location,
                    date=start_date,
                    defaults={'availability': self.location.location_details.default_availability}
                )

                # Checking if the existing availability is not 0
                if location_availability_table.availability <= 0:
                    raise forms.ValidationError("No available places for that day!")

        return start_date

    # Validation for the check in time
    def clean_start_time(self):
        start_date = self.cleaned_data.get('start_date')
        start_time = self.cleaned_data.get('start_time')

        if start_date is None or start_time is None:
            return start_time  # Avoiding validation if date is missing

        if self.booking.booking_details.start_date == localdate() and start_time:
            aware_start_time = make_aware(
                datetime.datetime.combine(localdate(), start_time))  # Combining the booking date and check in time as a one datetime
            if self.booking.booking_details.start_date != start_date and localtime() > aware_start_time - timedelta(hours=6):
                raise forms.ValidationError("You can only edit the start time 6 hours before the booking starts!")

        return start_time

    # Validation for the check-out time
    def clean_end_time(self):
        start_date = self.cleaned_data.get('start_date')
        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data.get('end_time')

        if start_time and end_time:

            duration = (datetime.datetime.combine(localdate(), end_time) - datetime.datetime.combine(localdate(), start_time)).seconds / 3600
            if duration < 3:
                raise forms.ValidationError("The booking duration must be at least 3 hours!")
            if duration > 8:
                raise forms.ValidationError("The booking duration cannot exceed 8 hours!")

            if start_date:
                # Checking if end_time is earlier than start_time then it means booking crosses midnight
                if end_time < start_time:
                    self.cleaned_data['end_date'] = start_date + timedelta(days=1)  # Next day
                else:
                    self.cleaned_data['end_date'] = start_date  # Same day

        return end_time

    # Validation for the special requests from the user
    def clean_special_requests(self):
        start_date = self.cleaned_data.get('start_date')
        start_time = self.cleaned_data.get('start_time')
        special_requests = self.cleaned_data['special_requests']

        if not special_requests:
            special_requests = "No Requests"

        if start_date == localdate() and start_time:
            aware_start_time = make_aware(datetime.datetime.combine(localdate(), start_time))
            if localtime() > aware_start_time - timedelta(hours=6):
                raise forms.ValidationError("You can only edit special requests up to 3 hours before the booking starts!")

        return special_requests


