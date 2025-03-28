from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from ..views.user_registration_views import home_page

# Importing all urls
urlpatterns = [
    path('', home_page, name='home'),
    path('register/', include('CoFlex_app.urls.user_registration_urls')),
    path('login/', include('CoFlex_app.urls.user_login_urls')),
    path('logout/', include('CoFlex_app.urls.user_logout_urls')),
    path('forgot-password/', include('CoFlex_app.urls.user_forgot_password_urls')),
    path('edit-info/', include('CoFlex_app.urls.user_edit_info_urls')),
    path('dashboard/', include('CoFlex_app.urls.user_dashboard_urls')),
    path('profile/', include('CoFlex_app.urls.user_profile_urls')),
    path('settings/', include('CoFlex_app.urls.user_settings_urls')),
    path('account-recovery/', include('CoFlex_app.urls.user_account_recovery_urls')),
    path('booking/', include('CoFlex_app.urls.subscribed_user_locations_urls')),
    path('all_bookings/', include('CoFlex_app.urls.subscribed_user_bookings_history_urls')),
    path('history/', include('CoFlex_app.urls.user_recent_actions_urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)