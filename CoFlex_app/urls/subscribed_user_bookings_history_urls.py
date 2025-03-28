from django.urls import path
from ..views.subscribed_user_bookings_history_views import subscribed_user_all_bookings, subscribed_user_booking_details, subscribed_user_cancel_booking

urlpatterns = [
    path('bookings_history/<int:user_id>/', subscribed_user_all_bookings, name='subscribed_user_all_bookings'),
    path('bookings_history/<int:user_id>/<str:booking_id>/booking_details/', subscribed_user_booking_details, name='subscribed_user_booking_details'),
    path('bookings_history/<int:user_id>/<str:booking_id>/booking_details/cancel_booking/', subscribed_user_cancel_booking, name='subscribed_user_cancel_booking')
]