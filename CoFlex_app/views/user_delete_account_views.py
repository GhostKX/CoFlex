import os
import shutil
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.utils.timezone import now

from ..forms.user_delete_account_forms import *

from ..models import (VerifiedUsers, UserAccountDeletion, DeletedAccountsMainInfo, DeletedAccountsProfile,
                      DeletedAccountsDetails,
                      DeletedAccountsExtraDetails, DeletedAccountsPhoto, DeletedAccountsSpecifics)
from .user_recent_actions_views import user_device_activity


@login_required
def user_delete_account(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    user_deletion = UserAccountDeletion.objects.filter(user=user).first()
    if request.method == 'POST':
        form = UserDeleteAccountForm(request.POST, user=user)
        if form.is_valid():
            user.is_active = False
            user_deletion.is_deleted = True
            user_deletion.deletion_time = now()
            user_deletion.deletion_details = 'User Deleted'
            user_deletion.deletion_attempts += 1

            if user_deletion.deletion_attempts >= 7:
                user_deletion.is_blocked = True

            user.save()
            user_deletion.save()

            deletion_entry = DeletedAccountsMainInfo.objects.create(
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                last_login=user.last_login,
                registered_datetime=user.registered_datetime,
                is_subscribed=user.user_details.is_subscribed,
                password=user.password
            )

            DeletedAccountsProfile.objects.create(
                user=deletion_entry,
                username=user.profile.username,
                phone_number=user.profile.phone_number,
                address=user.profile.address
            )

            DeletedAccountsDetails.objects.create(
                user=deletion_entry,
                bio=user.user_extra_details.bio,
                dob=user.user_extra_details.dob,
                gender=user.user_extra_details.gender,
                age=user.user_extra_details.age,
                website=user.user_extra_details.website
            )

            DeletedAccountsExtraDetails.objects.create(
                user=deletion_entry,
                second_email=user.user_extra_contact_details.second_email,
                second_phone_number=user.user_extra_contact_details.second_phone_number,
                second_address=user.user_extra_contact_details.second_address
            )

            original_photo = user.user_photo_details.profile_photo
            if original_photo:
                file_name = os.path.basename(original_photo.name)
                new_photo_path = os.path.join(settings.MEDIA_ROOT, 'deleted_profile_images', )
                shutil.copy2(original_photo.path, new_photo_path)

                DeletedAccountsPhoto.objects.create(
                    user=deletion_entry,
                    profile_photo=f'deleted_profile_images/{file_name}',
                    photo_path=f'deleted_profile_images/{file_name}',
                    uploaded_time=user.user_photo_details.uploaded_time
                )
            else:
                DeletedAccountsPhoto.objects.create(
                    user=deletion_entry,
                    profile_photo=user.user_photo_details.profile_photo,
                    photo_path=user.user_photo_details.photo_path,
                    uploaded_time=user.user_photo_details.uploaded_time
                )

            DeletedAccountsSpecifics.objects.create(
                user=deletion_entry,
                is_deleted=user.user_account_deletion.is_deleted,
                deletion_time=user.user_account_deletion.deletion_time,
                deletion_details=user.user_account_deletion.deletion_details,
                deletion_attempts=user.user_account_deletion.deletion_attempts,
                is_blocked=user.user_account_deletion.is_blocked
            )

            user_device_activity(instance=user, request=request, activity_type='Account Deletion', activity_details={})

            logout(request)
            messages.success(request, 'Your account has been deleted successfully!')

            return redirect('home')

    else:
        form = UserDeleteAccountForm(user=user)

    return render(request, 'user_delete_account/user_delete_account.html', {'form': form, 'user': user})


@login_required
def cancel_user_delete_account(request, user_id):
    messages.info(request, "Your account deletion has been canceled!")
    return redirect('user_settings', user_id=user_id)
