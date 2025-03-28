from django.urls import path

from ..views.user_edit_info_views import (user_edit_basic_info,
                                          user_edit_personal_info,
                                          user_edit_secondary_info,
                                          cancel_second_email,
                                          verify_second_email,
                                          verify_second_email_code,
                                          verify_second_email_code_resend_code,
                                          update_profile_photo)

urlpatterns = [
    path('user_edit_basic_info/<int:user_id>', user_edit_basic_info, name='user_edit_basic_info'),
    path('user_edit_personal_info/<int:user_id>', user_edit_personal_info, name='user_edit_personal_info'),
    path('user_edit_secondary_info/<int:user_id>', user_edit_secondary_info, name='user_edit_secondary_info'),
    path('user_edit_secondary_info/<int:user_id>/verify_second_email/', verify_second_email,
         name='verify_second_email'),
    path('user_edit_secondary_info/<int:user_id>/verify_second_email/verify_second_email_code/',
         verify_second_email_code,
         name='verify_second_email_code'),
    path('user_edit_secondary_info/<int:user_id>/verify_second_email/verify_second_email_code/resend_code',
         verify_second_email_code_resend_code, name='verify_second_email_code_resend_code'),
    path('user_edit_secondary_info/<int:user_id>/verify_second_email/verify_second_email_code/cancel/',
         cancel_second_email, name='cancel_second_email'),
    path('user_edit_profile/<int:user_id>/update_profile_photo/', update_profile_photo, name='update_profile_photo'),
]
