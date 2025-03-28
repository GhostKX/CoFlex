from django import forms
from django.utils.timezone import localtime, localdate, make_aware
import datetime
from ..models import SubscribedUsers, Booking, BookingDetails, Locations, LocationDetails, LocationAvailability


class ThirtyMinuteTimeInput(forms.Select):
    """
        Custom Time Input for the user that would let the user
        input the time in 30 minutes range in a more user-friendly 12-hour AM/PM format for display.
    """
    def __init__(self, attrs=None):
        choices = []
        for hour in range(0, 24):
            for minute in [0, 30]:
                time_str = f'{hour:02d}:{minute:02d}'
                # Improving the display format for the user
                hour_12 = hour % 12
                if hour_12 == 0:
                    hour_12 = 12
                ampm = 'AM' if hour < 12 else 'PM'
                display_str = f'{hour_12}:{minute:02d} {ampm}'
                choices.append((time_str, display_str))

        # Adding classes for the front
        if attrs is None:
            attrs = {}
        attrs['class'] = attrs.get('class', '') + ' time-select'

        super().__init__(attrs=attrs, choices=choices)

    def format_value(self, value):
        if value is None:
            return ''  # Returning empty string for empty values
        if isinstance(value, datetime.time):
            return f'{value.hour:02d}:{value.minute:02d}'
        return str(value)  # In any case the function returns the string


class BookingLocationForm(forms.ModelForm):
    """
        Form for booking a location:

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

    # Getting user and location as instances for the further fields validation
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.location = kwargs.pop('location', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = BookingDetails
        fields = ['start_date', 'start_time', 'end_time', 'special_requests']

    # Validation for the date of the booking
    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')

        if start_date:
            if start_date < localdate():
                raise forms.ValidationError('Booking Date cannot be in the past!')

            if self.user:
                try:
                    subscribed_user = SubscribedUsers.objects.get(user=self.user)
                except Exception as e:
                    raise forms.ValidationError('Error, Only Subscribed Users can book a location!')

                if subscribed_user:
                    existing_booking = Booking.objects.filter(user=subscribed_user,
                                                              booking_details__start_date=start_date).exclude(booking_details__status__in=['Due Out', 'Cancelled']).exists()
                    if existing_booking:
                        raise forms.ValidationError(
                            'You already have a booking on this date. Only one booking per day is allowed!')

                    location_availability_table = LocationAvailability.objects.filter(location=self.location,
                                                                                      date=start_date).first()
                    if not location_availability_table:
                        location_availability_table = LocationAvailability.objects.create(
                            location=self.location,
                            date=start_date,
                            availability=self.location.location_details.default_availability
                        )

                    if location_availability_table.availability == 0:
                        raise forms.ValidationError("No available places for that day!")

        return start_date

    # Validation for the check in time
    def clean_start_time(self):
        start_date = self.cleaned_data.get('start_date')
        start_time = self.cleaned_data.get('start_time')

        if start_date is None or start_time is None:
            return start_time  # Avoiding validation if the booking date is None

        current_datetime = localtime()
        selected_datetime = datetime.datetime.combine(start_date, start_time)
        selected_datetime = make_aware(selected_datetime)

        if selected_datetime < current_datetime:
            raise forms.ValidationError('Check In time cannot be in the past!')

        if start_time and start_time.minute not in [0, 30]:
            raise forms.ValidationError('Check In time must be either on the hour or half hour!')

        return start_time

    # Validation for the check-out time
    def clean_end_time(self):
        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data.get('end_time')

        if end_time and end_time.minute not in [0, 30]:
            raise forms.ValidationError('Check Out time must be either on the hour or half hour!')

        if start_time and end_time:

            # Calculating duration for validation
            start_datetime = datetime.datetime.combine(localdate(), start_time)
            end_datetime = datetime.datetime.combine(localdate(), end_time)

            # Assuming if check out time is earlier than the check in time
            # then the date when the booking ends 'end_date' is next day
            if end_datetime <= start_datetime:
                end_datetime += datetime.timedelta(days=1)
                self.cleaned_data['end_date'] = end_datetime.date()

            duration = (end_datetime - start_datetime).total_seconds() / 3600  # duration in hours

            if duration < 3:
                raise forms.ValidationError('Booking must be at least 3 hours!')
            elif duration > 8:
                raise forms.ValidationError('Booking cannot exceed 8 hours!')

        return end_time

    # Validation for the special requests from the user
    def clean_special_requests(self):
        special_requests = self.cleaned_data.get('special_requests')

        if not special_requests:
            special_requests = 'No Requests'
            return special_requests

        # Validating length of the field
        if len(special_requests) > 150:
            raise forms.ValidationError('Special Request field cannot exceed 150 characters!')

        return special_requests


