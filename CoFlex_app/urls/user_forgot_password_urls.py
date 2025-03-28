from django.urls import path

from ..views.user_forgot_password_views import (forgot_password_email,
                                                forgot_password_verification,
                                                forgot_password_reset_password,
                                                forgot_password_reset_password_resend_code)

urlpatterns = [
    path('forgot_password_email/', forgot_password_email, name='forgot_password_email'),
    path('forgot_password_verification/<int:user_id>', forgot_password_verification, name='forgot_password_verification'),
    path('forgot_password_reset_password/<int:user_id>', forgot_password_reset_password, name='forgot_password_reset_password'),
    path('forgot_password_reset_password_resend_code/<int:user_id>', forgot_password_reset_password_resend_code,
         name='forgot_password_reset_password_resend_code')
]