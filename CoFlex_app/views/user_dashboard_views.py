from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import now
from django.http import JsonResponse
from datetime import timedelta
import random
import uuid
from ..models import (VerifiedUsers, SubscribedUsersVerificationCode,

                      SubscribedUsers, SubscribedUsersDetails,
                      SubscribedUsersPaymentDetails, SubscribedUserCardDetails,
                      SubscribedUserCardDetailsLastFourDigits, SubscribedUsersStopped,

                      SubscribedUsersSubscriptionHistory, SubscribedUsersFuture)

from ..forms.user_card_details_forms import VerifiedUserCardDetails_SubscribedUsersVerificationCode_Forms
from django.conf import settings
from cryptography.fernet import Fernet
from .user_recent_actions_views import user_device_activity
from .email_functions import send_verification_code_email, send_subscription_confirmation_email


@login_required
def user_home(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)

    # Default context if user is not subscribed
    context = {
        "user": user,
        "is_subscribed": False,
    }

    subscription_plans = {
        "basic_month": ["Hot Desk Access", "Basic Wi-Fi"],
        "standard_month": ["Dedicated Desk", "Premium Wi-Fi", "10 Meeting Room Hours"],
        "vip_month": ["Private Office", "Premium Wi-Fi", "20 Meeting Room Hours", "Dedicated Support"],

        "basic_quarter": ["Hot Desk Access", "Enhanced Wi-Fi", "5 Meeting Room Hours"],
        "standard_quarter": ["Dedicated Desk", "Ultra-Fast Wi-Fi", "20 Meeting Room Hours", "Priority Support"],
        "vip_quarter": ["Large Private Office", "Ultra-Fast Wi-Fi", "Unlimited Meeting Rooms", "Executive Support"],

        "basic_semiannual": ["Hot Desk Access", "Premium Wi-Fi", "15 Meeting Room Hours", "Basic Support"],
        "standard_semiannual": ["Dedicated Desk", "Ultra-Fast Wi-Fi", "Unlimited Meeting Rooms", "Premium Support"],
        "vip_semiannual": ["Executive Private Suite", "Premium Networking", "Event Access", "24/7 Concierge"]
    }

    try:
        subscribed_user = SubscribedUsers.objects.get(user=user, is_subscribed=True)
        subscription_details = SubscribedUsersDetails.objects.get(subscribed_user=subscribed_user)
        payment_details = SubscribedUsersPaymentDetails.objects.get(subscribed_user=subscribed_user)
        card_details = SubscribedUserCardDetailsLastFourDigits.objects.get(subscribed_user=subscribed_user)

        # Subscription Information
        subscription_type = subscription_details.subscription_type
        subscription_plan = subscription_details.subscription_plan
        subscription_text = subscription_plans[subscription_plan]

        if subscription_details.subscription_status == 'stopped':
            duration = subscribed_user.subscribed_users_stopped.stopped_duration
            from_date = subscribed_user.subscribed_users_stopped.subscription_stopped_from_date
            till_date = subscribed_user.subscribed_users_stopped.subscription_stopped_till_date
            subscription_expiry_date = subscribed_user.subscribed_users_stopped.subscription_stopped_till_date
            days_left = subscribed_user.subscribed_users_stopped.subscription_stopped_days_left
            remaining_stop_attempts = subscribed_user.subscribed_users_stopped.remaining_stop_attempts
            is_expiring_soon = days_left is not None and days_left <= 3
        else:
            duration = subscription_details.subscription_duration
            from_date = subscription_details.subscription_from_date
            till_date = subscription_details.subscription_till_date
            subscription_expiry_date = subscribed_user.subscription_expiry_date
            days_left = subscription_details.days_left
            remaining_stop_attempts = subscribed_user.subscribed_users_stopped.remaining_stop_attempts
            is_expiring_soon = days_left is not None and days_left <= 7

        # Payment Information
        last_payment_amount = payment_details.charged_amount if payment_details else None
        last_payment_date = payment_details.charged_date if payment_details else None
        payment_method = payment_details.payment_method if payment_details else None
        payment_method = payment_method.replace("_", " ").title()
        subscription_plan = subscription_plan.replace("_", " ").title()
        payment_status = payment_details.payment_status if payment_details else "pending"

        # Masked Card Details
        last_four_digits = card_details.last_four_digits if card_details else "****"
        f1_last_four_digits = Fernet(settings.FIRST_FERNET_KEY_LAST_FOUR_DIGITS)
        f2_last_four_digits = Fernet(settings.SECOND_FERNET_KEY_LAST_FOUR_DIGITS)

        last_four_digits = f2_last_four_digits.decrypt(f1_last_four_digits.decrypt(last_four_digits.encode())).decode()

        progress_width = (days_left / duration) * 100 if duration and duration > 0 else 0

        # Context Update
        context.update({
            "is_subscribed": True,

            "subscription_type": subscription_type.capitalize(),
            "subscription_plan": subscription_plan,
            "subscription_text": subscription_text,
            "subscription_expiry": subscription_expiry_date,
            "duration": duration,
            "subscription_from_date": from_date,
            "subscription_till_date": till_date,
            "days_left": days_left,
            "is_expiring_soon": is_expiring_soon,
            "subscription_status": subscription_details.subscription_status,

            "remaining_stop_attempts": remaining_stop_attempts,

            "last_payment_amount": last_payment_amount,
            "last_payment_date": last_payment_date,
            "payment_method": payment_method,
            "payment_status": payment_status,
            "progress_width": progress_width,
            "last_four_digits": f"**** **** **** {last_four_digits}",
        })

    except SubscribedUsers.DoesNotExist:
        pass

    return render(request, 'user_dashboard/user_home.html', context)


@login_required
def user_card_details_verification_code_validation(request, user_id, subscription_plan):
    user = get_object_or_404(VerifiedUsers, id=user_id)

    subscription_plans = {
        "basic_month": {"price": 50, "days": 30, 'subscription_type': 'monthly'},
        "standard_month": {"price": 100, "days": 30, 'subscription_type': 'monthly'},
        "vip_month": {"price": 200, "days": 30, 'subscription_type': 'monthly'},
        "basic_quarter": {"price": 135, "days": 90, 'subscription_type': 'quarterly'},
        "standard_quarter": {"price": 270, "days": 90, 'subscription_type': 'quarterly'},
        "vip_quarter": {"price": 540, "days": 90, 'subscription_type': 'quarterly'},
        "basic_semiannual": {"price": 250, "days": 180, 'subscription_type': 'semiannually'},
        "standard_semiannual": {"price": 500, "days": 180, 'subscription_type': 'semiannually'},
        "vip_semiannual": {"price": 1000, "days": 180, 'subscription_type': 'semiannually'},
    }
    subscription_plan_type = subscription_plan.replace("_", " ").title()
    amount_to_charge = subscription_plans[subscription_plan]['price']

    if request.method == 'POST':
        form = VerifiedUserCardDetails_SubscribedUsersVerificationCode_Forms(request.POST, user=user)
        print(form.is_valid())
        print(f'Form errors: {form.errors}')
        if form.is_valid():

            if subscription_plan not in subscription_plans:
                messages.error(request, 'Invalid subscription type. Please try again!')
                return redirect('user_home', user_id=user.id)

            verification_entry = SubscribedUsersVerificationCode.objects.get(user=user)
            verification_entry.is_code_used = True
            verification_entry.verification_code = None
            verification_entry.save()

            amount_to_charge = subscription_plans[subscription_plan]["price"]
            subscription_duration = subscription_plans[subscription_plan]["days"]
            subscription_type = subscription_plans[subscription_plan]["subscription_type"]

            def generate_subscription_unique_id():
                while True:
                    subscription_unique_id = uuid.uuid4().hex  # 32-character UUID
                    exists = (
                            SubscribedUsers.objects.filter(subscription_unique_id=subscription_unique_id).exists() or
                            SubscribedUsersSubscriptionHistory.objects.filter(
                                subscription_unique_id=subscription_unique_id).exists() or
                            SubscribedUsersFuture.objects.filter(subscription_unique_id=subscription_unique_id).exists()
                    )
                    if not exists:
                        return subscription_unique_id

            subscribed_user = SubscribedUsers.objects.create(
                user=user,
                subscription_unique_id=generate_subscription_unique_id(),
                subscription_datetime=timezone.now(),
                subscription_expiry_date=timezone.now().date() + timedelta(days=subscription_duration),
                is_subscribed=True,
                is_active=True
            )

            subscribed_user_details = SubscribedUsersDetails.objects.create(
                subscribed_user=subscribed_user,
                subscription_type=subscription_type,
                subscription_plan=subscription_plan,
                subscription_duration=subscription_duration,
                days_left=subscription_duration,
                subscription_from_date=timezone.now().date(),
                subscription_till_date=timezone.now().date() + timedelta(days=subscription_duration),
                subscription_status='active'
            )

            subscribed_user_payment_details = SubscribedUsersPaymentDetails.objects.create(
                subscribed_user=subscribed_user,
                charged_amount=amount_to_charge,
                charged_date=timezone.now().date(),
                charged_time=timezone.now().time(),
                is_charged=True,
                payment_method='credit_card',
                payment_status='successful'
            )

            card_number = form.cleaned_data.get('card_number')
            last_four_digits = card_number[-4:]
            expiry_date = form.cleaned_data.get('expiry_date')
            cvv = form.cleaned_data.get('cvv')
            card_holder_name = form.cleaned_data.get('card_holder_name')

            f1 = Fernet(settings.FIRST_FERNET_KEY)
            f2 = Fernet(settings.SECOND_FERNET_KEY)
            f3 = Fernet(settings.THIRD_FERNET_KEY)
            f4 = Fernet(settings.FOURTH_FERNET_KEY)
            f5 = Fernet(settings.FIFTH_FERNET_KEY)

            subscribed_user_card_details = SubscribedUserCardDetails.objects.create(
                subscribed_user=subscribed_user,
                card_number=(f1.encrypt(f2.encrypt(f3.encrypt(f4.encrypt(f5.encrypt(card_number.encode())))))).decode(),
                expiry_date=(f1.encrypt(f2.encrypt(f3.encrypt(f4.encrypt(f5.encrypt(expiry_date.encode())))))).decode(),
                cvv=(f1.encrypt(f2.encrypt(f3.encrypt(f4.encrypt(f5.encrypt(cvv.encode())))))).decode(),
                card_holder_name=(
                    f1.encrypt(f2.encrypt(f3.encrypt(f4.encrypt(f5.encrypt(card_holder_name.encode())))))).decode(),
                added_time=timezone.now()
            )

            f1_last_four_digits = Fernet(settings.FIRST_FERNET_KEY_LAST_FOUR_DIGITS)
            f2_last_four_digits = Fernet(settings.SECOND_FERNET_KEY_LAST_FOUR_DIGITS)

            subscribed_users_card_details_last_four_digits = SubscribedUserCardDetailsLastFourDigits.objects.create(
                subscribed_user=subscribed_user,
                last_four_digits=(
                    f1_last_four_digits.encrypt(f2_last_four_digits.encrypt(last_four_digits.encode()))).decode(),
                added_date=timezone.now().date(),
                added_time=timezone.now().time(),
            )

            if subscribed_user.subscribed_users_details.subscription_type == 'monthly':
                remaining_stop_attempts = 3
            elif subscribed_user.subscribed_users_details.subscription_type == 'quarterly':
                remaining_stop_attempts = 4
            else:
                remaining_stop_attempts = 5

            subscribed_users_stopped = SubscribedUsersStopped.objects.create(
                subscribed_user=subscribed_user,
                stopped_duration=subscribed_user.subscribed_users_details.subscription_duration / 10,
                subscription_stopped_days_left=subscribed_user.subscribed_users_details.subscription_duration / 10,
                remaining_stop_attempts=remaining_stop_attempts
            )

            user_device_activity(instance=user, request=request, activity_type='Purchased Subscription',
                                 activity_details={})

            send_subscription_confirmation_email(user=user,
                                                 sender_email=settings.EMAIL_HOST_USER,
                                                 recipient_email=user.email,
                                                 subscription=subscribed_user,
                                                 subscription_details=subscribed_user.subscribed_users_details,
                                                 payment_details=subscribed_user.subscribed_users_payment_details,
                                                 card_details_last_four=subscribed_user.subscribed_users_card_details_last_four_digits)

            messages.success(request, 'Your payment has been verified successfully!')

            return redirect('user_home', user_id=user.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")

    else:
        form = VerifiedUserCardDetails_SubscribedUsersVerificationCode_Forms(user=user)

    return render(request, 'user_card_details/user_card_details_verification_code_validation.html', {'form': form,
                                                                                                     'user': user,
                                                                                                     'subscription_plan_type': subscription_plan_type,
                                                                                                     'amount_to_charge': amount_to_charge,
                                                                                                     'subscription_plan': subscription_plan})


@login_required
def user_card_details_sending_verification_code(request, user_id):
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method.'}, status=400)
    user = get_object_or_404(VerifiedUsers, id=user_id)

    verification_code = str(random.randint(100000, 999999))

    try:
        send_verification_code_email(user=user,
                                     sender_email=settings.EMAIL_HOST_USER,
                                     recipient_email=user.email,
                                     verification_code=verification_code,
                                     expiry_time='a minute')

        f_code = Fernet(settings.FERNET_KEY_VERIFICATION_CODE)
        verification_code = (f_code.encrypt(str(verification_code).encode())).decode()

        SubscribedUsersVerificationCode.objects.update_or_create(
            user=user,
            defaults={
                'verification_code': verification_code,
                'is_code_used': False,
                'expires_at': now() + timedelta(minutes=1)
            }
        )

        # messages.success(request, 'A verification code has been sent to your email!')

        return JsonResponse({'message': 'Verification code sent successfully.'}, status=200)

    except Exception as e:
        messages.error(request, f'Error sending verification email: {e}')
        return JsonResponse({'error': f'Error sending verification email: {str(e)}'}, status=500)


@login_required
def user_card_cancel_verification(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    messages.info(request, "Your subscription process has been canceled!")
    return redirect('user_home', user_id=user.id)
