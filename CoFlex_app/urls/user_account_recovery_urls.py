from django.urls import path
from ..views.user_account_recovery_views import (restore_account,
                                                 verify_user_account_recovery_code,
                                                 verify_user_account_recovery_code_resend_code)

urlpatterns = [
    path('restore/', restore_account, name='restore_account'),
    path('restore/code/<int:user_id>/', verify_user_account_recovery_code, name='verify_user_account_recovery_code'),
    path('restore/code/<int:user_id>/resend_code/', verify_user_account_recovery_code_resend_code,
         name='verify_user_account_recovery_code_resend_code')
]
