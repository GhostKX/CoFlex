from django.urls import path
from ..views.subscribed_user_booking_views import locations, get_user_location, booking_location

urlpatterns = [
    path('locations/<int:user_id>/', locations, name='locations'),
    path('locations/<int:user_id>/get_user_location/', get_user_location, name='get_user_location'),
    path('locations/<int:user_id>/booking_location/<str:location_code>/', booking_location, name='booking_location')
]