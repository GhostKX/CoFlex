from django.contrib import admin
from .models import AllBookings, AllBookingDetails


@admin.register(AllBookings)
class AllBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'booking_id', 'created_date', 'created_time')
    search_fields = ('user', 'location')


@admin.register(AllBookingDetails)
class AllBookingDetailsAdmin(admin.ModelAdmin):
    list_display = ('all_booking', 'start_date', 'start_time', 'end_date', 'end_time', 'special_requests', 'status')
    search_fields = ('booking', 'start_date', 'status')

