from django.urls import path
from ..views.user_recent_actions_views import user_recent_actions_history, user_action_details

urlpatterns = [
    path('recent_actions/<int:user_id>/', user_recent_actions_history, name='user_recent_actions_history'),
    path('recent_actions/<int:user_id>/<str:session_key>/<str:action_type>/action_details/', user_action_details, name='user_action_details'),
]