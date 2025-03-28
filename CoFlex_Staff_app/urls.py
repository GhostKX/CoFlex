from django.urls import path
from .views import (staff_dashboard,
                    staff_update_profile_photo,
                    logout_staff,
                    staff_calendar_date,
                    staff_specific_date,
                    staff_date_page,
                    staff_edit_details,
                    verify_new_staff_email,
                    verify_new_staff_email_code,
                    verify_new_staff_email_code_resend_code,
                    cancel_new_staff_email,
                    booking_details_view,
                    staff_recent_actions_history,
                    staff_action_details)

urlpatterns = [
    path('dashboard/<int:staff_id>/<str:location_code>/', staff_dashboard, name='staff_dashboard'),

    path('dashboard/<int:staff_id>/<str:location_code>/staff_update_profile_photo', staff_update_profile_photo,
         name='staff_update_profile_photo'),

    path('logout/', logout_staff, name='logout_staff'),

    path('dashboard/<int:staff_id>/<str:location_code>/staff_calendar_date/', staff_calendar_date,
         name='staff_calendar_date'),
    path('dashboard/<int:staff_id>/<str:location_code>/staff_calendar_date/<str:selected_date>/staff_date_page/',
         staff_date_page, name='staff_date_page'),
    path('dashboard/<int:staff_id>/<str:location_code>/staff_specific_date/', staff_specific_date,
         name='staff_specific_date'),

    path('dashboard/<int:staff_id>/<str:location_code>/<str:booking_id>/booking_details_view/', booking_details_view, name='booking_details_view'),


    path('dashboard/<int:staff_id>/<str:location_code>/staff_edit_details/', staff_edit_details,
         name='staff_edit_details'),
    path('dashboard/<int:staff_id>/<str:location_code>/staff_edit_details/verify_new_staff_email/',
         verify_new_staff_email, name='verify_new_staff_email'),
    path(
        'dashboard/<int:staff_id>/<str:location_code>/staff_edit_details/verify_new_staff_email/verify_new_staff_email_code/',
        verify_new_staff_email_code, name='verify_new_staff_email_code'),
    path(
        'dashboard/<int:staff_id>/<str:location_code>/staff_edit_details/verify_new_staff_email/verify_new_staff_email_code/verify_new_staff_email_code_resend_code',
        verify_new_staff_email_code_resend_code, name='verify_new_staff_email_code_resend_code'),
    path(
        'dashboard/<int:staff_id>/<str:location_code>/staff_edit_details/verify_new_staff_email/verify_new_staff_email_code/cancel_new_staff_email',
        cancel_new_staff_email, name='cancel_new_staff_email'),

    path('dashboard/<int:staff_id>/<str:location_code>/recent_actions/', staff_recent_actions_history, name='staff_recent_actions_history'),
    path('dashboard/<int:staff_id>/<str:location_code>/recent_actions/<str:session_key>/<str:action_type>/action_details/', staff_action_details, name='staff_action_details')

]
