from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now
from datetime import timedelta
import random
from django.core.mail import send_mail
from django.utils.html import escape
from ..models import (VerifiedUsers,

                      SandSubscribedUsers, SandSubscribedUsersVerificationCode,
                      SandSubscribedUsersDetails, SandSubscribedUsersPaymentDetails,
                      SandSubscribedUserCardDetails, SandSubscribedUserCardDetailsLastFourDigits,

                      SubscribedUsers,
                      SubscribedUsersDetails, SubscribedUsersPaymentDetails,
                      SubscribedUserCardDetails, SubscribedUserCardDetailsLastFourDigits,
                      SubscribedUsersSubscriptionHistory)

from ..forms.user_card_details_forms import VerifiedUserCardDetailsForms, SubscribedUsersVerificationCodeForms
from django.conf import settings
from cryptography.fernet import Fernet
from .user_recent_actions_views import user_device_activity


@login_required
def user_home(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)

    # Default context if user is not subscribed
    context = {
        "user": user,
        "is_subscribed": False,
    }

    try:
        subscribed_user = SubscribedUsers.objects.get(user=user, is_subscribed=True, is_active=True)
        subscription_details = SubscribedUsersDetails.objects.get(user=subscribed_user)
        payment_details = SubscribedUsersPaymentDetails.objects.filter(user=subscribed_user).last()
        card_details = SubscribedUserCardDetailsLastFourDigits.objects.filter(user=subscribed_user).last()

        # Subscription Information
        type_of_subscription = (subscription_details.type_of_subscription.replace('_', ' ')).title()
        expiry_date = subscribed_user.subscription_expiry
        days_left = (expiry_date.date() - now().date()).days if expiry_date else None
        is_expiring_soon = days_left is not None and days_left <= 7

        # Payment Information
        last_payment_amount = payment_details.charged_amount if payment_details else None
        last_payment_date = payment_details.charged_date if payment_details else None
        payment_method = payment_details.payment_method if payment_details else None
        payment_method = (payment_method.replace('_', ' ')).title()
        payment_status = payment_details.payment_status if payment_details else "pending"

        # Masked Card Details
        last_four_digits = card_details.last_four_digits if card_details else "****"
        f_last_four_digits = Fernet(settings.FERNET_KEY_LAST_FOUR_DIGITS)
        last_four_digits = (f_last_four_digits.decrypt(last_four_digits.encode())).decode()

        progress_width = (days_left / subscription_details.duration) * 100 if subscription_details.duration and subscription_details.duration > 0 else 0

        # Context Update
        context.update({
            "is_subscribed": True,
            "subscription_type": type_of_subscription,
            "subscription_expiry": expiry_date,
            "duration": subscription_details.duration,
            "days_left": days_left,
            "is_expiring_soon": is_expiring_soon,
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
def user_card_details(request, user_id, subscription_type):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    if request.method == 'POST':
        form = VerifiedUserCardDetailsForms(request.POST, user=user)
        if form.is_valid():
            subscription_plans = {
                "basic_month": {"price": 50, "days": 30},
                "standard_month": {"price": 100, "days": 30},
                "vip_month": {"price": 200, "days": 30},
                "basic_quarter": {"price": 135, "days": 90},
                "standard_quarter": {"price": 270, "days": 90},
                "vip_quarter": {"price": 540, "days": 90},
                "basic_semiannual": {"price": 250, "days": 180},
                "standard_semiannual": {"price": 500, "days": 180},
                "vip_semiannual": {"price": 1000, "days": 180},
            }

            if subscription_type not in subscription_plans:
                messages.error(request, 'Invalid subscription type. Please try again!')
                return redirect('user_card_details', user_id=user.id, subscription_type=subscription_type)

            amount_to_charge = subscription_plans[subscription_type]["price"]
            duration_days = subscription_plans[subscription_type]["days"]

            user.is_subscribed = True
            user.save()

            sand_subscribed_user, created = SandSubscribedUsers.objects.get_or_create(user=user)
            sand_subscribed_user.subscription_datetime = now()
            sand_subscribed_user.subscription_expiry = now() + timedelta(days=duration_days)
            sand_subscribed_user.is_subscribed = False
            sand_subscribed_user.is_active = True
            sand_subscribed_user.save()

            sand_subscribed_user_details, details_created = SandSubscribedUsersDetails.objects.get_or_create(
                user=sand_subscribed_user)
            sand_subscribed_user_payment_details, payment_created = SandSubscribedUsersPaymentDetails.objects.get_or_create(
                user=sand_subscribed_user)
            sand_subscribed_user_card_details, card_created = SandSubscribedUserCardDetails.objects.get_or_create(
                user=sand_subscribed_user)
            sand_subscribed_users_card_details_last_four_digits, last_four_digits_created = SandSubscribedUserCardDetailsLastFourDigits.objects.get_or_create(
                user=sand_subscribed_user
            )

            sand_subscribed_user_details.type_of_subscription = subscription_type
            sand_subscribed_user_details.duration = duration_days
            sand_subscribed_user_details.save()

            sand_subscribed_user_payment_details.charged_amount = amount_to_charge
            sand_subscribed_user_payment_details.charged_date = now().date()
            sand_subscribed_user_payment_details.charged_time = now().time()
            sand_subscribed_user_payment_details.is_charged = False
            sand_subscribed_user_payment_details.payment_method = 'credit_card'
            sand_subscribed_user_payment_details.payment_status = 'completed'
            sand_subscribed_user_payment_details.save()

            f_first = Fernet(settings.SAND_FIRST_FERNET_KEY)
            f_second = Fernet(settings.SAND_SECOND_FERNET_KEY)

            card_number = form.cleaned_data.get('card_number')
            last_four_digits = card_number[-4:]
            expiry_date = form.cleaned_data.get('expiry_date')
            cvv = form.cleaned_data.get('cvv')
            card_holder_name = form.cleaned_data.get('card_holder_name')

            sand_subscribed_user_card_details.card_number = (f_second.encrypt(f_first.encrypt(card_number.encode()))).decode()
            sand_subscribed_user_card_details.expiry_date = (f_second.encrypt(f_first.encrypt(expiry_date.encode()))).decode()
            sand_subscribed_user_card_details.cvv = (f_second.encrypt(f_first.encrypt(cvv.encode()))).decode()
            sand_subscribed_user_card_details.card_holder_name = (f_second.encrypt(f_first.encrypt(card_holder_name.encode()))).decode()
            sand_subscribed_user_card_details.added_time = now()
            sand_subscribed_user_card_details.save()

            f_last_four_digits = Fernet(settings.SAND_FERNET_KEY_LAST_FOUR_DIGITS)
            last_four_digits = (f_last_four_digits.encrypt(last_four_digits.encode())).decode()

            sand_subscribed_users_card_details_last_four_digits.last_four_digits = last_four_digits
            sand_subscribed_users_card_details_last_four_digits.added_date = now().date()
            sand_subscribed_users_card_details_last_four_digits.added_time = now().time()
            sand_subscribed_users_card_details_last_four_digits.save()

            verification_code = str(random.randint(100000, 999999))

            try:
                send_mail('Verification Code',
                          f'<p>Message to {escape(user.email)}',
                          'settings.EMAIL_HOST_USER',
                          [user.email],
                          fail_silently=False,
                          html_message=f'<html><body style="font-size: 18px; font-family: Arial, sans-serif;">'
                                       f'<p>{escape(user.first_name)} {escape(user.last_name)},'
                                       f' your verification code is: <b style="font-size: 24px; font-weight: bold;">{verification_code}</b>'
                                       f'</p>'
                                       f'<p>This code will expire in a minute!</p>'
                                       f'</body></html>')
                messages.success(request, 'A verification code has been sent to your email!')

                f_code = Fernet(settings.FERNET_KEY_VERIFICATION_CODE)
                verification_code = (f_code.encrypt(str(verification_code).encode())).decode()

                SandSubscribedUsersVerificationCode.objects.get_or_create(
                    user=sand_subscribed_user,
                    verification_code=verification_code,
                    is_code_used=False,
                    expires_at=now() + timedelta(minutes=1)
                )
                return redirect('user_card_details_verification_code', user_id=user.id)
            except Exception as e:
                messages.error(request, f'Error sending verification email: {e}')
                return redirect(f'user_home', user_id=user.id)

    else:
        form = VerifiedUserCardDetailsForms(user=user)

    return render(request, 'user_card_details/user_card_details.html', {'form': form, 'user': user})


@login_required
def user_card_cancel_verification(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    sand_subscribed_user = get_object_or_404(SandSubscribedUsers, user=user)
    sand_subscribed_user.delete()
    messages.info(request, "Your subscription process has been canceled. Please start again.")
    return redirect('user_home', user_id=user_id)


@login_required
def user_card_details_verification_code(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    sand_subscribed_user = get_object_or_404(SandSubscribedUsers, user=user)

    if request.method == 'POST':
        form = SubscribedUsersVerificationCodeForms(request.POST, user=sand_subscribed_user)

        if form.is_valid():
            verification_entry = SandSubscribedUsersVerificationCode.objects.get(user=sand_subscribed_user)
            verification_entry.is_code_used = True
            verification_entry.verification_code = None
            verification_entry.save()

            sand_subscribed_user.is_subscribed = True
            sand_subscribed_user.save()

            sand_subscribed_user.sand_subscribed_users_payment_details.is_charged = True
            sand_subscribed_user.sand_subscribed_users_payment_details.save()

            subscribed_user, created_at = SubscribedUsers.objects.get_or_create(
                user=user,
                subscription_datetime=sand_subscribed_user.subscription_datetime,
                subscription_expiry=sand_subscribed_user.subscription_expiry,
                is_subscribed=sand_subscribed_user.is_subscribed,
                is_active=sand_subscribed_user.is_active
            )

            SubscribedUsersDetails.objects.get_or_create(
                user=subscribed_user,
                type_of_subscription=sand_subscribed_user.sand_subscribed_users_details.type_of_subscription,
                duration=sand_subscribed_user.sand_subscribed_users_details.duration,
            )

            SubscribedUsersPaymentDetails.objects.get_or_create(
                user=subscribed_user,
                charged_amount=sand_subscribed_user.sand_subscribed_users_payment_details.charged_amount,
                charged_date=sand_subscribed_user.sand_subscribed_users_payment_details.charged_date,
                charged_time=sand_subscribed_user.sand_subscribed_users_payment_details.charged_time,
                is_charged=sand_subscribed_user.sand_subscribed_users_payment_details.is_charged,
                payment_method=sand_subscribed_user.sand_subscribed_users_payment_details.payment_method,
                payment_status=sand_subscribed_user.sand_subscribed_users_payment_details.payment_status
            )

            f1 = Fernet(settings.FIRST_FERNET_KEY)
            f2 = Fernet(settings.SECOND_FERNET_KEY)
            f3 = Fernet(settings.THIRD_FERNET_KEY)

            f_first = Fernet(settings.SAND_FIRST_FERNET_KEY)
            f_second = Fernet(settings.SAND_SECOND_FERNET_KEY)

            card_number = (f3.encrypt(f2.encrypt(f1.encrypt(f_first.decrypt(f_second.decrypt(sand_subscribed_user.sand_subscribed_users_card_details.card_number.encode())))))).decode()
            expiry_date = (f3.encrypt(f2.encrypt(f1.encrypt(f_first.decrypt(f_second.decrypt(sand_subscribed_user.sand_subscribed_users_card_details.expiry_date.encode())))))).decode()
            cvv = (f3.encrypt(f2.encrypt(f1.encrypt(f_first.decrypt(f_second.decrypt(sand_subscribed_user.sand_subscribed_users_card_details.cvv.encode())))))).decode()
            card_holder_name = (f3.encrypt(f2.encrypt(f1.encrypt(f_first.decrypt(f_second.decrypt(sand_subscribed_user.sand_subscribed_users_card_details.card_holder_name.encode())))))).decode()

            SubscribedUserCardDetails.objects.get_or_create(
                user=subscribed_user,
                card_number=card_number,
                expiry_date=expiry_date,
                cvv=cvv,
                card_holder_name=card_holder_name,
                added_time=sand_subscribed_user.sand_subscribed_users_card_details.added_time
            )

            f_sand_code = Fernet(settings.SAND_FERNET_KEY_LAST_FOUR_DIGITS)
            f_code = Fernet(settings.FERNET_KEY_LAST_FOUR_DIGITS)
            last_four_digits=(f_code.encrypt(f_sand_code.decrypt(sand_subscribed_user.sand_subscribed_users_card_details_last_four_digits.last_four_digits.encode()))).decode()

            SubscribedUserCardDetailsLastFourDigits.objects.get_or_create(
                user=subscribed_user,
                last_four_digits=last_four_digits,
                added_date=sand_subscribed_user.sand_subscribed_users_card_details_last_four_digits.added_date,
                added_time=sand_subscribed_user.sand_subscribed_users_card_details_last_four_digits.added_time,
            )

            SubscribedUsersSubscriptionHistory.objects.get_or_create(
                user=subscribed_user,
                start_date=now().date(),
                end_date=now().date() + timedelta(days=sand_subscribed_user.sand_subscribed_users_details.duration),
                subscription_type=sand_subscribed_user.sand_subscribed_users_details.type_of_subscription,
                subscription_status='subscribed'
            )

            sand_subscribed_user.delete()

            user_device_activity(instance=user, request=request, activity_type='Purchased Subscription', activity_details={})

            messages.success(request, 'Your payment has been verified successfully!')

            return redirect('user_home', user_id=user.id)
    else:
        form = SubscribedUsersVerificationCodeForms(user=sand_subscribed_user)

    return render(request, 'user_card_details/user_card_details_verification_code.html', {'form': form,
                                                                                          'user': user,
                                                                                          'subscribed_user': sand_subscribed_user,
                                                                                          'subscribed_users_details': sand_subscribed_user.sand_subscribed_users_details})


@login_required
def user_card_details_verification_code_resend_code(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    sand_subscribed_user = get_object_or_404(SandSubscribedUsers, user=user)

    verification_code = str(random.randint(100000, 999999))

    try:
        send_mail('Verification Code',
                  f'<p>Message to {escape(user.email)}',
                  'settings.EMAIL_HOST_USER',
                  [user.email],
                  fail_silently=False,
                  html_message=f'<html><body style="font-size: 18px; font-family: Arial, sans-serif;">'
                               f'<p>{escape(user.first_name)} {escape(user.last_name)},'
                               f' your verification code is: <b style="font-size: 24px; font-weight: bold;">{verification_code}</b>'
                               f'</p>'
                               f'<p>This code will expire in a minute!</p>'
                               f'</body></html>')

        f_code = Fernet(settings.FERNET_KEY_VERIFICATION_CODE)
        verification_code = (f_code.encrypt(str(verification_code).encode())).decode()

        verification_entry = SandSubscribedUsersVerificationCode.objects.filter(user=sand_subscribed_user).first()

        if verification_entry:
            verification_entry.verification_code = verification_code
            verification_entry.expires_at = now() + timedelta(minutes=1)
            verification_entry.is_code_used = False
            verification_entry.save()
        else:
            SandSubscribedUsersVerificationCode.objects.create(
                user=sand_subscribed_user,
                verification_code=verification_code,
                is_code_used=False,
                expires_at=now() + timedelta(minutes=1)
            )

        messages.success(request, 'A verification code has been sent to your email!')

    except Exception as e:
        messages.error(request, f'Error sending verification email: {e}')

    return redirect('user_card_details_verification_code', user_id=user.id)


