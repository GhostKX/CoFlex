from django.urls import path
from ..views.user_registration_views import (register_user, verify_user,
                                             resend_code, cancel_verification, user_complete_profile)

urlpatterns = [
    path('register_user/', register_user, name='register_user'),
    path('verify/<int:user_id>', verify_user, name='verify_user'),
    path('resend/<int:user_id>', resend_code, name='resend_code'),
    path('cancel_verification/<int:user_id>', cancel_verification, name='cancel_verification'),
    path('complete/<int:user_id>', user_complete_profile, name='user_complete_profile'),
]
