import random
from datetime import timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.shortcuts import redirect, get_object_or_404, reverse
from django.shortcuts import render
from django.utils.html import escape
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_protect
from ..forms.user_edit_info_forms import *
from ..models import (VerifiedUsers, SecondEmailVerificationCode)
from .user_recent_actions_views import user_device_activity


@login_required
def user_edit_basic_info(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    profile = user.profile
    if request.method == 'POST':
        form = UserEditBasicInfoForm(request.POST, instance=user)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')

            changed_details = {}
            if user.first_name != first_name:
                changed_details['First Name'] = {'old': user.first_name, 'new': first_name}

            if user.last_name != last_name:
                changed_details['Last Name'] = {'old': user.last_name, 'new': last_name}

            user.first_name = first_name if first_name else user.first_name
            user.last_name = last_name if last_name else user.last_name

            username = form.cleaned_data.get('username')
            phone_number = form.cleaned_data.get('phone_number')

            if profile.username != username:
                changed_details['Username'] = {'old': profile.username, 'new': username}

            if profile.phone_number != phone_number:
                changed_details['Phone Number'] = {'old': profile.phone_number, 'new': phone_number}

            profile.username = username
            profile.phone_number = phone_number if phone_number else profile.phone_number

            user.save()
            profile.save()

            if changed_details:
                user_device_activity(instance=user, request=request, activity_type='Updated Basic Info',
                                     activity_details=changed_details)

            messages.success(request, 'User information updated successfully!')
            return redirect('user_read_profile', user_id=user.id)

    else:
        initial_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'username': profile.username,
            'phone_number': profile.phone_number,
        }
        form = UserEditBasicInfoForm(initial=initial_data, instance=user)

    return render(request, 'user_edit_info/user_edit_basic_info.html', {'form': form, 'user': user, 'profile': profile})


@login_required
def user_edit_personal_info(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    user_extra_details = user.user_extra_details
    user_address_details = user.profile
    if request.method == 'POST':
        form = UserExtraDetailsForm(request.POST, instance=user_extra_details)
        if form.is_valid():
            changed_details = {}

            bio = form.cleaned_data.get('bio')
            if user_extra_details.bio != bio:
                changed_details['Bio'] = {'old': user_extra_details.bio, 'new': bio}

            dob = form.cleaned_data.get('dob')
            if user_extra_details.dob != dob:
                changed_details['Dob'] = {'old': str(user_extra_details.dob), 'new': str(dob)}

            gender = form.cleaned_data.get('gender')
            if user_extra_details.gender != gender:
                changed_details['Gender'] = {'old': user_extra_details.gender, 'new': gender}

            age = form.cleaned_data.get('age')
            if user_extra_details.age != age:
                changed_details['Age'] = {'old': user_extra_details.age, 'new': age}

            website = form.cleaned_data.get('website')
            if user_extra_details.website != website:
                changed_details['Website'] = {'old': user_extra_details.website, 'new': website}

            address = form.cleaned_data.get('address')
            if user_address_details.address != address:
                changed_details['Address'] = {'old': user_address_details.address, 'new': address}

            user_extra_details.bio = bio
            user_extra_details.dob = dob
            user_extra_details.gender = gender
            user_extra_details.age = age
            user_extra_details.website = website
            user_address_details.address = address

            if changed_details:
                user_device_activity(instance=user, request=request, activity_type='Updated Personal Info',
                                     activity_details=changed_details)

            user_extra_details.save()
            user_address_details.save()
            user.save()

            messages.success(request, 'User information updated successfully!')
            return redirect('user_read_profile', user_id=user.id)

    else:
        initial_data = {
            'bio': user_extra_details.bio,
            'dob': user_extra_details.dob,
            'gender': user_extra_details.gender,
            'age': user_extra_details.age,
            'website': user_extra_details.website,
            'address': user_address_details.address,
        }
        form = UserExtraDetailsForm(initial=initial_data, instance=user_extra_details)

    return render(request, 'user_edit_info/user_edit_personal_info.html', {'form': form,
                                                                           'user': user,
                                                                           'user_address_details': user_address_details,
                                                                           'user_extra_details': user_extra_details})


@login_required
def user_edit_secondary_info(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    user_edit_secondary_info = user.user_extra_contact_details
    user_second_email = user.second_email_verification_code

    if request.method == 'POST':
        form = UserExtraContactDetailsForm(request.POST, instance=user)
        if form.is_valid():

            changed_details = {}
            second_phone_number = form.cleaned_data.get('second_phone_number')
            if user_edit_secondary_info.second_phone_number != second_phone_number:
                changed_details['Second Phone Number'] = {'old': user_edit_secondary_info.second_phone_number,
                                                          'new': second_phone_number}

            second_address = form.cleaned_data.get('second_address')
            if user_edit_secondary_info.second_address != second_address:
                changed_details['Second Address'] = {'old': user_edit_secondary_info.second_address,
                                                     'new': second_address}

            user_edit_secondary_info.second_phone_number = second_phone_number
            user_edit_secondary_info.second_address = second_address
            user_edit_secondary_info.save()

            if changed_details:
                user_device_activity(instance=user, request=request, activity_type='Updated Secondary Info',
                                     activity_details=changed_details)

            second_email = form.cleaned_data.get('second_email')
            if user_edit_secondary_info.second_email != second_email:
                if second_email:
                    user_second_email.second_email = second_email
                    user_second_email.save()
                    return redirect('verify_second_email', user_id=user.id)
                else:
                    changed_details = {'Second Email': {'old': user_edit_secondary_info.second_email, 'new': second_email}}

                    user_device_activity(instance=user, request=request, activity_type='Changed Second Email',
                                         activity_details=changed_details)
                    user_edit_secondary_info.second_email = form.cleaned_data.get('second_email')
                    user_edit_secondary_info.save()

            messages.success(request, 'User information updated successfully!')
            return redirect('user_read_profile', user_id=user.id)
    else:
        initial_data = {
            'second_email': user_edit_secondary_info.second_email,
            'second_phone_number': user_edit_secondary_info.second_phone_number,
            'second_address': user_edit_secondary_info.second_address,
        }
        form = UserExtraContactDetailsForm(initial=initial_data, instance=user)

    return render(request, 'user_edit_info/user_edit_secondary_info.html', {'form': form, 'user': user})


@login_required
def verify_second_email(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    user_second_email_table = user.second_email_verification_code

    verification_code = str(random.randint(100000, 999999))

    try:
        send_mail('Verification Code',
                  f'<p>Message to {escape(user_second_email_table.second_email)}',
                  'settings.EMAIL_HOST_USER',
                  [user_second_email_table.second_email],
                  fail_silently=False,
                  html_message=f'<html><body style="font-size: 18px; font-family: Arial, sans-serif;">'
                               f'<p>{escape(user.first_name)} {escape(user.last_name)},'
                               f' your verification code is: <b style="font-size: 24px; font-weight: bold;">{verification_code}</b>'
                               f'</p>'
                               f'<p>This code will expire in a minute!</p>'
                               f'</body></html>')
        messages.success(request, 'A verification code has been sent to your email!')

        user_second_email_table.verification_code = verification_code
        user_second_email_table.is_code_used = False
        user_second_email_table.expires_at = now() + timedelta(minutes=1)
        user_second_email_table.save()

        return redirect(reverse('verify_second_email_code', kwargs={'user_id': user.id}))
    except Exception as e:
        messages.error(request, f'Error sending verification email: {e}')
        return redirect(f'user_read_profile', user_id=user.id)


@login_required
def verify_second_email_code(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    user_second_email_table = SecondEmailVerificationCode.objects.get(user=user)

    if request.method == 'POST':
        form = SecondEmailVerificationCodeForm(request.POST, user=user)

        if form.is_valid():
            changed_details = {'Second Email': {'old': user.user_extra_contact_details.second_email,
                                                'new': user_second_email_table.second_email}}
            user.user_extra_contact_details.second_email = user_second_email_table.second_email

            user_second_email_table.is_code_used = True
            user_second_email_table.verification_code = None
            user_second_email_table.save()
            user.user_extra_contact_details.save()

            if changed_details:
                user_device_activity(instance=user, request=request, activity_type='Changed Second Email',
                                     activity_details=changed_details)

            messages.success(request, 'User information has been updated successfully!')

            return redirect('user_read_profile', user_id=user.id)
    else:
        form = SecondEmailVerificationCodeForm()

    return render(request, 'user_edit_info/verify_second_email_code.html', {'form': form, 'user': user,
                                                                            'user_second_email': user_second_email_table.second_email})


@login_required
def verify_second_email_code_resend_code(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    user_second_email_table = SecondEmailVerificationCode.objects.get(user=user)

    verification_code = str(random.randint(100000, 999999))

    user_second_email_table.verification_code = verification_code
    user_second_email_table.expires_at = now() + timedelta(minutes=1)
    user_second_email_table.is_code_used = False
    user_second_email_table.save()

    try:
        send_mail('Verification Code',
                  f'<p>Message to {escape(user_second_email_table.second_email)}',
                  'settings.EMAIL_HOST_USER',
                  [user_second_email_table.second_email],
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

    return redirect('verify_second_email_code', user_id=user.id)


@login_required
def cancel_second_email(request, user_id):
    messages.info(request, "Your Second Email was not verified!")
    return redirect('user_read_profile', user_id=user_id)


@login_required
@csrf_protect
def update_profile_photo(request, user_id):
    if request.method == 'POST' and request.FILES.get('profile_photo'):

        profile_photo = request.FILES['profile_photo']

        file_type = os.path.splitext(profile_photo.name)[-1]
        file_new_name = f'user_{user_id}{file_type}'

        try:
            user = VerifiedUsers.objects.get(id=user_id)
            user_photo_details = user.user_photo_details

            if user_photo_details.photo_path:
                old_photo_path = os.path.join(settings.MEDIA_ROOT, user_photo_details.photo_path)
                os.remove(old_photo_path)

            fs = FileSystemStorage(location='media/profile_images/')
            saved_file_path = fs.save(file_new_name, profile_photo)

            # Save the uploaded file
            user_photo_details.profile_photo = f'profile_images/{file_new_name}'
            user_photo_details.photo_path = f'profile_images/{saved_file_path}'
            user_photo_details.uploaded_time = now()
            user_photo_details.save()

            user_device_activity(instance=user, request=request, activity_type='Updated Profile Photo',
                                 activity_details={})

            messages.success(request, 'Profile photo updated successfully')

        except Exception as e:
            messages.error(request, f'Error uploading photo: {str(e)}')

    return redirect('user_read_profile', user_id=user_id)
