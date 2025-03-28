from django.urls import path
from ..views.user_profile_views import user_read_profile

urlpatterns = [
    path('profile_user/<int:user_id>/', user_read_profile, name='user_read_profile'),
]
