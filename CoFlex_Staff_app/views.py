from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.utils.timezone import now, localdate, localtime
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.utils.html import escape
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import (StaffAccounts, StaffEditMainEmail, StaffSignUpLoginLogoutActivity, StaffDeviceActivities,
                     StaffLocations, StaffLocationDetails, StaffLocationAvailability,
                     All_Locations_Bookings, All_Locations_Bookings_Details)
import os
from datetime import datetime
from datetime import timedelta
import random
import pytz
from .forms import StaffCalendarDateChoosingForm, StaffEditProfileDetailsForm, StaffEditEmailVerificationCodeForm, \
    StaffBookingDetailsViewForms
from django.utils import timezone
import ipaddress
import ipinfo
from django_user_agents.utils import get_user_agent


@login_required
def staff_dashboard(request, staff_id, location_code):
    staff = get_object_or_404(StaffAccounts, id=staff_id, location_code=location_code)
    staff_profile = staff.staff_profiles
    staff_photo_details = staff.staff_photo_details

    all_bookings = All_Locations_Bookings.objects.filter(location_code=location_code).order_by('created_date', 'created_time')

    # Getting today's date
    tashkent_tz = pytz.timezone('Asia/Tashkent')
    tashkent_time = now().astimezone(tashkent_tz)
    today = tashkent_time.date()
    current_date = today

    # Getting bookings where start_date == today
    all_bookings_today = All_Locations_Bookings_Details.objects.filter(location_booking__location_code=location_code, start_date=today).select_related('location_booking')

    # Attaching booking details correctly
    for booking_detail in all_bookings_today:
        setattr(booking_detail.location_booking, "booking_details", booking_detail)

    # Generating a list of 10 days (yesterday, today, next 8 days)
    days_range = []
    for i in range(-1, 9):
        day_date = today + timedelta(days=i)
        day_info = {
            "date": day_date.strftime("%Y-%m-%d"),
            "day_name": day_date.strftime("%a"),
            "day_number": day_date.day,
            "is_today": day_date == today
        }
        days_range.append(day_info)

    context = {
        'staff': staff,
        'staff_profile': staff_profile,
        'staff_photo_details': staff_photo_details,
        'all_bookings': all_bookings,
        'all_bookings_today': all_bookings_today,
        'days_range': days_range,
        'current_date': current_date,
    }

    return render(request, 'CoFlex_Staff_app/staff_dashboard.html', context)


@require_POST
@login_required
def staff_specific_date(request, staff_id, location_code):
    staff = get_object_or_404(StaffAccounts, id=staff_id, location_code=location_code)

    try:
        data = json.loads(request.body)
        selected_date = data.get('selected_date')
        date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()

        # Getting filter parameters
        book_id_filter = data.get('book_id', '').lower()
        first_name_filter = data.get('first_name', '').lower()
        last_name_filter = data.get('last_name', '').lower()
        checkin_filter = data.get('checkin', '').lower()
        checkout_filter = data.get('checkout', '').lower()
        requests_filter = data.get('requests', '').lower()
        status_filter = data.get('status', 'all')

    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid request format'}, status=400)

    all_location_bookings = All_Locations_Bookings.objects.filter(location_code=location_code)
    all_location_bookings_details = All_Locations_Bookings_Details.objects.filter(location_booking__location_code=location_code)

    if book_id_filter:
        all_location_bookings = all_location_bookings.filter(booking_id__icontains=book_id_filter)

    if status_filter and status_filter != 'all':
        all_location_bookings = all_location_bookings_details.filter(status__icontains=status_filter)

    if first_name_filter:
        all_location_bookings = all_location_bookings.filter(user_first_name__icontains=first_name_filter)

    if last_name_filter:
        all_location_bookings = all_location_bookings.filter(user_last_name__icontains=last_name_filter)

    # Filter bookings for the selected date and apply remaining filters
    bookings = []
    for booking in all_location_bookings:
        booking_details = getattr(booking, 'booking_details', None)

        if booking_details and booking_details.start_date == date_obj:
            start_time = booking_details.start_time.strftime('%H:%M')
            end_time = booking_details.end_time.strftime('%H:%M')

            if (checkin_filter and checkin_filter not in start_time.lower()):
                continue

            if (checkout_filter and checkout_filter not in end_time.lower()):
                continue

            if (requests_filter and requests_filter not in booking_details.special_requests.lower()):
                continue

            bookings.append({
                'booking_id': booking.booking_id,
                'user_first_name': booking.user_first_name,
                'user_last_name': booking.user_last_name,
                'start_time': start_time,
                'end_time': end_time,
                'special_requests': booking_details.special_requests,
                'status': booking_details.status
            })

    return JsonResponse({'bookings': bookings})


@login_required
@csrf_protect
def staff_update_profile_photo(request, staff_id, location_code):
    if request.method == 'POST' and request.FILES.get('profile_photo'):

        profile_photo = request.FILES['profile_photo']

        file_type = os.path.splitext(profile_photo.name)[-1]
        file_new_name = f'staff_{staff_id}{file_type}'

        try:
            staff = StaffAccounts.objects.get(id=staff_id)
            staff_photo_details = staff.staff_photo_details

            if staff_photo_details.photo_path:
                old_photo_path = os.path.join(settings.MEDIA_ROOT, staff_photo_details.photo_path)
                os.remove(old_photo_path)

            fs = FileSystemStorage(location='media/staff_profile_images/')
            saved_file_path = fs.save(file_new_name, profile_photo)

            # Saving the uploaded file
            staff_photo_details.profile_photo = f'staff_profile_images/{file_new_name}'
            staff_photo_details.photo_path = f'staff_profile_images/{saved_file_path}'
            staff_photo_details.uploaded_time = now()
            staff_photo_details.save()

            staff_device_activity(instance=staff, request=request, activity_type='Updated Profile Photo',
                                  activity_details={})

            messages.success(request, 'Profile photo updated successfully')

        except Exception as e:
            messages.error(request, f'Error uploading photo: {str(e)}')

    return redirect('staff_dashboard', staff_id=staff_id, location_code=location_code)


@login_required()
def logout_staff(request):
    logout(request)

    messages.success(request, "You have been logged out successfully!")
    return redirect(reverse('home'))


@login_required
def staff_edit_details(request, staff_id, location_code):
    staff = get_object_or_404(StaffAccounts, id=staff_id)
    staff_profiles = staff.staff_profiles
    staff_edit_main_email = staff.staff_edit_main_email

    if request.method == 'POST':
        form = StaffEditProfileDetailsForm(request.POST, instance=staff)
        if form.is_valid():

            changed_details = {}
            staff_first_name = form.cleaned_data.get('staff_first_name')
            if staff.staff_first_name != staff_first_name:
                changed_details['staff_first_name'] = {'old': staff.staff_first_name,
                                                       'new': staff_first_name}

            staff_last_name = form.cleaned_data.get('staff_last_name')
            if staff.staff_last_name != staff_last_name:
                changed_details['staff_last_name'] = {'old': staff.staff_last_name,
                                                      'new': staff_last_name}

            staff_username = form.cleaned_data.get('staff_username')
            if staff_profiles.staff_username != staff_username:
                changed_details['staff_username'] = {'old': staff_profiles.staff_username,
                                                     'new': staff_username}

            phone_number = form.cleaned_data.get('phone_number')
            if staff_profiles.phone_number != phone_number:
                changed_details['phone_number'] = {'old': staff_profiles.phone_number,
                                                   'new': phone_number}

            address = form.cleaned_data.get('address')
            if staff_profiles.address != address:
                changed_details['address'] = {'old': staff_profiles.address,
                                              'new': address}

            if changed_details:
                staff_device_activity(instance=staff, request=request, activity_type='Updated Personal Info',
                                      activity_details=changed_details)

            staff.staff_first_name = staff_first_name if staff_first_name else staff.staff_first_name
            staff.staff_last_name = staff_last_name if staff_last_name else staff.staff_last_name
            staff_profiles.staff_username = staff_username if staff_username else staff.staff_username
            staff_profiles.phone_number = phone_number if phone_number else staff.phone_number
            staff_profiles.address = address if address else staff.address

            staff.save()
            staff_profiles.save()

            staff_email = form.cleaned_data.get('staff_email')
            if staff_email and staff_email != staff.staff_email:
                staff_edit_main_email.new_email = staff_email
                staff_edit_main_email.save()

                return redirect('verify_new_staff_email', staff_id=staff.id, location_code=location_code)
            else:
                staff.staff_email = form.cleaned_data.get('staff_email')
                staff.save()

            messages.success(request, 'Staff information updated successfully!')
            return redirect('staff_dashboard', staff_id=staff.id, location_code=location_code)

    else:
        initial_data = {
            'staff_first_name': staff.staff_first_name,
            'staff_last_name': staff.staff_last_name,
            'staff_email': staff.staff_email,
            'staff_username': staff_profiles.staff_username,
            'phone_number': staff_profiles.phone_number,
            'address': staff_profiles.address
        }
        form = StaffEditProfileDetailsForm(initial=initial_data, instance=staff)

    return render(request, 'CoFlex_Staff_app/staff_edit_details.html',
                  {'form': form, 'staff': staff, 'staff_profiles': staff_profiles})


@login_required
def verify_new_staff_email(request, staff_id, location_code):
    staff = get_object_or_404(StaffAccounts, id=staff_id, location_code=location_code)
    staff_edit_main_email = staff.staff_edit_main_email

    verification_code = str(random.randint(100000, 999999))

    try:
        send_mail('Verification Code',
                  f'<p>Message to {escape(staff_edit_main_email.new_email)}',
                  'settings.EMAIL_HOST_USER',
                  [staff_edit_main_email.new_email],
                  fail_silently=False,
                  html_message=f'<html><body style="font-size: 18px; font-family: Arial, sans-serif;">'
                               f'<p>{escape(staff.staff_first_name)} {escape(staff.staff_last_name)},'
                               f' your verification code is: <b style="font-size: 24px; font-weight: bold;">{verification_code}</b>'
                               f'</p>'
                               f'<p>This code will expire in a minute!</p>'
                               f'</body></html>')
        messages.success(request, 'A verification code has been sent to your email!')

        staff_edit_main_email.verification_code = verification_code
        staff_edit_main_email.is_code_used = False
        staff_edit_main_email.expires_at = now() + timedelta(minutes=1)
        staff_edit_main_email.save()

        return redirect(
            reverse('verify_new_staff_email_code', kwargs={'staff_id': staff.id, 'location_code': location_code}))
    except Exception as e:
        messages.error(request, f'Error sending verification email: {e}')
        return redirect('staff_dashboard', staff_id=staff.id, location_code=location_code)


@login_required
def verify_new_staff_email_code(request, staff_id, location_code):
    staff = get_object_or_404(StaffAccounts, id=staff_id, location_code=location_code)
    staff_edit_main_email = StaffEditMainEmail.objects.get(staff=staff)

    if request.method == 'POST':
        form = StaffEditEmailVerificationCodeForm(request.POST, staff=staff)

        if form.is_valid():
            changed_details = {'staff_email': {'old': staff.staff_email,
                                               'new': staff_edit_main_email.new_email}}

            staff.staff_email = staff_edit_main_email.new_email

            if changed_details:
                if changed_details:
                    staff_device_activity(instance=staff, request=request, activity_type='Changed Email Address',
                                          activity_details=changed_details)

            staff_edit_main_email.is_code_used = True
            staff_edit_main_email.verification_code = None
            staff_edit_main_email.save()
            staff.save()

            messages.success(request, 'Staff information has been updated successfully!')

            return redirect('staff_dashboard', staff_id=staff.id, location_code=location_code)
    else:
        form = StaffEditEmailVerificationCodeForm()

    return render(request, 'CoFlex_Staff_app/verify_new_staff_email_code.html', {'form': form, 'staff': staff,
                                                                                 'staff_new_email': staff_edit_main_email.new_email})


@login_required
def verify_new_staff_email_code_resend_code(request, staff_id, location_code):
    staff = get_object_or_404(StaffAccounts, id=staff_id, location_code=location_code)
    staff_edit_main_email = StaffEditMainEmail.objects.get(staff=staff)

    verification_code = str(random.randint(100000, 999999))

    staff_edit_main_email.verification_code = verification_code
    staff_edit_main_email.expires_at = now() + timedelta(minutes=1)
    staff_edit_main_email.is_code_used = False
    staff_edit_main_email.save()

    try:
        send_mail('Verification Code',
                  f'<p>Message to {escape(staff_edit_main_email.new_email)}',
                  'settings.EMAIL_HOST_USER',
                  [staff_edit_main_email.new_email],
                  fail_silently=False,
                  html_message=f'<html><body style="font-size: 18px; font-family: Arial, sans-serif;">'
                               f'<p>{escape(staff.staff_first_name)} {escape(staff.staff_last_name)},'
                               f' your verification code is: <b style="font-size: 24px; font-weight: bold;">{verification_code}</b>'
                               f'</p>'
                               f'<p>This code will expire in a minute!</p>'
                               f'</body></html>')
        messages.success(request, 'A verification code has been sent to your email!')
    except Exception as e:
        messages.error(request, f'Error sending verification email: {e}')

    return redirect('verify_new_staff_email_code', staff_id=staff.id, location_code=location_code)


@login_required
def cancel_new_staff_email(request, staff_id, location_code):
    messages.info(request, "Your New Email was not verified!")
    return redirect('staff_dashboard', staff_id=staff_id, location_code=location_code)


@login_required
@csrf_protect
def staff_calendar_date(request, staff_id, location_code):
    if request.method == 'POST':
        form = StaffCalendarDateChoosingForm(request.POST)
        if form.is_valid():
            selected_date = form.cleaned_data.get("selected_date")
            return redirect('staff_date_page', staff_id=staff_id, location_code=location_code,
                            selected_date=selected_date)
        else:
            messages.error(request, "Invalid date selection. Please choose a valid date.")

        return redirect('staff_dashboard', staff_id=staff_id, location_code=location_code)


@login_required
def staff_date_page(request, staff_id, location_code, selected_date):
    staff = get_object_or_404(StaffAccounts, id=staff_id, location_code=location_code)

    location = get_object_or_404(StaffLocations, location_code=location_code)
    location_name = location.location_name

    if request.method == 'POST':
        try:
            new_selected_date = request.POST.get('selected_date')
            if new_selected_date:
                parsed_date = datetime.strptime(new_selected_date, '%Y-%m-%d').date()
                return redirect('staff_date_page', staff_id=staff_id,
                                location_code=location_code,
                                selected_date=parsed_date.strftime('%Y-%m-%d'))
        except (ValueError, TypeError) as e:
            messages.error(request, f"Invalid date format: {e}")

    if not selected_date:
        selected_date = localdate().strftime('%Y-%m-%d')

    try:
        if isinstance(selected_date, str):
            query_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        else:
            query_date = selected_date
    except ValueError:
        query_date = localdate()
        messages.error(request, "Invalid date format. Showing today's bookings instead.")

    # Getting all bookings for the selected date
    all_bookings_on_selected_date = All_Locations_Bookings_Details.objects.filter(location_booking__location_code=location_code, start_date=query_date).select_related('location_booking')

    context = {
        'staff': staff,
        'location_code': location_code,
        'selected_date': query_date,
        'location_name': location_name,
        'all_bookings_on_selected_date': all_bookings_on_selected_date
    }

    return render(request, 'CoFlex_Staff_app/staff_date_page.html', context)


@login_required
def booking_details_view(request, staff_id, location_code, booking_id):
    staff = get_object_or_404(StaffAccounts, id=staff_id, location_code=location_code)

    booking = All_Locations_Bookings.objects.get(booking_id=booking_id)
    booking_details = All_Locations_Bookings_Details.objects.get(location_booking=booking)

    form = StaffBookingDetailsViewForms(request.POST)
    if form.is_valid():
        new_status = form.cleaned_data.get('status')

        if booking_details.status == new_status:
            messages.info(request, f'No Changes were made to the Booking {booking_id}.')
        else:

            if new_status == 'In Progress' and not booking_details.actual_start_time:
                booking_details.actual_start_time = localtime(now())

            if new_status == 'Finished' and not booking_details.actual_end_time:
                booking_details.actual_end_time = localtime(now())

                if booking_details.actual_start_time:
                    time_difference = booking_details.actual_end_time - booking_details.actual_start_time
                    hours = time_difference.total_seconds() / 3600
                    booking_details.duration = round(hours, 2)
                    booking_details.duration = hours

            print(f"Saved actual_start_time: {booking_details.actual_start_time}")  # Debugging

            changed_details = {f'booking_status': {'old': booking_details.status, 'new': new_status}}
            booking_details.status = new_status
            booking_details.save()

            if changed_details:
                staff_device_activity(instance=staff, request=request, activity_type=f'Changed Status of Booking {booking_id} ',
                                      activity_details=changed_details)

            messages.success(request, f'Booking {booking_id} status was successfully changed!')

        return redirect('staff_dashboard', staff_id=staff_id, location_code=location_code)

    else:
        initial_data = {
            'status': booking_details.status
        }
        form = StaffBookingDetailsViewForms(initial=initial_data)

    context = {
        'staff': staff,
        'booking': booking,
        'booking_details': booking_details,
        'form': form,
    }

    return render(request, 'CoFlex_Staff_app/booking_details_view.html', context)


def get_staff_ip(request):
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


def get_staff_device_details(request):
    staff_agent = get_user_agent(request)
    device_type = ''
    if staff_agent.is_mobile:
        device_type = 'Mobile Phone'
    elif staff_agent.is_tablet:
        device_type = 'Tablet'
    elif staff_agent.is_pc:
        device_type = 'PC/Laptop'
    elif staff_agent.is_bot:
        device_type = 'Bot'
    else:
        device_type = 'Unknown'

    browser = staff_agent.browser.family or 'Unknown'
    operating_system = staff_agent.os.family or 'Unknown'

    device_name = staff_agent.device.family
    if not device_name or device_name.lower() == "other":
        device_name = staff_agent.os.family

    return {
        'device_type': device_type,
        'browser': browser,
        'operating_system': operating_system,
        'device_name': device_name
    }


def get_staff_location_details(request):
    staff_ip_address = get_staff_ip(request)
    if staff_ip_address:
        access_token = str(settings.LOCATION_ACCESS_TOKEN)
        handler = ipinfo.getHandler(access_token)
        staff_location_details = handler.getDetails()

        staff_ip = staff_location_details.ip
        staff_city = staff_location_details.city
        staff_region = staff_location_details.region
        staff_country = staff_location_details.country_name
        staff_latitude = staff_location_details.latitude
        staff_longitude = staff_location_details.longitude

        return {
            'staff_ip': staff_ip,
            'staff_city': staff_city,
            'staff_region': staff_region,
            'staff_country': staff_country,
            'staff_latitude': staff_latitude,
            'staff_longitude': staff_longitude
        }

    return {}


def staff_device_activity(instance, request, activity_type, activity_details):
    if instance:

        if not request.session.session_key:
            while True:
                request.session.create()
                session_key = request.session.session_key

                if not StaffSignUpLoginLogoutActivity.objects.filter(session_key=session_key).exists():
                    return session_key
        session_key = request.session.session_key

        try:
            staff_session = StaffSignUpLoginLogoutActivity.objects.filter(staff=instance,
                                                                          session_key=session_key).first()
        except Exception as e:
            print("Session not found for staff!")
            return

        staff_activity = StaffDeviceActivities.objects.create(
            staff_session=staff_session,
            activity_type=activity_type,
            activity_details=activity_details,
            date_time=timezone.now()
        )
        staff_activity.save()


@login_required
def staff_recent_actions_history(request, staff_id, location_code):
    staff = get_object_or_404(StaffAccounts, id=staff_id)

    current_session_key = request.session.session_key

    history = []

    # Fetching all login sessions in order (oldest first)
    staff_sessions = StaffSignUpLoginLogoutActivity.objects.filter(staff=staff, action='Login').order_by('-date_time')

    for session in staff_sessions:
        session_activities = StaffDeviceActivities.objects.filter(staff_session=session).order_by('-date_time')

        logout_event = StaffSignUpLoginLogoutActivity.objects.filter(staff=staff, session_key=session.session_key, action='Logout').order_by('-date_time').first()

        if session.session_key == current_session_key:
            is_current_session = True
        else:
            is_current_session = False

        # Adding the session and its actions to history
        history.append({
            'login': session,
            'activities': session_activities,
            'logout': logout_event,
            'is_current_session': is_current_session
        })

    return render(request, 'CoFlex_Staff_app/staff_recent_actions.html', {'staff': staff, 'location_code': location_code, 'history': history})


@login_required
def staff_action_details(request, staff_id, location_code, session_key, action_type):
    staff = get_object_or_404(StaffAccounts, id=staff_id)
    staff_session = get_object_or_404(StaffSignUpLoginLogoutActivity, staff=staff, session_key=session_key, action=action_type)

    return render(request, 'CoFlex_Staff_app/staff_action_details.html', {'staff': staff, 'location_code': location_code, 'staff_session': staff_session})
