import random
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404, reverse
from django.shortcuts import render
from django.utils.timezone import now

from ..forms.user_edit_main_email_forms import *
from ..models import (VerifiedUsers, UserEditMainEmail)
from .user_recent_actions_views import user_device_activity
from .email_functions import send_verification_code_email


@login_required
def user_edit_main_email(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    user_edit = user.user_edit_main_email
    if request.method == 'POST':
        form = UserEditMainEmailForm(request.POST, user=user)
        if form.is_valid():
            user_edit.new_email = form.cleaned_data.get('new_email')

            verification_code = str(random.randint(100000, 999999))

            try:
                send_verification_code_email(user=user,
                                             sender_email=settings.EMAIL_HOST_USER,
                                             recipient_email=user_edit.new_email,
                                             verification_code=verification_code,
                                             expiry_time='a minute')

                messages.success(request, 'A verification code has been sent to your email!')

                user_edit.verification_code = verification_code
                user_edit.is_code_used = False
                user_edit.expires_at = now() + timedelta(minutes=1)
                user_edit.save()

                return redirect(reverse('verify_user_edit_main_email_code', kwargs={'user_id': user.id}))
            except Exception as e:
                messages.error(request, f'Error sending verification email: {e}')
                return redirect(f'user_read_profile', user_id=user.id)

    else:
        form = UserEditMainEmailForm(user=user)

    return render(request, 'user_edit_main_email/user_edit_main_email.html', {'form': form, 'user': user})


@login_required
def verify_user_edit_main_email_code(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    user_new_email = UserEditMainEmail.objects.get(user=user)
    new_email = user_new_email.new_email
    if request.method == 'POST':
        form = UserEditMainEmailCodeForm(request.POST, user=user)

        if form.is_valid():
            old_email = user.email
            user.email = new_email

            user.save()

            user_new_email.is_code_used = True
            user_new_email.verification_code = None

            user_new_email.save()

            changed_details = {'email': {'old': old_email, 'new': new_email}}
            user_device_activity(instance=user, request=request, activity_type='Changed Email',
                                 activity_details=changed_details)

            messages.success(request, 'User information has been updated successfully!')

            return redirect('user_read_profile', user_id=user.id)
    else:
        form = UserEditMainEmailCodeForm()

    return render(request, 'user_edit_main_email/verify_user_edit_main_email_code.html', {'form': form, 'user': user})


@login_required
def verify_user_edit_main_email_code_resend_code(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    user_new_email = UserEditMainEmail.objects.get(user=user).new_email

    verification_code = str(random.randint(100000, 999999))

    verification_entry = UserEditMainEmail.objects.get(user=user)
    verification_entry.verification_code = verification_code
    verification_entry.expires_at = now() + timedelta(minutes=1)
    verification_entry.is_code_used = False
    verification_entry.save()

    try:
        send_verification_code_email(user=user,
                                     sender_email=settings.EMAIL_HOST_USER,
                                     recipient_email=user_new_email,
                                     verification_code=verification_code,
                                     expiry_time='a minute')
        messages.success(request, 'A verification code has been sent to your email!')
    except Exception as e:
        messages.error(request, f'Error sending verification email: {e}')

    return redirect('verify_user_edit_main_email_code', user_id=user.id)


@login_required
def cancel_edit_main_email(request, user_id):
    messages.info(request, "Your New Email was not verified!")
    return redirect('user_read_profile', user_id=user_id)