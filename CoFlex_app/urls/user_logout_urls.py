from django.urls import path

from ..views.user_login_logout_views import logout_user

urlpatterns = [
    path('logout_user/', logout_user, name='logout_user'),

]