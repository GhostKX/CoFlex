from django.urls import path
from ..views.user_dashboard_views import (user_home,
                                          user_card_details_verification_code_validation,
                                          user_card_details_sending_verification_code,
                                          user_card_cancel_verification)
from ..views.user_stop_subscription_views import user_stop_subscription, user_resume_subscription

urlpatterns = [
    path('user_home/<int:user_id>/', user_home, name='user_home'),
    path('user_home/<int:user_id>/card_details/<str:subscription_plan>/subscription/',
         user_card_details_verification_code_validation, name='user_card_details_verification_code_validation'),
    path('user_home/<int:user_id>/card_details/subscription/verification_code/', user_card_details_sending_verification_code, name='user_card_details_sending_verification_code'),
    path('user_home/<int:user_id>/card_details/subscription/verification_code/cancel/', user_card_cancel_verification,
         name='user_card_cancel_verification'),

    path('user_home/<int:user_id>/stop_subscription/', user_stop_subscription, name='user_stop_subscription'),
    path('user_home/<int:user_id>/resume_subscription/', user_resume_subscription, name='user_resume_subscription')

]
