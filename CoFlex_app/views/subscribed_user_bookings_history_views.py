from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, reverse
from django.shortcuts import render
from django.conf import settings
from ..models import VerifiedUsers, SubscribedUsers, Booking, BookingDetails, LocationAvailability
from ..forms.subscribed_user_bookings_history_forms import SubscribedUserBookingDetailsForm
from .user_recent_actions_views import user_device_activity
from .email_functions import send_booking_cancellation_email


@login_required
def subscribed_user_all_bookings(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    subscribed_user = SubscribedUsers.objects.filter(user=user).first()
    if subscribed_user:
        users_all_bookings = Booking.objects.filter(user=subscribed_user).order_by('-booking_details__start_date')

        all_user_bookings_list = []
        for booking in users_all_bookings:
            booking_details = getattr(booking, 'booking_details', None)
            all_user_bookings_list.append({
                'booking': booking,
                'booking_details': booking_details
            })

        context = {
            'user': user,
            'all_user_bookings_list': all_user_bookings_list
        }
    else:
        context = {
            'user': user
        }

    return render(request, 'subscribed_user_bookings_history/subscribed_user_bookings_history.html', context)


@login_required
def subscribed_user_booking_details(request, user_id, booking_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    booking = get_object_or_404(Booking, booking_id=booking_id)
    booking_details = get_object_or_404(BookingDetails, booking=booking)
    location = booking.location

    original_start_date = booking_details.start_date

    if request.method == 'POST':
        form = SubscribedUserBookingDetailsForm(request.POST, user=user, location=location, booking=booking)
        if form.is_valid():
            changed_details = {}
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            start_time = form.cleaned_data.get('start_time')
            end_time = form.cleaned_data.get('end_time')
            special_requests = form.cleaned_data.get('special_requests')

            if (booking_details.start_date == start_date
                    and booking_details.start_time == start_time
                    and booking_details.end_time == end_time
                    and booking_details.special_requests == special_requests):
                messages.info(request, f"No changed were made of booking {booking_id}!")
            else:
                if booking_details.start_date != start_date:
                    changed_details = {'Check In Date': {'old': str(booking_details.start_date), 'new': str(start_date)},
                                       'Check Out Date': {'old': str(booking_details.end_date), 'new': str(end_date)}}

                    old_availability = LocationAvailability.objects.filter(location=location,
                                                                           date=original_start_date).first()
                    if old_availability:
                        old_availability.availability += 1
                        old_availability.save()

                    new_availability = LocationAvailability.objects.get(location=location, date=start_date)
                    if new_availability.availability > 0:
                        new_availability.availability -= 1
                        new_availability.save()

                if booking_details.start_time != start_time:
                    changed_details['Check In Time'] = {'old': str(booking_details.start_time), 'new': str(start_time)}

                if booking_details.end_time != end_time:
                    changed_details['Check Out Time'] = {'old': str(booking_details.end_time), 'new': str(end_time)}

                if booking_details.special_requests != special_requests:
                    changed_details['Special Requests'] = {'old': booking_details.special_requests,
                                                           'new': special_requests}

                if changed_details:
                    user_device_activity(instance=user, request=request,
                                         activity_type=f'Changed Booking Details of {booking_id}',
                                         activity_details=changed_details)

                booking_details.start_date = start_date
                booking_details.end_date = end_date
                booking_details.start_time = start_time
                booking_details.end_time = end_time
                booking_details.special_requests = special_requests
                booking_details.save()  # This save triggers a signal

                messages.success(request, f"Booking details of {booking_id} updated successfully!")

            return redirect('subscribed_user_all_bookings', user_id=user_id)

    else:
        initial_data = {
            'start_date': booking_details.start_date,
            'start_time': booking_details.start_time,
            'end_time': booking_details.end_time,
            'special_requests': booking_details.special_requests,
        }
        form = SubscribedUserBookingDetailsForm(initial=initial_data, user=user, location=location, booking=booking)

    context = {
        'form': form,
        'user': user,
        'booking': booking,
        'booking_details': booking_details,
        'location': location
    }

    return render(request, 'subscribed_user_bookings_history/subscribed_user_booking_details.html', context)


@login_required
def subscribed_user_cancel_booking(request, user_id, booking_id):
    if request.method == 'POST':
        user = get_object_or_404(VerifiedUsers, id=user_id)
        booking = get_object_or_404(Booking, booking_id=booking_id)
        booking_details = booking.booking_details
        location = booking.location

        booking_details.status = 'Cancelled'
        booking_details.save()

        location_availability = LocationAvailability.objects.filter(location=location,
                                                                    date=booking_details.start_date).first()
        if location_availability:
            if location_availability.availability == location.location_details.default_availability:
                pass
            else:
                location_availability.availability += 1
                location_availability.save()

            user_device_activity(instance=user, request=request, activity_type=f'Cancelled Booking {booking_id}',
                                 activity_details={})

            send_booking_cancellation_email(user=user,
                                            sender_email=settings.EMAIL_HOST_USER,
                                            recipient_email=user.email,
                                            booking=booking,
                                            booking_details=booking_details,
                                            location=location)

            messages.success(request, f"Booking {booking_id} has been cancelled successfully!")

    return redirect('subscribed_user_all_bookings', user_id=user_id)
