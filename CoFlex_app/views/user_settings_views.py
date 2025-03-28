from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def user_settings(request, user_id):
    return render(request, 'user_settings/user_settings.html', {'user_id': user_id})