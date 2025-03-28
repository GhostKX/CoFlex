from django.urls import path
from ..views.user_dashboard_views import (user_home,
                                          user_card_details,
                                          user_card_details_verification_code,
                                          user_card_details_verification_code_resend_code,
                                          user_card_cancel_verification)

urlpatterns = [
    path('user_home/<int:user_id>/', user_home, name='user_home'),
    path('user_home/<int:user_id>/card_details/<str:subscription_type>/subscription/', user_card_details, name='user_card_details'),
    path('user_home/<int:user_id>/card_details/subscription/verification_code/', user_card_details_verification_code, name='user_card_details_verification_code'),
    path('user_home/<int:user_id>/card_details/subscription/verification_code/resend_code/', user_card_details_verification_code_resend_code, name='user_card_details_verification_code_resend_code'),
    path('user_home/<int:user_id>/card_details/subscription/verification_code/cancel/', user_card_cancel_verification, name='user_card_cancel_verification'),
]
