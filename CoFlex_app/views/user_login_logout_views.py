from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth import get_backends
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..forms.user_login_forms import UserLoginForm, StaffAccounts, VerifiedUsers
from django.urls import reverse


def login_user(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():

            user = form.cleaned_data.get('user')
            user_type = form.cleaned_data.get('user_type')

            if user_type == 'staff':
                # Authentication backend
                backend = get_backends()[0]
                print(backend)
                user.backend = f"{backend.__module__}.{backend.__class__.__name__}"

                login(request, user, backend=user.backend)
                print(f"Staff is_authenticated after login: {request.user.is_authenticated}")
                return redirect(reverse('staff_dashboard', kwargs={'staff_id': user.id, 'location_code': user.location_code}))
            else:
                # Authentication backend
                backend = get_backends()[1]
                print(backend)
                user.backend = f"{backend.__module__}.{backend.__class__.__name__}"

                login(request, user, backend=user.backend)
                print(f"User is_authenticated after login: {request.user.is_authenticated}")
                messages.success(request, f'Welcome back, {user.first_name} {user.last_name}!')
                return redirect('user_read_profile', user_id=user.id)

        else:
            messages.error(request, 'Invalid login credentials. Please try again.')
    else:
        form = UserLoginForm()

    return render(request, 'user_login/login_user.html', {'form': form})


@login_required()
def logout_user(request):
    logout(request)

    messages.success(request, "You have been logged out successfully!")
    return redirect('home')
