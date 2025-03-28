from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from CoFlex_app.models import VerifiedUsers
from CoFlex_Staff_app.models import StaffAccounts


class CustomAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            # Checking if email exists in StaffAccounts
            user = StaffAccounts.objects.get(email=email)
            if user and check_password(password, user.password):
                return user
        except StaffAccounts.DoesNotExist:
            pass

        try:
            # Check if email exists in VerifiedUsers
            user = VerifiedUsers.objects.get(email=email)
            if user and check_password(password, user.password):
                return user
        except VerifiedUsers.DoesNotExist:
            pass

        return None

    def get_user(self, user_id):
        # Trying to get the user from StaffAccounts
        try:
            return StaffAccounts.objects.get(pk=user_id)
        except StaffAccounts.DoesNotExist:
            pass

        # Trying to get the user from VerifiedUsers
        try:
            return VerifiedUsers.objects.get(pk=user_id)
        except VerifiedUsers.DoesNotExist:
            pass

        # If no user is found, returning None
        return None
