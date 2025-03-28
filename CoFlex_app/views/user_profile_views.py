from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from ..models import VerifiedUsers


@login_required
def user_read_profile(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)

    profile = user.profile
    user_extra_details = user.user_extra_details
    user_extra_contact_details = user.user_extra_contact_details
    user_photo_details = user.user_photo_details

    context = {
        'profile': profile,
        'user': user,
        'user_extra_details': user_extra_details,
        'user_extra_contact_details': user_extra_contact_details,
        'user_photo_details': user_photo_details,
    }

    return render(request, 'user_profile/user_read_profile.html', context)