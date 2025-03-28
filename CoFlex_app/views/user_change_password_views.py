from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from .user_recent_actions_views import user_device_activity
from ..models import (VerifiedUsers)


@login_required
def user_change_password(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not old_password:
            messages.error(request, 'Old password can not be empty!')

        old_password_check = user.check_password(old_password)
        if not old_password_check:
            messages.error(request, 'Incorrect old password!')

        if not new_password:
            messages.error(request, 'New password can not be empty!')

        if not confirm_password:
            messages.error(request, 'New password can not be empty!')

        if new_password != confirm_password:
            messages.error(request, 'New password fields do not match!')

        try:
            validate_password(new_password)
        except messages.error as e:
            messages.error(e.messages)

        user.set_password(new_password)
        user.save()

        changed_details = {'Password': {'old': 'hashed', 'new': 'hashed'}}
        if changed_details:
            user_device_activity(instance=user, request=request, activity_type='Changed Password',
                                 activity_details=changed_details)

        logout(request)

        messages.success(request, 'Your password has been changed successfully!')
        return redirect('login_user')

    return render(request, 'user_change_password/user_change_password.html', {'user': user})


@login_required
def cancel_change_password(request, user_id):
    messages.info(request, "Your Password was not changed!")
    return redirect('user_read_profile', user_id=user_id)