import random
from datetime import timedelta

from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, reverse
from django.shortcuts import render
from django.utils.timezone import now
from django.conf import settings

from ..forms.user_forgot_password_forms import *

from ..models import (VerifiedUsers, VerifiedUsersPasswordVerificationCode)
from .user_recent_actions_views import user_device_activity
from .email_functions import send_verification_code_email


def forgot_password_email(request):
    form = UserForgotPasswordEmailForm(request.POST)
    if form.is_valid():
        user = form.cleaned_data.get('user')

        verification_code = str(random.randint(100000, 999999))

        try:
            send_verification_code_email(user=user,
                                         sender_email=settings.EMAIL_HOST_USER,
                                         recipient_email=user.email,
                                         verification_code=verification_code,
                                         expiry_time='a minute')

            messages.success(request, 'A verification code has been sent to your email!')

            verification_entry = VerifiedUsersPasswordVerificationCode.objects.get(user=user)

            verification_entry.verification_code = verification_code
            verification_entry.is_code_used = False
            verification_entry.expires_at = now() + timedelta(minutes=1)
            verification_entry.save()

            return redirect(reverse('forgot_password_verification', kwargs={'user_id': user.id}))

        except Exception as e:
            messages.error(request, f'Error sending verification email: {e}')
            return redirect(f'user_forgot_password_email')

    return render(request, 'user_forgot_password/user_forgot_password_email.html', {'form': form})


def forgot_password_verification(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)

    if request.method == 'POST':
        form = UserForgotPasswordVerificationCodeForm(request.POST, user=user)

        if form.is_valid():
            verification_entry = VerifiedUsersPasswordVerificationCode.objects.get(user=user)
            verification_entry.is_code_used = True
            verification_entry.verification_code = None
            verification_entry.save()

            messages.success(request, 'Your account has been verified successfully!')

            return redirect('forgot_password_reset_password', user_id=user.id)
    else:
        form = UserForgotPasswordVerificationCodeForm()

    return render(request, 'user_forgot_password/user_forgot_password_verification.html', {'form': form, 'user': user})


def forgot_password_reset_password(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)

    if request.method == 'POST':
        form = UserForgotPasswordResetPasswordForm(request.POST, instance=user)
        if form.is_valid():
            new_password = form.cleaned_data.get('password1')
            user.set_password(new_password)
            user.save()

            messages.success(request, 'Your password has been reset successfully.')

            changed_details = {'Password': {'old': 'hashed', 'new': 'hashed'}}
            user_device_activity(instance=user, request=request, activity_type='Reset Password',
                                 activity_details=changed_details)

            return redirect('login_user')

    else:
        form = UserForgotPasswordResetPasswordForm(instance=user)

    return render(request, 'user_forgot_password/user_forgot_password_reset_password.html', {'form': form})


def forgot_password_reset_password_resend_code(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)

    verification_code = str(random.randint(100000, 999999))

    verification_entry = VerifiedUsersPasswordVerificationCode.objects.get(user=user)
    verification_entry.verification_code = verification_code
    verification_entry.expires_at = now() + timedelta(minutes=1)
    verification_entry.is_code_used = False
    verification_entry.save()

    try:
        send_verification_code_email(user=user,
                                     sender_email=settings.EMAIL_HOST_USER,
                                     recipient_email=user.email,
                                     verification_code=verification_code,
                                     expiry_time='a minute')
        messages.success(request, 'A verification code has been sent to your email!')
    except Exception as e:
        messages.error(request, f'Error sending verification email: {e}')

    return redirect('forgot_password_verification', user_id=user.id)
