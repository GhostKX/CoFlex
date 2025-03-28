from datetime import date, time
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, reverse
from django.shortcuts import render
from django.utils.html import escape
from django.utils.timezone import now, localdate
from django.http import JsonResponse
from geopy.distance import geodesic
import random
import string
from datetime import datetime
from ..models import VerifiedUsers, SubscribedUsers, Locations, LocationDetails, LocationAvailability, Booking, BookingDetails
from ..forms.subscribed_user_booking_location_forms import BookingLocationForm
from .user_recent_actions_views import user_device_activity


@login_required
def locations(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)

    # Getting locations by category
    c_space_locations = Locations.objects.filter(location_name__icontains='c-space')
    ground_zero_locations = Locations.objects.filter(location_name__icontains='ground zero')
    other_locations = (Locations.objects.filter(
        location_name__icontains='impulse') | Locations.objects.filter(location_name__icontains='bb')
                       | Locations.objects.filter(location_name__icontains='hub') | Locations.objects.filter(location_name__icontains='u-enter')
                       | Locations.objects.filter(location_name__icontains='Westminster') | Locations.objects.filter(location_name__icontains='Impact'))

    # Preparing all locations data for the map
    all_locations_data = []
    for location in Locations.objects.all():
        today_availability = location.location_availability.filter(date=localdate().today()).first()
        if not today_availability:
            today_availability = LocationAvailability.objects.create(
                location=location,
                date=localdate().today(),
                availability=location.location_details.default_availability
            )

        available_spots = today_availability.availability

        booking_url = reverse('booking_location', kwargs={'user_id': user_id, 'location_code': location.location_code})

        location_data = {
            'latitude': float(location.location_latitude),
            'longitude': float(location.location_longitude),
            'location_code': location.location_code,
            'name': location.location_name,
            'icon_path': location.icon_path,
            'address': location.location_details.address,
            'contact_phone': location.location_details.contact_phone,
            'working_hours': location.location_details.working_hours,
            'image_path': location.location_details.image_path,
            'website': location.location_details.website,
            'available_spots': available_spots,
            'booking_url': booking_url
        }

        all_locations_data.append(location_data)

    context = {
        'user': user,
        'c_space_locations': c_space_locations,
        'ground_zero_locations': ground_zero_locations,
        'other_locations': other_locations,
        'all_locations_data': all_locations_data,
    }

    return render(request, 'subscribed_user_booking/subscribed_user_booking_locations.html', context)


@login_required
def get_user_location(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')

    user_location = (float(latitude), float(longitude))
    distance_locations = {}
    locations = Locations.objects.all()
    for location in locations:
        specific_location = (location.location_latitude, location.location_longitude)
        distance = geodesic(user_location, specific_location).km

        # Getting today's availability
        today_availability = location.location_availability.filter(date=localdate().today()).first()
        available_spots = (today_availability.availability
                           if today_availability
                           else location.location_details.default_availability)
        booking_url = reverse('booking_location', kwargs={'user_id': user_id, 'location_code': location.location_code})

        distance_locations[location.location_code] = {
            'user_id': user_id,
            'distance_km': round(distance, 2),
            'latitude': float(location.location_latitude),
            'longitude': float(location.location_longitude),
            'location_code': location.location_code,
            'name': location.location_name,
            'icon_path': location.icon_path,
            'address': location.location_details.address,
            'contact_phone': location.location_details.contact_phone,
            'working_hours': location.location_details.working_hours,
            'image_path': location.location_details.image_path,
            'website': location.location_details.website,
            'available_spots': available_spots,
            'booking_url': booking_url
        }

    nearest_locations = sorted(distance_locations.items(), key=lambda x: x[1]['distance_km'])[:3]
    all_locations = sorted(distance_locations.items())

    return JsonResponse({'nearest_locations': nearest_locations, 'all_locations': all_locations})


@login_required
def booking_location(request, user_id, location_code):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    location = get_object_or_404(Locations, location_code=location_code)
    location_availability = get_object_or_404(LocationAvailability, location=location, date=localdate().today())

    if request.method == 'POST':
        form = BookingLocationForm(request.POST, user=user, location=location)
        if form.is_valid():
            subscribed_user = SubscribedUsers.objects.get(user=user)

            def generate_booking_id():
                while True:
                    booking_id = ''
                    for i in range(6):
                        letter = random.choice(string.ascii_letters)
                        number = random.choice(string.digits)

                        booking_id += letter + number

                    if not Booking.objects.filter(booking_id=booking_id).exists():
                        return booking_id

            booking_id = generate_booking_id()

            booking = Booking.objects.create(
                user=subscribed_user,
                location=location,
                booking_id=booking_id,
                created_date=date.today(),
                created_time=now().time()
            )

            end_date = form.cleaned_data.get('end_date') or form.cleaned_data['start_date']
            booking_details = BookingDetails.objects.create(
                booking=booking,
                start_date=form.cleaned_data['start_date'],
                start_time=form.cleaned_data['start_time'],
                end_date=end_date,
                end_time=form.cleaned_data['end_time'],
                special_requests=form.cleaned_data['special_requests'],
                status='Booked'
            )

            try:
                send_mail('Booking Confirmation',
                          f'<p>Message to {escape(user.email)}',
                          'settings.EMAIL_HOST_USER',
                          [user.email],
                          fail_silently=False,
                          html_message=f"""
                                  <html>
                                  <body style="font-family: Arial, sans-serif; font-size: 16px; color: #333; line-height: 1.6;">
                                      <h2 style="color: #007BFF;">Hello {escape(user.first_name)} {escape(user.last_name)},</h2>

                                      <p>We are pleased to confirm your booking at <b>{escape(location.location_name)}</b> 🎉</p>

                                      <h3 style="color: #28A745;">Booking Details 📅</h3>
                                      <ul>
                                          <li><b>Booking Created:</b> {booking.created_date} at {booking.created_time.strftime('%H:%M:%S')}</li>
                                          <li><b>Location:</b> {escape(location.location_name)}</li>
                                          <li><b>Address:</b> {escape(location.location_details.address)}</li>
                                          <li><b>Contact:</b> {escape(location.location_details.contact_phone)}</li>
                                          <li><b>Website:</b> <a href="{escape(location.location_details.website)}" target="_blank">{escape(location.location_details.website)}</a></li>
                                      </ul>

                                      <h3 style="color: #DC3545;">Scheduled Timing ⏰</h3>
                                      <ul>
                                          <li><b>Date:</b> {booking_details.start_date}</li>
                                          <li><b>From:</b> {booking_details.start_time}</li>
                                          <li><b>To:</b> {booking_details.end_time}</li>
                                      </ul>

                                      <p>If you have any questions, feel free to contact us.</p>
                                      <p>We look forward to seeing you!</p>

                                      <p style="margin-top: 20px; font-size: 14px; color: #555;">
                                          <i>This is an automated email, please do not reply.</i>
                                      </p>
                                  </body>
                                  </html>
                                  """
                          )
            except Exception as e:
                messages.error(request, f'Error sending verification email: {e}')

            new_location_availability_table = LocationAvailability.objects.get(location=location, date=booking_details.start_date)

            new_location_availability_table.availability -= 1
            new_location_availability_table.save()

            user_device_activity(instance=user, request=request, activity_type=f'New Booking {booking_id}',
                                 activity_details={})

            messages.success(request, "Booking successfully created!")
            return redirect('subscribed_user_all_bookings', user_id=user_id)
    else:
        initial_data = {
            'start_time': time(9, 0),  # 9:00 AM
            'end_time': time(12, 0),  # 12:00 PM
        }
        form = BookingLocationForm(initial=initial_data, user=user, location=location)

    return render(request, 'subscribed_user_booking/booking_location.html',
                  {'form': form, 'user': user, 'location': location, 'location_availability': location_availability})


