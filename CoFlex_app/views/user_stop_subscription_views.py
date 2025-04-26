from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import now, localtime, localdate
from datetime import timedelta
from ..models import (VerifiedUsers, SubscribedUsers, SubscribedUsersStopped,
                      SubscribedUsersSubscriptionHistory, SubscribedUsersSubscriptionHistoryDetails,
                      SubscribedUsersSubscriptionHistoryPaymentDetails, SubscribedUsersSubscriptionHistoryStopped)
from ..forms.user_stop_subscription_form import UserStopSubscriptionForm
from .user_recent_actions_views import user_device_activity
from math import ceil


@login_required
def user_stop_subscription(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    subscribed_user = get_object_or_404(SubscribedUsers, user=user)
    subscribed_user_stopped = get_object_or_404(SubscribedUsersStopped, subscribed_user=subscribed_user)
    stopped_duration = subscribed_user_stopped.stopped_duration
    stopped_days_left = subscribed_user_stopped.subscription_stopped_days_left

    if request.method == 'POST':
        form = UserStopSubscriptionForm(request.POST, user=user)
        if form.is_valid():

            if subscribed_user_stopped.remaining_stop_attempts == 0:
                messages.error(request, f'You have reached the limit for stopping your subscription.\n'
                                        f'You can no longer stop it at this time. If you need assistance, please contact support.')
                return redirect('user_home', user_id=user.id)

            if subscribed_user_stopped.subscription_stopped_days_left == 0:
                messages.error(request, f'You have no stop days remaining\n'
                                        f'You can no longer stop it at this time. If you need assistance, please contact support.')
                return redirect('user_home', user_id=user.id)

            subscribed_user.is_active = False
            subscribed_user.save()

            subscribed_user.subscribed_users_details.subscription_status = 'stopped'
            subscribed_user.subscribed_users_details.save()

            subscribed_user_stopped.remaining_stop_attempts -= 1
            subscribed_user_stopped.subscription_stopped_at = localtime()
            subscribed_user_stopped.subscription_stopped_from_date = localdate()
            subscribed_user_stopped.subscription_stopped_till_date = localdate() + timedelta(days=stopped_days_left)
            subscribed_user_stopped.save()

            user_device_activity(instance=user, request=request, activity_type='Stopped Subscription',
                                 activity_details={})

            messages.success(request, 'Your subscription has been successfully stopped!')

            return redirect('user_home', user_id=user.id)

    else:
        form = UserStopSubscriptionForm(user=user)

    return render(request, 'user_dashboard/user_stop_subscription.html', {'form': form,
                                                                          'user': user,
                                                                          'stopped_duration': stopped_duration,
                                                                          'stopped_days_left': stopped_days_left})


@login_required
def user_resume_subscription(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(VerifiedUsers, id=user_id)
        subscribed_user = get_object_or_404(SubscribedUsers, user=user)
        subscribed_user_stopped = get_object_or_404(SubscribedUsersStopped, subscribed_user=subscribed_user)

        if not subscribed_user_stopped.subscription_stopped_at:
            messages.error(request, 'No active stop period found.')
            return redirect('user_home', user_id=user.id)

        time_now = localtime()
        stopped_at_time = subscribed_user_stopped.subscription_stopped_at
        days_stopped = ceil((time_now - stopped_at_time).total_seconds() / (60 * 60 * 24))

        subscribed_user_stopped.subscription_resumed_at = time_now
        subscribed_user_stopped.subscription_stopped_days_left -= int(days_stopped)
        subscribed_user_stopped.save()

        subscribed_user.is_active = True
        subscribed_user.subscription_expiry_date += timedelta(days=days_stopped)
        subscribed_user.save()

        subscribed_user.subscribed_users_details.subscription_status = 'active'
        subscribed_user.subscribed_users_details.subscription_till_date += timedelta(days=days_stopped)
        subscribed_user.subscribed_users_details.save()

        user_device_activity(instance=user, request=request, activity_type='Resumed Subscription', activity_details={})

        messages.success(request, 'Your subscription has been successfully resumed!')

    return redirect('user_home', user_id=user_id)


@login_required
def user_cancel_subscription(request, user_id):
    user = get_object_or_404(VerifiedUsers, id=user_id)
    subscribed_user = get_object_or_404(SubscribedUsers, user=user)
    subscribed_users_details = subscribed_user.subscribed_users_details
    subscribed_users_payment_details = subscribed_user.subscribed_users_payment_details
    subscribed_users_stopped = subscribed_user.subscribed_users_stopped

    if request.method == "POST":
        form = UserStopSubscriptionForm(request.POST, user=user)
        if form.is_valid():

            subscribed_user.is_subscribed = False
            subscribed_user.is_active = False
            subscribed_user.save()

            subscribed_users_details.subscription_status = 'subscription_canceled'
            subscribed_users_details.save()

    else:
        form = UserStopSubscriptionForm(user=user)


