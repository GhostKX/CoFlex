import random
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import login
from django.core.mail import send_mail
from django.shortcuts import redirect, get_object_or_404, reverse
from django.shortcuts import render
from django.utils.html import escape
from django.contrib.auth import get_backends
from .user_recent_actions_views import user_device_activity
from ..forms.user_account_recovery_forms import *
from ..models import (VerifiedUsers, UserAccountRecoveryCode)


def restore_account(request):
    if request.method == 'POST':
        form = UserRestoreAccountForm(request.POST)
        if form.is_valid():

            restoration_email = form.cleaned_data.get('restoration_email')
            restoration_details = form.cleaned_data.get('restoration_details')

            user = VerifiedUsers.objects.get(email=restoration_email)
            user.user_account_restoration.restoration_email = restoration_email
            user.user_account_restoration.restoration_details = restoration_details
            user.user_account_restoration.restoration_time = now()
            user.user_account_restoration.save()

            verification_code = str(random.randint(100000, 999999))

            try:
                send_mail('Verification Code',
                          f'<p>Message to {escape(user.email)}',
                          'settings.EMAIL_HOST_USER',
                          [user.email],
                          fail_silently=False,
                          html_message=f'<html><body style="font-size: 18px; font-family: Arial, sans-serif;">'
                                       f'<p>{escape(user.first_name)} {escape(user.last_name)},'
                                       f' your account recovery verification code is: <b style="font-size: 24px; font-weight: bold;">{verification_code}</b>'
                                       f'</p>'
                                       f'<p>This code will expire in a minute!</p>'
                                       f'</body></html>')
                messages.success(request, 'A verification code has been sent to your email!')

                user.user_account_recovery_code.verification_code = verification_code
                user.user_account_recovery_code.is_code_used = False
                user.user_account_recovery_code.expires_at = now() + timedelta(minutes=1)
                user.user_account_recovery_code.save()

                return redirect(reverse('verify_user_account_recovery_code', kwargs={'user_id': user.id}))
            except Exception as e:
                messages.error(request, f'Error sending verification email: {e}')
                return redirect(f'register_user')
    else:
        form = UserRestoreAccountForm()

    return render(request, 'user_account_recovery/user_account_recovery.html', {'form': form})


def verify_user_account_recovery_code(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    if request.method == 'POST':
        form = UserRestoreAccountCodeForm(request.POST, user=user)
        if form.is_valid():
            user.is_active = True

            user.user_account_deletion.deletion_time = None
            user.user_account_deletion.is_deleted = False

            user.user_account_recovery_code.is_code_used = True
            user.user_account_recovery_code.verification_code = None

            user.save()
            user.user_account_deletion.save()
            user.user_account_recovery_code.save()

            # Authentication backend
            backend = get_backends()[0]
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"

            login(request, user, backend=user.backend)
            print(f"User is_authenticated after login: {request.user.is_authenticated}")

            user_device_activity(instance=user, request=request, activity_type='Account Recovery', activity_details={})

            messages.success(request,
                             f'Welcome back, {user.first_name} {user.last_name}! Your account has been recovered successfully!')
            return redirect('user_read_profile', user_id=user.id)
    else:
        form = UserRestoreAccountCodeForm(user=user)

    return render(request, 'user_account_recovery/verify_user_account_recovery_code.html', {'form': form, 'user': user})


def verify_user_account_recovery_code_resend_code(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)

    verification_code = str(random.randint(100000, 999999))

    verification_entry = UserAccountRecoveryCode.objects.get(user=user)
    verification_entry.verification_code = verification_code
    verification_entry.expires_at = now() + timedelta(minutes=1)
    verification_entry.is_code_used = False
    verification_entry.save()

    try:
        send_mail('Verification Code',
                  f'<p>Message to {escape(user.email)}',
                  'settings.EMAIL_HOST_USER',
                  [user.email],
                  fail_silently=False,
                  html_message=f'<html><body style="font-size: 18px; font-family: Arial, sans-serif;">'
                               f'<p>{escape(user.first_name)} {escape(user.last_name)},'
                               f' your account recovery verification code is: <b style="font-size: 24px; font-weight: bold;">{verification_code}</b>'
                               f'</p>'
                               f'<p>This code will expire in a minute!</p>'
                               f'</body></html>')
        messages.success(request, 'A verification code has been sent to your email!')
    except Exception as e:
        messages.error(request, f'Error sending verification email: {e}')

    return redirect('verify_user_account_recovery_code', user_id=user.id)