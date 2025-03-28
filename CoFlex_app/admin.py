from django.contrib import admin
from .models import (UnverifiedUsers, UnverifiedUsersVerificationCode,
                     VerifiedUsers, Profile, UserDetails,
                     UserExtraDetails, UserExtraContactDetails, UserPhotoDetails,
                     VerifiedUsersPasswordVerificationCode,
                     SecondEmailVerificationCode,
                     UserEditMainEmail, UserAccountDeletion, UserAccountRestoration, UserAccountRecoveryCode,
                     DeletedAccountsMainInfo, DeletedAccountsProfile,
                     DeletedAccountsDetails, DeletedAccountsExtraDetails,
                     DeletedAccountsPhoto, DeletedAccountsSpecifics,
                     SandSubscribedUsers, SandSubscribedUsersVerificationCode, SandSubscribedUsersDetails,
                     SandSubscribedUsersPaymentDetails, SandSubscribedUserCardDetails,
                     SandSubscribedUserCardDetailsLastFourDigits,
                     SubscribedUsers, SubscribedUsersDetails,
                     SubscribedUsersPaymentDetails, SubscribedUserCardDetails,
                     SubscribedUserCardDetailsLastFourDigits, SubscribedUsersSubscriptionHistory,
                     Locations, LocationDetails, LocationAvailability,
                     Booking, BookingDetails,
                     UserSignUpLoginLogoutActivity, UserDeviceActivities)


@admin.register(UnverifiedUsers)
class UnverifiedUsersAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'registered_datetime', 'last_login')
    search_fields = ('first_name', 'last_name', 'email')


@admin.register(UnverifiedUsersVerificationCode)
class UnverifiedUsersVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'verification_code', 'is_code_used', 'expires_at')
    search_fields = ('user__email',)


@admin.register(VerifiedUsers)
class VerifiedUsersAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'registered_datetime', 'is_active', 'last_login')
    search_fields = ('first_name', 'last_name', 'email')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Exclude admin (superuser)
        return queryset.exclude(is_superuser=True)

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


@admin.register(Profile)
class VerifiedUsersProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'username', 'phone_number', 'address')
    search_fields = ('user__email', 'username', 'phone_number')


@admin.register(UserDetails)
class VerifiedUsersDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'is_email_verified', 'is_subscribed',)
    search_fields = ('user__email',)

    list_filter = ('is_subscribed',)


@admin.register(UserExtraDetails)
class UserExtraDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'dob', 'gender', 'age', 'website')
    search_fields = ('user__email',)
    list_filter = ('gender',)


@admin.register(UserExtraContactDetails)
class UserExtraContactDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'second_email', 'second_phone_number', 'second_address')
    search_fields = ('user__email', 'second_email', 'second_phone_number')


@admin.register(UserPhotoDetails)
class UserPhotoDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_photo', 'photo_path', 'uploaded_time')
    search_fields = ('user__email',)


@admin.register(VerifiedUsersPasswordVerificationCode)
class VerifiedUsersPasswordVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'verification_code', 'is_code_used', 'expires_at')
    search_fields = ('user',)


@admin.register(SecondEmailVerificationCode)
class SecondEmailVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'second_email', 'verification_code', 'is_code_used', 'expires_at')
    search_fields = ('user__email', 'second_email')


@admin.register(UserEditMainEmail)
class SecondEmailVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'new_email', 'verification_code', 'is_code_used', 'expires_at')
    search_fields = ('user__email', 'new_email')


@admin.register(UserAccountDeletion)
class UserAccountDeletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_deleted', 'deletion_time', 'deletion_details', 'deletion_attempts', 'is_blocked')
    search_fields = ('user__email',)


@admin.register(DeletedAccountsMainInfo)
class DeletedAccountsMainInfoAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'registered_datetime', 'last_login', 'is_subscribed')
    search_fields = ('first_name', 'last_name', 'email')


@admin.register(DeletedAccountsProfile)
class DeletedAccountsProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'username', 'phone_number', 'address')
    search_fields = ('user__email', 'username', 'phone_number')


@admin.register(DeletedAccountsDetails)
class DeletedAccountsDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'dob', 'gender', 'age', 'website')
    search_fields = ('user__email',)
    list_filter = ('gender',)


@admin.register(DeletedAccountsExtraDetails)
class DeletedAccountsExtraDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'second_email', 'second_phone_number', 'second_address')
    search_fields = ('user__email', 'second_email', 'second_phone_number')


@admin.register(DeletedAccountsPhoto)
class UserPhotoDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_photo', 'photo_path', 'uploaded_time')
    search_fields = ('user__email',)


@admin.register(DeletedAccountsSpecifics)
class UserAccountDeletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_deleted', 'deletion_time', 'deletion_details', 'deletion_attempts', 'is_blocked')
    search_fields = ('user__email',)


@admin.register(UserAccountRestoration)
class UserAccountRestorationAdmin(admin.ModelAdmin):
    list_display = ('user', 'restoration_email', 'restoration_details', 'restoration_time')
    search_fields = ('user', 'restoration_email',)


@admin.register(UserAccountRecoveryCode)
class UserAccountRecoveryCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'verification_code', 'is_code_used', 'expires_at')
    search_fields = ('user',)


@admin.register(SandSubscribedUsers)
class SandSubscribedUsersAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_datetime', 'subscription_expiry', 'is_subscribed', 'is_active')
    search_fields = ('user_email',)


@admin.register(SandSubscribedUsersVerificationCode)
class SandSubscribedUsersVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'verification_code', 'is_code_used', 'expires_at')
    search_fields = ('user',)


@admin.register(SandSubscribedUsersDetails)
class SandSubscribedUserDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'type_of_subscription', 'duration')
    search_fields = ('user_email', 'type_of_subscription', 'duration')


@admin.register(SandSubscribedUsersPaymentDetails)
class SandSubscribedUsersPaymentDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'charged_amount', 'charged_date', 'charged_time', 'is_charged', 'payment_method', 'payment_status')
    search_fields = ('user__email',)


@admin.register(SandSubscribedUserCardDetails)
class SandSubscribedUserCardDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_number', 'expiry_date', 'cvv', 'card_holder_name', 'added_time')
    search_fields = ('user__email',)


@admin.register(SandSubscribedUserCardDetailsLastFourDigits)
class SandSubscribedUserCardDetailsLastFourDigitsAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_four_digits', 'added_date', 'added_time')
    search_fields = ('user__email',)


@admin.register(SubscribedUsers)
class SubscribedUsersAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_datetime', 'subscription_expiry', 'is_subscribed', 'is_active')
    search_fields = ('user_email',)


@admin.register(SubscribedUsersDetails)
class SubscribedUserDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'type_of_subscription', 'duration')
    search_fields = ('user_email', 'type_of_subscription', 'duration')


@admin.register(SubscribedUsersPaymentDetails)
class SubscribedUsersPaymentDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'charged_amount', 'charged_date', 'charged_time', 'is_charged', 'payment_method', 'payment_status')
    search_fields = ('user__email',)


@admin.register(SubscribedUserCardDetails)
class SubscribedUserCardDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_number', 'expiry_date', 'cvv', 'card_holder_name', 'added_time')
    search_fields = ('user__email',)


@admin.register(SubscribedUserCardDetailsLastFourDigits)
class SubscribedUserCardDetailsLastFourDigitsAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_four_digits', 'added_date', 'added_time')
    search_fields = ('user__email',)


@admin.register(SubscribedUsersSubscriptionHistory)
class SubscribedUsersSubscriptionHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'subscription_type', 'subscription_status')
    search_fields = ('user__email',)


@admin.register(Locations)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('location_name', 'location_code', 'location_longitude', 'location_latitude', 'icon_path')
    search_fields = ('location_name', 'location_code')


@admin.register(LocationDetails)
class LocationDetailsAdmin(admin.ModelAdmin):
    list_display = ('location', 'address', 'contact_phone', 'working_hours', 'image_path', 'website', 'default_availability')
    search_fields = ('location', 'address', 'contact_phone', 'website')


@admin.register(LocationAvailability)
class LocationDetailsAdmin(admin.ModelAdmin):
    list_display = ('location', 'date', 'availability')
    search_fields = ('location', 'date')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'booking_id', 'created_date', 'created_time')
    search_fields = ('user', 'location', 'booking_id')


@admin.register(BookingDetails)
class BookingDetailsAdmin(admin.ModelAdmin):
    list_display = ('booking', 'start_date', 'start_time', 'end_date', 'end_time', 'special_requests', 'status')
    search_fields = ('booking', 'start_date', 'status')


@admin.register(UserSignUpLoginLogoutActivity)
class UserSignUpLoginLogoutActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'ip_address', 'device_type', 'browser', 'operating_system', 'city', 'country', 'date_time', 'is_Logged_in', 'action')
    search_fields = ('user__email', 'session_key', 'ip_address', 'browser', 'city', 'country')
    list_filter = ('action', 'is_Logged_in', 'date_time', 'country')
    ordering = ('-date_time',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Exclude the superuser's own data
        if request.user.is_superuser:
            queryset = queryset.exclude(user=request.user)  # Exclude the superuser's data
        return queryset


@admin.register(UserDeviceActivities)
class UserDeviceActivitiesAdmin(admin.ModelAdmin):
    list_display = ('user_session', 'activity_type', 'activity_details', 'date_time')
    search_fields = ('user_session__user__email', 'activity_type')
    list_filter = ('activity_type', 'date_time')
    ordering = ('-date_time',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Exclude the superuser's own data
        if request.user.is_superuser:
            queryset = queryset.exclude(user_session__user=request.user)  # Exclude the superuser's data
        return queryset


