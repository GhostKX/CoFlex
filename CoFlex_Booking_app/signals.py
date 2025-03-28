from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from django.utils import timezone
from .models import AllBookings, AllBookingDetails
from CoFlex_app.models import (Booking, BookingDetails, VerifiedUsers,
                               UserSignUpLoginLogoutActivity)
from CoFlex_Staff_app.models import StaffAccounts, StaffSignUpLoginLogoutActivity
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.conf import settings
import ipaddress
import ipinfo
from django_user_agents.utils import get_user_agent


def get_user_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")

    try:
        ipaddress.ip_address(ip)
        return ip
    except ValueError:
        return None


def get_user_device_details(request):
    user_agent = get_user_agent(request)
    device_type = ''
    if user_agent.is_mobile:
        device_type = 'Mobile Phone'
    elif user_agent.is_tablet:
        device_type = 'Tablet'
    elif user_agent.is_pc:
        device_type = 'PC/Laptop'
    elif user_agent.is_bot:
        device_type = 'Bot'
    else:
        device_type = 'Unknown'

    browser = user_agent.browser.family or 'Unknown'
    operating_system = user_agent.os.family or 'Unknown'

    device_name = user_agent.device.family
    if not device_name or device_name.lower() == "other":
        device_name = user_agent.os.family

    return {
        'device_type': device_type,
        'browser': browser,
        'operating_system': operating_system,
        'device_name': device_name
    }


def get_user_location_details(request):
    user_ip_address = get_user_ip(request)
    if user_ip_address:
        access_token = str(settings.LOCATION_ACCESS_TOKEN)
        handler = ipinfo.getHandler(access_token)
        user_location_details = handler.getDetails()

        user_ip = user_location_details.ip
        user_city = user_location_details.city
        user_region = user_location_details.region
        user_country = user_location_details.country_name
        user_organization = user_location_details.org
        user_latitude = user_location_details.latitude
        user_longitude = user_location_details.longitude

        return {
            'user_ip': user_ip,
            'user_city': user_city,
            'user_region': user_region,
            'user_country': user_country,
            'user_organization': user_organization,
            'user_latitude': user_latitude,
            'user_longitude': user_longitude
        }

    return {}


@receiver(user_logged_in)
def user_log_in_activity(sender, request, user, **kwargs):
    user_ip_address = get_user_ip(request)
    if user_ip_address:

        device_details = get_user_device_details(request)
        location_details = get_user_location_details(request)

        user_ip = location_details.get('user_ip', user_ip_address)
        user_city = location_details.get('user_city', 'Unknown')
        user_region = location_details.get('user_region', 'Unknown')
        user_country = location_details.get('user_country', 'Unknown')
        user_organization = location_details.get('user_organization', 'Unknown')
        user_latitude = location_details.get('user_latitude', None)
        user_longitude = location_details.get('user_longitude', None)

        if isinstance(user, VerifiedUsers):
            if not request.session.session_key:
                while True:
                    request.session.create()
                    session_key = request.session.session_key

                    if not UserSignUpLoginLogoutActivity.objects.filter(session_key=session_key).exists():
                        return session_key
            session_key = request.session.session_key

            UserSignUpLoginLogoutActivity.objects.create(
                user=user,
                session_key=session_key,
                ip_address=user_ip,
                device_type=device_details['device_type'],
                browser=device_details['browser'],
                operating_system=device_details['operating_system'],
                device_name=device_details['device_name'],
                organization=user_organization,
                city=user_city,
                region=user_region,
                country=user_country,
                latitude=user_latitude,
                longitude=user_longitude,
                date_time=timezone.now(),
                is_Logged_in=True,
                action='Login'
            )

        elif isinstance(user, StaffAccounts):
            if not request.session.session_key:
                while True:
                    request.session.create()
                    session_key = request.session.session_key

                    if not UserSignUpLoginLogoutActivity.objects.filter(session_key=session_key).exists():
                        return session_key
            session_key = request.session.session_key

            StaffSignUpLoginLogoutActivity.objects.create(
                staff=user,
                session_key=session_key,
                ip_address=user_ip,
                device_type=device_details['device_type'],
                browser=device_details['browser'],
                operating_system=device_details['operating_system'],
                device_name=device_details['device_name'],
                city=user_city,
                region=user_region,
                country=user_country,
                organization=user_organization,
                latitude=user_latitude,
                longitude=user_longitude,
                date_time=timezone.now(),
                is_Logged_in=True,
                action='Login'
            )


@receiver(user_logged_out)
def user_log_out_activity(sender, request, user, **kwargs):
    user_ip_address = get_user_ip(request)
    if user_ip_address:

        session_key = request.session.session_key

        device_details = get_user_device_details(request)
        location_details = get_user_location_details(request)

        user_ip = location_details.get('user_ip', user_ip_address)
        user_city = location_details.get('user_city', 'Unknown')
        user_region = location_details.get('user_region', 'Unknown')
        user_country = location_details.get('user_country', 'Unknown')
        user_organization = location_details.get('user_organization', 'Unknown'),
        user_latitude = location_details.get('user_latitude', None)
        user_longitude = location_details.get('user_longitude', None)

        if isinstance(user, VerifiedUsers):
            user_session = UserSignUpLoginLogoutActivity.objects.filter(user=user, session_key=session_key, is_Logged_in=True)
            if user_session.exists():
                user_session.update(is_Logged_in=False)

                UserSignUpLoginLogoutActivity.objects.create(
                    user=user,
                    session_key=session_key,
                    ip_address=user_ip,
                    device_type=device_details['device_type'],
                    browser=device_details['browser'],
                    operating_system=device_details['operating_system'],
                    device_name=device_details['device_name'],
                    city=user_city,
                    region=user_region,
                    country=user_country,
                    organization=user_organization,
                    latitude=user_latitude,
                    longitude=user_longitude,
                    date_time=timezone.now(),
                    is_Logged_in=False,
                    action='Logout'
                )

        elif isinstance(user, StaffAccounts):
            staff_session = StaffSignUpLoginLogoutActivity.objects.filter(staff=user, session_key=session_key, is_Logged_in=True)
            if staff_session.exists():
                staff_session.update(is_Logged_in=False)

                StaffSignUpLoginLogoutActivity.objects.create(
                    staff=user,
                    session_key=session_key,
                    ip_address=user_ip,
                    device_type=device_details['device_type'],
                    browser=device_details['browser'],
                    operating_system=device_details['operating_system'],
                    device_name=device_details['device_name'],
                    city=user_city,
                    region=user_region,
                    country=user_country,
                    organization=user_organization,
                    latitude=user_latitude,
                    longitude=user_longitude,
                    date_time=timezone.now(),
                    is_Logged_in=False,
                    action='Logout'
                )


@receiver(post_save, sender=BookingDetails)
def create_edit_all_booking_data(sender, instance, created, **kwargs):
    booking = instance.booking

    if created:
        all_booking = AllBookings.objects.create(
            user=booking.user,
            location=booking.location,
            booking_id=booking.booking_id,
            created_date=booking.created_date,
            created_time=booking.created_time,
        )

        all_booking_details = AllBookingDetails.objects.create(
            all_booking=all_booking,
            start_date=instance.start_date,
            start_time=instance.start_time,
            end_date=instance.end_date,
            end_time=instance.end_time,
            special_requests=instance.special_requests,
            status=instance.status
        )

        if all_booking and all_booking_details:
            location_code = all_booking.location.location_code

            location_code = f'{location_code.title()}' + '_Bookings'
            location_code_details = f'{location_code.title()}' + '_Details'

            LocationTable = apps.get_model('CoFlex_Staff_app', location_code)
            LocationTableDetails = apps.get_model('CoFlex_Staff_app', location_code_details)

            location_booking_table = LocationTable.objects.create(
                user_first_name=all_booking.user.user.first_name,
                user_last_name=all_booking.user.user.last_name,
                user_email=all_booking.user.user.email,
                user_phone_number=all_booking.user.user.profile.phone_number,
                booking_id=all_booking.booking_id,
                location_code=all_booking.location.location_code,
                location_name=all_booking.location.location_name,
                created_date=all_booking.created_date,
                created_time=all_booking.created_time
            )

            location_booking_table_details = LocationTableDetails.objects.create(
                location_booking=location_booking_table,
                start_date=all_booking_details.start_date,
                start_time=all_booking_details.start_time,
                end_date=all_booking_details.end_date,
                end_time=all_booking_details.end_time,
                special_requests=all_booking_details.special_requests,
                status=all_booking_details.status
            )
    else:

        all_booking = AllBookings.objects.filter(booking_id=booking.booking_id).first()
        if all_booking:
            all_booking.user = booking.user
            all_booking.location = booking.location
            all_booking.created_date = booking.created_date
            all_booking.created_time = booking.created_time
            all_booking.save()

        all_booking_details = AllBookingDetails.objects.filter(all_booking=all_booking).first()
        if all_booking_details:
            all_booking_details.start_date = instance.start_date
            all_booking_details.start_time = instance.start_time
            all_booking_details.end_date = instance.end_date
            all_booking_details.end_time = instance.end_time
            all_booking_details.special_requests = instance.special_requests
            all_booking_details.status = instance.status

            all_booking_details.save()

        if all_booking and all_booking_details:
            location_code = all_booking.location.location_code

            location_code = f'{location_code.title()}' + '_Bookings'
            location_code_details = f'{location_code.title()}' + '_Details'

            LocationTable = apps.get_model('CoFlex_Staff_app', location_code)
            LocationTableDetails = apps.get_model('CoFlex_Staff_app', location_code_details)

            location_booking_table = LocationTable.objects.filter(booking_id=all_booking.booking_id).first()
            if location_booking_table:

                LocationTable.objects.filter(booking_id=all_booking.booking_id).update(
                    user_first_name=all_booking.user.user.first_name,
                    user_last_name=all_booking.user.user.last_name,
                    user_email=all_booking.user.user.email,
                    user_phone_number=all_booking.user.user.profile.phone_number,
                    booking_id=all_booking.booking_id,
                    location_code=all_booking.location.location_code,
                    location_name=all_booking.location.location_name,
                    created_date=all_booking.created_date,
                    created_time=all_booking.created_time,
                )

                LocationTableDetails.objects.filter(location_booking=location_booking_table).update(
                    start_date=all_booking_details.start_date,
                    start_time=all_booking_details.start_time,
                    end_date=all_booking_details.end_date,
                    end_time=all_booking_details.end_time,
                    special_requests=all_booking_details.special_requests,
                    status=all_booking_details.status
                )


@receiver(post_save)
def updating_user_booking_status(sender, instance, created, **kwargs):
    if sender.__name__.endswith('_Bookings_Details'):
        if not created:
            try:
                all_booking = AllBookings.objects.filter(booking_id=instance.location_booking.booking_id).first()
                all_booking_details = AllBookingDetails.objects.filter(all_booking=all_booking).first()

                if all_booking_details and all_booking_details.status != instance.status:
                    all_booking_details.status = instance.status
                    all_booking_details.save()

                    if instance:

                        if all_booking_details.actual_start_time != instance.actual_start_time:
                            all_booking_details.actual_start_time = instance.actual_start_time
                            print(f'After saving: {instance.actual_start_time}')

                        if all_booking_details.actual_end_time != instance.actual_end_time:
                            all_booking_details.actual_end_time = instance.actual_end_time

                        if all_booking_details.duration != instance.duration:
                            all_booking_details.duration = instance.duration

                        all_booking_details.save()
                        print(f'Something: {instance.actual_start_time}')

                booking = Booking.objects.filter(booking_id=instance.location_booking.booking_id).first()
                booking_details = BookingDetails.objects.filter(booking=booking).first()
                if booking_details and booking_details.status != all_booking_details.status:
                    update_fields = {}

                    if booking_details.status != all_booking_details.status:
                        update_fields['status'] = all_booking_details.status

                    if booking_details.actual_start_time != all_booking_details.actual_start_time:
                        update_fields['actual_start_time'] = all_booking_details.actual_start_time

                    if booking_details.actual_end_time != all_booking_details.actual_end_time:
                        update_fields['actual_end_time'] = all_booking_details.actual_end_time

                    if booking_details.duration != all_booking_details.duration:
                        update_fields['duration'] = all_booking_details.duration

                    if update_fields:
                        BookingDetails.objects.filter(booking=booking).update(**update_fields)

            except Exception as e:
                print(f"Error updating AllBookings: {e}")
