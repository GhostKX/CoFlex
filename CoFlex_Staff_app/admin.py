from django.contrib import admin
from .models import (StaffAccounts, StaffAccountsProfiles, StaffPhotoDetails, StaffEditMainEmail,
                     C_Space_Yunusabad_Bookings, C_Space_Modera_Bookings_Details,
                     C_Space_Modera_Bookings, C_Space_Yunusabad_Bookings_Details,
                     C_Space_Labzak_Bookings, C_Space_Labzak_Bookings_Details,
                     C_Space_Chust_Bookings, C_Space_Chust_Bookings_Details,
                     C_Space_Elbek_Bookings, C_Space_Elbek_Bookings_Details,
                     C_Space_Airport_Bookings, C_Space_Airport_Bookings_Details,
                     Ground_Zero_Minor_Bookings, Ground_Zero_Minor_Bookings_Details,
                     Ground_Zero_Sharq_Bookings, Ground_Zero_Sharq_Bookings_Details,
                     Ground_Zero_Kitob_Olami_Bookings, Ground_Zero_Kitob_Olami_Bookings_Details,
                     Bb_Works_Bookings, Bb_Works_Bookings_Details,
                     U_Enter_Bookings, U_Enter_Bookings_Details,
                     Impact_Coworking_Bookings, Impact_Coworking_Bookings_Details,
                     Impulse_Coworking_Bookings, Impulse_Coworking_Bookings_Details,
                     Hub_Coworking_Bookings, Hub_Coworking_Bookings_Details,
                     Wiut_Bookings, Wiut_Bookings_Details,
                     StaffSignUpLoginLogoutActivity, StaffDeviceActivities)
from django.contrib.auth.hashers import make_password


@admin.register(StaffAccounts)
class StaffAccountsAdmin(admin.ModelAdmin):
    list_display = ('staff_first_name', 'staff_last_name', 'email', 'location_code', 'is_active')
    search_fields = ('staff_first_name', 'staff_last_name', 'email', 'location_code')

    def get_readonly_fields(self, request, obj=None):
        # Make `is_staff` and `is_superuser` readonly in the admin panel
        readonly_fields = ['is_staff', 'is_superuser', 'is_active']
        if obj:
            # Additional logic to prevent staff users from editing
            if obj.is_superuser:
                readonly_fields.append('is_superuser')
            if obj.is_staff:
                readonly_fields.append('is_staff')

        return self.readonly_fields + tuple(readonly_fields)

    def save_model(self, request, obj, form, change):

        # Hashing the password only when creating a new staff member or changing the password
        if change:
            original_obj = StaffAccounts.objects.get(pk=obj.pk)
            if original_obj.password != obj.password:  # Only hashing if password was changed
                obj.password = make_password(obj.password)
        else:
            obj.password = make_password(obj.password)  # Always hashing for new staff members

        super().save_model(request, obj, form, change)


@admin.register(StaffAccountsProfiles)
class StaffAccountsProfilesAdmin(admin.ModelAdmin):
    list_display = ('staff', 'staff_username', 'phone_number', 'address')
    search_fields = ('staff', 'staff_username', 'phone_number')


@admin.register(StaffPhotoDetails)
class StaffPhotoDetailsAdmin(admin.ModelAdmin):
    list_display = ('staff', 'profile_photo', 'photo_path', 'uploaded_time')
    search_fields = ('staff', 'profile_photo', 'photo_path')


@admin.register(StaffEditMainEmail)
class StaffEditMainEmailAdmin(admin.ModelAdmin):
    list_display = ('staff', 'new_email', 'verification_code', 'is_code_used', 'expires_at')
    search_fields = ('staff', 'new_email')


@admin.register(StaffSignUpLoginLogoutActivity)
class UserSignUpLoginLogoutActivityAdmin(admin.ModelAdmin):
    list_display = ('staff', 'session_key', 'ip_address', 'device_type', 'browser', 'operating_system', 'city', 'country', 'date_time', 'is_Logged_in', 'action')
    search_fields = ('staff__staff_email', 'session_key', 'ip_address', 'browser', 'city', 'country')
    list_filter = ('action', 'is_Logged_in', 'date_time', 'country')
    ordering = ('-date_time',)


@admin.register(StaffDeviceActivities)
class UserDeviceActivitiesAdmin(admin.ModelAdmin):
    list_display = ('staff_session', 'activity_type', 'activity_details', 'date_time')
    search_fields = ('staff_session__staff__staff_email', 'activity_type')
    list_filter = ('activity_type', 'date_time')
    ordering = ('-date_time',)


@admin.register(C_Space_Yunusabad_Bookings)
class C_Space_Yunusabad_BookingsAdmin(admin.ModelAdmin):
    list_display = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                    'location_code', 'location_name', 'created_date', 'created_time')
    search_fields = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                     'location_code', 'location_name')


@admin.register(C_Space_Yunusabad_Bookings_Details)
class C_Space_Yunusabad_Bookings_DetailsAdmin(admin.ModelAdmin):
    list_display = ('location_booking', 'start_date', 'start_time', 'end_date', 'end_time', 'special_requests', 'status')
    search_fields = ('location_booking',)


@admin.register(C_Space_Modera_Bookings)
class C_Space_Modera_BookingsAdmin(admin.ModelAdmin):
    list_display = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                    'location_code', 'location_name', 'created_date', 'created_time')
    search_fields = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                     'location_code', 'location_name')


@admin.register(C_Space_Modera_Bookings_Details)
class C_Space_Modera_Bookings_DetailsAdmin(admin.ModelAdmin):
    list_display = ('location_booking', 'start_date', 'start_time', 'end_date', 'end_time', 'special_requests', 'status')
    search_fields = ('location_booking',)


@admin.register(C_Space_Labzak_Bookings)
class C_Space_Labzak_BookingsAdmin(admin.ModelAdmin):
    list_display = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                    'location_code', 'location_name', 'created_date', 'created_time')
    search_fields = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                     'location_code', 'location_name')


@admin.register(C_Space_Labzak_Bookings_Details)
class C_Space_Labzak_Bookings_DetailsAdmin(admin.ModelAdmin):
    list_display = ('location_booking', 'start_date', 'start_time', 'end_date', 'end_time', 'special_requests', 'status')
    search_fields = ('location_booking',)


@admin.register(C_Space_Chust_Bookings)
class C_Space_Chust_BookingsAdmin(admin.ModelAdmin):
    list_display = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                    'location_code', 'location_name', 'created_date', 'created_time')
    search_fields = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                     'location_code', 'location_name')


@admin.register(C_Space_Chust_Bookings_Details)
class C_Space_Chust_Bookings_DetailsAdmin(admin.ModelAdmin):
    list_display = ('location_booking', 'start_date', 'start_time', 'end_date', 'end_time', 'special_requests', 'status')
    search_fields = ('location_booking',)


@admin.register(C_Space_Elbek_Bookings)
class C_Space_Elbek_BookingsAdmin(admin.ModelAdmin):
    list_display = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                    'location_code', 'location_name', 'created_date', 'created_time')
    search_fields = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                     'location_code', 'location_name')


@admin.register(C_Space_Elbek_Bookings_Details)
class C_Space_Elbek_Bookings_DetailsAdmin(admin.ModelAdmin):
    list_display = ('location_booking', 'start_date', 'start_time', 'end_date', 'end_time', 'special_requests', 'status')
    search_fields = ('location_booking',)


@admin.register(C_Space_Airport_Bookings)
class C_Space_Airport_BookingsAdmin(admin.ModelAdmin):
    list_display = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                    'location_code', 'location_name', 'created_date', 'created_time')
    search_fields = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                     'location_code', 'location_name')


@admin.register(C_Space_Airport_Bookings_Details)
class C_Space_Airport_Bookings_DetailsAdmin(admin.ModelAdmin):
    list_display = ('location_booking', 'start_date', 'start_time', 'end_date', 'end_time', 'special_requests', 'status')
    search_fields = ('location_booking',)


@admin.register(Ground_Zero_Minor_Bookings)
class Ground_Zero_Minor_BookingsAdmin(admin.ModelAdmin):
    list_display = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                    'location_code', 'location_name', 'created_date', 'created_time')
    search_fields = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                     'location_code', 'location_name')


@admin.register(Ground_Zero_Minor_Bookings_Details)
class Ground_Zero_Minor_Bookings_DetailsAdmin(admin.ModelAdmin):
    list_display = ('location_booking', 'start_date', 'start_time', 'end_date', 'end_time', 'special_requests', 'status')
    search_fields = ('location_booking',)


@admin.register(Ground_Zero_Sharq_Bookings)
class Ground_Zero_Sharq_BookingsAdmin(admin.ModelAdmin):
    list_display = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                    'location_code', 'location_name', 'created_date', 'created_time')
    search_fields = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                     'location_code', 'location_name')


@admin.register(Ground_Zero_Sharq_Bookings_Details)
class Ground_Zero_Sharq_Bookings_DetailsAdmin(admin.ModelAdmin):
    list_display = ('location_booking', 'start_date', 'start_time', 'end_date', 'end_time', 'special_requests', 'status')
    search_fields = ('location_booking',)


@admin.register(Ground_Zero_Kitob_Olami_Bookings)
class Ground_Zero_Kitob_Olami_BookingsAdmin(admin.ModelAdmin):
    list_display = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                    'location_code', 'location_name', 'created_date', 'created_time')
    search_fields = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                     'location_code', 'location_name')


@admin.register(Ground_Zero_Kitob_Olami_Bookings_Details)
class Ground_Zero_Kitob_Olami_Bookings_DetailsAdmin(admin.ModelAdmin):
    list_display = ('location_booking', 'start_date', 'start_time', 'end_date', 'end_time', 'special_requests', 'status')
    search_fields = ('location_booking',)


@admin.register(Bb_Works_Bookings)
class Bb_Works_BookingsAdmin(admin.ModelAdmin):
    list_display = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                    'location_code', 'location_name', 'created_date', 'created_time')
    search_fields = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                     'location_code', 'location_name')


@admin.register(Bb_Works_Bookings_Details)
class Bb_Works_Bookings_DetailsAdmin(admin.ModelAdmin):
    list_display = ('location_booking', 'start_date', 'start_time', 'end_date', 'end_time', 'special_requests', 'status')
    search_fields = ('location_booking',)


@admin.register(U_Enter_Bookings)
class U_Enter_BookingsAdmin(admin.ModelAdmin):
    list_display = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                    'location_code', 'location_name', 'created_date', 'created_time')
    search_fields = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                     'location_code', 'location_name')


@admin.register(U_Enter_Bookings_Details)
class U_Enter_Bookings_DetailsAdmin(admin.ModelAdmin):
    list_display = ('location_booking', 'start_date', 'start_time', 'end_date', 'end_time', 'special_requests', 'status')
    search_fields = ('location_booking',)


@admin.register(Impact_Coworking_Bookings)
class Impact_Coworking_BookingsAdmin(admin.ModelAdmin):
    list_display = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                    'location_code', 'location_name', 'created_date', 'created_time')
    search_fields = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                     'location_code', 'location_name')


@admin.register(Impact_Coworking_Bookings_Details)
class Impact_Coworking_Bookings_DetailsAdmin(admin.ModelAdmin):
    list_display = ('location_booking', 'start_date', 'start_time', 'end_date', 'end_time', 'special_requests', 'status')
    search_fields = ('location_booking',)


@admin.register(Impulse_Coworking_Bookings)
class Impulse_Coworking_BookingsAdmin(admin.ModelAdmin):
    list_display = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                    'location_code', 'location_name', 'created_date', 'created_time')
    search_fields = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                     'location_code', 'location_name')


@admin.register(Impulse_Coworking_Bookings_Details)
class Impulse_Coworking_Bookings_DetailsAdmin(admin.ModelAdmin):
    list_display = ('location_booking', 'start_date', 'start_time', 'end_date', 'end_time', 'special_requests', 'status')
    search_fields = ('location_booking',)


@admin.register(Hub_Coworking_Bookings)
class Hub_Coworking_BookingsAdmin(admin.ModelAdmin):
    list_display = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                    'location_code', 'location_name', 'created_date', 'created_time')
    search_fields = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                     'location_code', 'location_name')


@admin.register(Hub_Coworking_Bookings_Details)
class Hub_Coworking_Bookings_DetailsAdmin(admin.ModelAdmin):
    list_display = ('location_booking', 'start_date', 'start_time', 'end_date', 'end_time', 'special_requests', 'status')
    search_fields = ('location_booking',)


@admin.register(Wiut_Bookings)
class Wiut_BookingsAdmin(admin.ModelAdmin):
    list_display = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                    'location_code', 'location_name', 'created_date', 'created_time')
    search_fields = ('user_first_name', 'user_last_name', 'user_email', 'user_phone_number', 'booking_id',
                     'location_code', 'location_name')


@admin.register(Wiut_Bookings_Details)
class Wiut_BookingsAdmin(admin.ModelAdmin):
    list_display = ('location_booking', 'start_date', 'start_time', 'end_date', 'end_time', 'special_requests', 'status')
    search_fields = ('location_booking',)