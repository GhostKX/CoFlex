import random
from datetime import timedelta
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, get_object_or_404, reverse
from django.shortcuts import render
from django.utils.html import escape
from django.utils.timezone import now
from ..forms.user_registration_forms import (UserRegistrationForm, UserVerificationForm, UserProfileForm)
from ..models import (UnverifiedUsers, UnverifiedUsersVerificationCode,
                      VerifiedUsers, Profile, UserDetails,
                      UserExtraDetails, UserExtraContactDetails, UserPhotoDetails,
                      VerifiedUsersPasswordVerificationCode,
                      SecondEmailVerificationCode,
                      UserEditMainEmail,
                      UserAccountDeletion, UserAccountRestoration, UserAccountRecoveryCode,
                      UserSignUpLoginLogoutActivity)
from .user_recent_actions_views import user_signed_up_activity, user_device_activity


def home_page(request):
    return render(request, 'home.html')


def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

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
                user.save()

                UnverifiedUsersVerificationCode.objects.create(
                    user=user,
                    verification_code=verification_code,
                    is_code_used=False,
                    expires_at=now() + timedelta(minutes=1)
                )
                return redirect(reverse('verify_user', kwargs={'user_id': user.id}))
            except Exception as e:
                messages.error(request, f'Error sending verification email: {e}')
                return redirect(f'register_user')
    else:
        form = UserRegistrationForm()

    return render(request, 'user_registration/register_user.html', {'form': form})


def cancel_verification(request, user_id):
    user = get_object_or_404(UnverifiedUsers, id=user_id)
    user.delete()
    messages.info(request, "Your registration process has been canceled. Please start again.")
    return redirect('register_user')


def verify_user(request, user_id):
    user = get_object_or_404(UnverifiedUsers, id=user_id)

    if request.method == 'POST':
        form = UserVerificationForm(request.POST, user=user)

        if form.is_valid():
            verification_entry = UnverifiedUsersVerificationCode.objects.get(user=user)
            verification_entry.is_code_used = True
            verification_entry.verification_code = None
            verification_entry.save()

            messages.success(request, 'Your account has been verified successfully!')

            verified_user = VerifiedUsers.objects.create(
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                registered_datetime=user.registered_datetime,
                password=user.password
            )

            verified_user.save()
            user_signed_up_activity(instance=verified_user, request=request, created=True)

            Profile.objects.create(user=verified_user)
            UserDetails.objects.create(user=verified_user)
            UserExtraDetails.objects.create(user=verified_user)
            UserExtraContactDetails.objects.create(user=verified_user)
            UserPhotoDetails.objects.create(user=verified_user)
            VerifiedUsersPasswordVerificationCode.objects.create(user=verified_user)
            SecondEmailVerificationCode.objects.create(user=verified_user)
            UserEditMainEmail.objects.create(user=verified_user)
            UserAccountDeletion.objects.create(user=verified_user)
            UserAccountRestoration.objects.create(user=verified_user)
            UserAccountRecoveryCode.objects.create(user=verified_user)

            user.delete()

            return redirect('user_complete_profile', user_id=verified_user.id)
    else:
        form = UserVerificationForm()

    return render(request, 'user_registration/verify_user.html', {'form': form, 'user': user})


def resend_code(request, user_id):
    user = get_object_or_404(UnverifiedUsers, id=user_id)

    verification_code = str(random.randint(100000, 999999))
    verification_entry = UnverifiedUsersVerificationCode.objects.filter(user=user).first()

    if verification_entry:
        verification_entry.verification_code = verification_code
        verification_entry.expires_at = now() + timedelta(minutes=1)
        verification_entry.is_code_used = False
        verification_entry.save()
    else:
        UnverifiedUsersVerificationCode.objects.create(
            user=user,
            verification_code=verification_code,
            is_code_used=False,
            expires_at=now() + timedelta(minutes=1)
        )

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
    except Exception as e:
        messages.error(request, f'Error sending verification email: {e}')

    return redirect('verify_user', user_id=user.id)


def user_complete_profile(request, user_id):
    verified_user = get_object_or_404(VerifiedUsers, id=user_id)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=verified_user.profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = verified_user

            changed_fields = {}

            if form.cleaned_data.get('username'):
                profile.username = form.cleaned_data['username']
                changed_fields['Username'] = {'old': profile.username, 'new': profile.username}

            if form.cleaned_data.get('phone_number'):
                profile.phone_number = form.cleaned_data['phone_number']
                changed_fields['Phone Number'] = {'old': profile.phone_number, 'new': profile.phone_number}

            if form.cleaned_data.get('address'):
                profile.address = form.cleaned_data['address']
                changed_fields['Address'] = {'old': profile.address, 'new': profile.address}

            profile.save()

            session_key = request.session.session_key
            instance = UserSignUpLoginLogoutActivity.objects.get(user=verified_user, session_key=session_key)

            instance.is_Logged_in = False
            instance.save()

            if changed_fields:
                user_device_activity(instance=instance.user, request=request, activity_type='Updated Profile Details', activity_details=changed_fields)

            messages.success(request, 'Profile updated successfully!')
            return redirect('user_read_profile', user_id=verified_user.id)
    else:
        form = UserProfileForm(instance=verified_user.profile)

    return render(request, 'user_registration/user_complete_profile.html', {'form': form, 'user': verified_user})
