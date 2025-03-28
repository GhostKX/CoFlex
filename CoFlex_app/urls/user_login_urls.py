from django.urls import path

from ..views.user_login_logout_views import login_user

urlpatterns = [
    path('', login_user, name='login'),  # <-- This makes /login/ work
    path('login_user/', login_user, name='login_user')
]


