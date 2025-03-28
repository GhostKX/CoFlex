from CoFlex_app.models import UserSignUpLoginLogoutActivity, UserDeviceActivities
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, reverse
from django.shortcuts import render
import ipaddress
import ipinfo
from django_user_agents.utils import get_user_agent
from ..models import VerifiedUsers


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

        print(user_location_details.all)

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


def user_signed_up_activity(instance, request, created):
    if created:
        user_ip_address = get_user_ip(request)
        if user_ip_address:
            if not request.session.session_key:
                request.session.create()

            session_key = request.session.session_key

            device_details = get_user_device_details(request)
            device_type = device_details['device_type']
            browser = device_details['browser']
            operating_system = device_details['operating_system']
            device_name = device_details['device_name']

            user_location_details_dict = get_user_location_details(request)
            if user_location_details_dict:
                user_ip = user_location_details_dict['user_ip']
                user_city = user_location_details_dict['user_city']
                user_region = user_location_details_dict['user_region']
                user_country = user_location_details_dict['user_country']
                user_organization = user_location_details_dict['user_organization']
                user_latitude = user_location_details_dict['user_latitude']
                user_longitude = user_location_details_dict['user_longitude']

                UserSignUpLoginLogoutActivity.objects.create(
                    user=instance,
                    session_key=session_key,
                    ip_address=user_ip,
                    device_type=device_type,
                    browser=browser,
                    operating_system=operating_system,
                    device_name=device_name,
                    organization=user_organization,
                    city=user_city,
                    region=user_region,
                    country=user_country,
                    latitude=user_latitude,
                    longitude=user_longitude,
                    date_time=timezone.now(),
                    is_Logged_in=True,
                    action='Sign Up'
                )


def user_device_activity(instance, request, activity_type, activity_details):
    if instance:
        if not request.session.session_key:
            while True:
                request.session.create()
                session_key = request.session.session_key

                if not UserSignUpLoginLogoutActivity.objects.filter(session_key=session_key).exists():
                    return session_key
        session_key = request.session.session_key

        try:
            user_session = UserSignUpLoginLogoutActivity.objects.filter(user=instance, session_key=session_key).first()
        except Exception as e:
            print("Session not found for user!")
            return

        user_activity = UserDeviceActivities.objects.create(
            user_session=user_session,
            activity_type=activity_type,
            activity_details=activity_details,
            date_time=timezone.now()
        )
        user_activity.save()


@login_required
def user_recent_actions_history(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)

    current_session_key = request.session.session_key

    history = []

    # Fetch all login sessions in order (oldest first)
    user_sessions = UserSignUpLoginLogoutActivity.objects.filter(user=user, action='Login').order_by('-date_time')

    for session in user_sessions:
        # Getting all actions linked to this session_key
        session_activities = UserDeviceActivities.objects.filter(user_session=session).order_by('-date_time')

        # Finding logout event for this session
        logout_event = UserSignUpLoginLogoutActivity.objects.filter(user=user, session_key=session.session_key, action='Logout').order_by('-date_time').first()

        if session.session_key == current_session_key:
            is_current_session = True
        else:
            is_current_session = False

        history.append({
            'login': session,
            'activities': session_activities,
            'logout': logout_event,
            'is_current_session': is_current_session
        })

    try:
        user_sign_up_session = UserSignUpLoginLogoutActivity.objects.get(user=user, action='Sign Up')
        history.append(user_sign_up_session)
    except UserSignUpLoginLogoutActivity.DoesNotExist:
        pass

    return render(request, 'user_recent_actions/user_recent_actions.html', {'user': user, 'history': history})


@login_required
def user_action_details(request, user_id, session_key, action_type):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    user_session = get_object_or_404(UserSignUpLoginLogoutActivity, user=user, session_key=session_key, action=action_type)

    return render(request, 'user_recent_actions/user_action_details.html', {'user': user, 'user_session': user_session})







