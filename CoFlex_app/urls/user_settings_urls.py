from django.urls import path
from ..views.user_settings_views import user_settings
from ..views.user_edit_main_email_views import (user_edit_main_email,
                                                verify_user_edit_main_email_code,
                                                verify_user_edit_main_email_code_resend_code,
                                                cancel_edit_main_email)
from ..views.user_change_password_views import (user_change_password,
                                                cancel_change_password)
from ..views.user_delete_account_views import (user_delete_account,
                                               cancel_user_delete_account)

urlpatterns = [
    path('settings_user/<int:user_id>', user_settings, name='user_settings'),

    path('settings_user/<int:user_id>/edit_email/', user_edit_main_email, name='user_edit_main_email'),
    path('settings_user/<int:user_id>/edit_email/verification_code', verify_user_edit_main_email_code,
         name='verify_user_edit_main_email_code'),
    path('settings_user/<int:user_id>/edit_email/verification_code/resend_code/',
         verify_user_edit_main_email_code_resend_code,
         name='verify_user_edit_main_email_code_resend_code'),
    path('settings_user/<int:user_id>/edit_email/verification_code/resend_code/cancel/', cancel_edit_main_email,
         name='cancel_edit_main_email'),

    path('settings_user/<int:user_id>/change_password/', user_change_password, name='user_change_password'),
    path('settings_user/<int:user_id>/change_password/cancel/', cancel_change_password, name='cancel_change_password'),

    path('settings_user/<int:user_id>/delete_account/', user_delete_account, name='user_delete_account'),
    path('settings_user/<int:user_id>/delete_account/cancel/', cancel_user_delete_account,
         name='cancel_user_delete_account'),
]
