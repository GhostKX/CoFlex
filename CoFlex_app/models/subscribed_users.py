from datetime import timedelta
from django.db import models
from django.utils.timezone import now
from .verified_user_profile_details import VerifiedUsers


# Subscribed Users table for storing verification code
class SubscribedUsersVerificationCode(models.Model):
    user = models.OneToOneField(VerifiedUsers, on_delete=models.CASCADE,
                                related_name='subscribed_users_verification_code')
    verification_code = models.CharField(max_length=100, null=True, blank=True)
    is_code_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = 'Subscribed User Verification Code'
        verbose_name_plural = 'Subscribed Users Verification Codes'

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = now() + timedelta(minutes=1)
        super().save(*args, **kwargs)

    def is_expired(self):
        return self.expires_at < now()

    def __str__(self):
        return f'Verification code for {self.subscribed_user.user.email}'


# Subscribed Users table
class SubscribedUsers(models.Model):
    user = models.OneToOneField(VerifiedUsers, on_delete=models.CASCADE, related_name='subscribed_users')
    subscription_unique_id = models.CharField(unique=True, null=False, blank=False, max_length=50)

    subscription_datetime = models.DateTimeField(null=False, blank=False)
    subscription_expiry_date = models.DateField(null=True, blank=True)

    is_subscribed = models.BooleanField(null=False, blank=False, default=True)
    is_active = models.BooleanField(null=False, blank=False, default=True)

    class Meta:
        verbose_name = 'Subscribed User'
        verbose_name_plural = 'Subscribed Users'

    def __str__(self):
        return self.user.email


# Subscribed Users Details table
class SubscribedUsersDetails(models.Model):
    subscribed_user = models.OneToOneField(SubscribedUsers, on_delete=models.CASCADE,
                                           related_name='subscribed_users_details')
    subscription_type = models.CharField(max_length=50, choices=[
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semiannually', 'Semiannually')
    ])
    subscription_plan = models.CharField(max_length=50, choices=[
        ('basic_month', 'Basic - Monthly'),
        ('standard_month', 'Standard - Monthly'),
        ('vip_month', 'VIP - Monthly'),
        ('basic_quarter', 'Basic - Quarterly'),
        ('standard_quarter', 'Standard - Quarterly'),
        ('vip_quarter', 'VIP - Quarterly'),
        ('basic_semiannual', 'Basic - Semi-Annual'),
        ('standard_semiannual', 'Standard - Semi-Annual'),
        ('vip_semiannual', 'VIP - Semi-Annual'),
    ], null=True, blank=True)

    subscription_duration = models.IntegerField(null=True, blank=True)
    days_left = models.IntegerField(null=True, blank=True)
    subscription_from_date = models.DateField(null=True, blank=True)
    subscription_till_date = models.DateField(null=True, blank=True)
    subscription_status = models.CharField(max_length=50, choices=[
        ('active', 'Active'),
        ('stopped', 'Stopped'),
        ('subscription_canceled', 'Subscription Canceled')
    ], default='active')

    class Meta:
        verbose_name = 'Subscribed User Details'
        verbose_name_plural = 'Subscribed Users Details'

    def __str__(self):
        return f'Subscribed user details of {self.subscribed_user.user.email}'


# Subscribed Users Payment Details table
class SubscribedUsersPaymentDetails(models.Model):
    subscribed_user = models.OneToOneField(SubscribedUsers, on_delete=models.CASCADE,
                                           related_name='subscribed_users_payment_details')
    charged_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    charged_date = models.DateField(blank=True, null=True)
    charged_time = models.TimeField(blank=True, null=True)
    is_charged = models.BooleanField(blank=True, null=True, default=False)
    payment_method = models.CharField(max_length=50, choices=[
        ('credit_card', 'Credit Card'),
        ('payme', 'PayMe'),
        ('click', 'Click')
    ], null=True, blank=True)
    payment_status = models.CharField(
        max_length=50, choices=[
            ('pending', 'Pending'),
            ('successful', 'Successful'),
            ('failed', 'Failed'),
        ],
        default='pending',
    )

    class Meta:
        verbose_name = 'Subscribed User Payment Details'
        verbose_name_plural = 'Subscribed Users Payment Details'

    def __str__(self):
        return f'Subscribed user payment details of {self.subscribed_user.user.email}'


# Subscribed Users Card Details table
class SubscribedUserCardDetails(models.Model):
    subscribed_user = models.OneToOneField(SubscribedUsers, on_delete=models.CASCADE,
                                           related_name='subscribed_users_card_details')
    card_number = models.CharField(null=True, blank=True, max_length=600)
    expiry_date = models.CharField(null=True, blank=True, max_length=600)
    cvv = models.CharField(null=True, blank=True, max_length=600)
    card_holder_name = models.CharField(null=True, blank=True, max_length=600)
    added_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Subscribed User Card Details'
        verbose_name_plural = 'Subscribed Users Card Details'

    def __str__(self):
        return f'Subscribed user Card details of {self.subscribed_user.user.email}'


# Subscribed Users Last Four Digits table
class SubscribedUserCardDetailsLastFourDigits(models.Model):
    subscribed_user = models.OneToOneField(SubscribedUsers, on_delete=models.CASCADE,
                                           related_name='subscribed_users_card_details_last_four_digits')
    last_four_digits = models.CharField(null=True, blank=True, max_length=100)
    added_date = models.DateField(null=True, blank=True)
    added_time = models.TimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Subscribed User Card Details Last Four Digits'
        verbose_name_plural = 'Subscribed Users Card Details Last Four Digits'

    def __str__(self):
        return f'Subscribed user Card details of {self.subscribed_user.user.email}'


# Subscribed Users Stopped table
class SubscribedUsersStopped(models.Model):
    subscribed_user = models.OneToOneField(SubscribedUsers, on_delete=models.CASCADE,
                                           related_name='subscribed_users_stopped')

    stopped_duration = models.IntegerField(null=True, blank=True)
    subscription_stopped_days_left = models.IntegerField(null=True, blank=True)
    remaining_stop_attempts = models.IntegerField(null=True, blank=True)

    subscription_stopped_from_date = models.DateField(null=True, blank=True)
    subscription_stopped_till_date = models.DateField(null=True, blank=True)

    subscription_stopped_at = models.DateTimeField(null=True, blank=True)
    subscription_resumed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Subscribed User Stopped'
        verbose_name_plural = 'Subscribed Users Stopped'

    def __str__(self):
        return f'Subscribed user stopped of {self.subscribed_user.user.email}'


# Subscribed Users Subscription History table
class SubscribedUsersSubscriptionHistory(models.Model):
    user = models.ForeignKey(VerifiedUsers, on_delete=models.CASCADE,
                             related_name='subscribed_users_subscription_history')
    subscription_unique_id = models.CharField(unique=True, null=False, blank=False, max_length=50)

    subscription_datetime = models.DateTimeField(null=False, blank=False)
    subscription_expiry_date = models.DateField(null=True, blank=True)

    is_subscribed = models.BooleanField(null=False, blank=False, default=False)
    is_active = models.BooleanField(null=False, blank=False, default=False)

    class Meta:
        verbose_name = 'Subscribed User Subscription History'
        verbose_name_plural = 'Subscribed Users Subscription History'

    def __str__(self):
        return self.user.email


class SubscribedUsersSubscriptionHistoryDetails(models.Model):
    subscribed_user_history = models.OneToOneField(SubscribedUsersSubscriptionHistory, on_delete=models.CASCADE,
                                                   related_name='subscribed_users_subscription_history_details')
    subscription_type = models.CharField(max_length=50, choices=[
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semiannually', 'Semiannually')
    ])
    subscription_plan = models.CharField(max_length=50, choices=[
        ('basic_month', 'Basic - Monthly'),
        ('standard_month', 'Standard - Monthly'),
        ('vip_month', 'VIP - Monthly'),
        ('basic_quarter', 'Basic - Quarterly'),
        ('standard_quarter', 'Standard - Quarterly'),
        ('vip_quarter', 'VIP - Quarterly'),
        ('basic_semiannual', 'Basic - Semi-Annual'),
        ('standard_semiannual', 'Standard - Semi-Annual'),
        ('vip_semiannual', 'VIP - Semi-Annual'),
    ], null=True, blank=True)

    subscription_duration = models.IntegerField(null=True, blank=True)
    days_left = models.IntegerField(null=True, blank=True)
    subscription_from_date = models.DateField(null=True, blank=True)
    subscription_till_date = models.DateField(null=True, blank=True)
    subscription_status = models.CharField(max_length=50, choices=[
        ('active', 'Active'),
        ('stopped', 'Stopped'),
        ('subscription_canceled', 'Subscription Canceled')
    ], default='active')

    class Meta:
        verbose_name = 'Subscribed User Subscription History Details'
        verbose_name_plural = 'Subscribed Users Subscription History Details'

    def __str__(self):
        return f'Subscribed user subscription history details of {self.subscribed_user_history.user.email}'


class SubscribedUsersSubscriptionHistoryPaymentDetails(models.Model):
    subscribed_user_history = models.OneToOneField(SubscribedUsersSubscriptionHistory, on_delete=models.CASCADE,
                                                   related_name='subscribed_users_subscription_history_payment_details')
    charged_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    charged_date = models.DateField(blank=True, null=True)
    charged_time = models.TimeField(blank=True, null=True)
    is_charged = models.BooleanField(blank=True, null=True, default=False)
    payment_method = models.CharField(max_length=50, choices=[
        ('credit_card', 'Credit Card'),
        ('payme', 'PayMe'),
        ('click', 'Click')
    ], null=True, blank=True)
    payment_status = models.CharField(
        max_length=50, choices=[
            ('pending', 'Pending'),
            ('successful', 'Successful'),
            ('failed', 'Failed'),
        ],
        default='pending',
    )

    class Meta:
        verbose_name = 'Subscribed User Subscription History Payment Details'
        verbose_name_plural = 'Subscribed Users Subscription History Payment Details'

    def __str__(self):
        return f'Subscribed user subscription history payment details of {self.subscribed_user_history.user.email}'


class SubscribedUsersSubscriptionHistoryStopped(models.Model):
    subscribed_user_history = models.OneToOneField(SubscribedUsersSubscriptionHistory, on_delete=models.CASCADE,
                                                   related_name='subscribed_users_subscription_history_stopped')

    stopped_duration = models.IntegerField(null=True, blank=True)
    subscription_stopped_days_left = models.IntegerField(null=True, blank=True)
    remaining_stop_attempts = models.IntegerField(null=True, blank=True)

    subscription_stopped_from_date = models.DateField(null=True, blank=True)
    subscription_stopped_till_date = models.DateField(null=True, blank=True)

    subscription_stopped_at = models.DateTimeField(null=True, blank=True)
    subscription_resumed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Subscribed User Subscription History Stopped'
        verbose_name_plural = 'Subscribed Users Subscription History Stopped'

    def __str__(self):
        return f'Subscribed user subscription history stopped of {self.subscribed_user_history.user.email}'


# Subscribed Users Future tables
class SubscribedUsersFuture(models.Model):
    user = models.OneToOneField(VerifiedUsers, on_delete=models.CASCADE, related_name='subscribed_users_future')
    subscription_unique_id = models.CharField(unique=True, null=False, blank=False, max_length=50)

    subscription_datetime = models.DateTimeField(null=False, blank=False)
    subscription_expiry_date = models.DateField(null=True, blank=True)

    is_subscribed = models.BooleanField(null=False, blank=False, default=True)
    is_active = models.BooleanField(null=False, blank=False, default=True)

    class Meta:
        verbose_name = 'Subscribed User Future'
        verbose_name_plural = 'Subscribed Users Future'

    def __str__(self):
        return self.user.email


class SubscribedUsersFutureDetails(models.Model):
    subscribed_user_future = models.OneToOneField(SubscribedUsersFuture, on_delete=models.CASCADE,
                                                  related_name='subscribed_users_future_details')
    subscription_type = models.CharField(max_length=50, choices=[
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semiannually', 'Semiannually')
    ])
    subscription_plan = models.CharField(max_length=50, choices=[
        ('basic_month', 'Basic - Monthly'),
        ('standard_month', 'Standard - Monthly'),
        ('vip_month', 'VIP - Monthly'),
        ('basic_quarter', 'Basic - Quarterly'),
        ('standard_quarter', 'Standard - Quarterly'),
        ('vip_quarter', 'VIP - Quarterly'),
        ('basic_semiannual', 'Basic - Semi-Annual'),
        ('standard_semiannual', 'Standard - Semi-Annual'),
        ('vip_semiannual', 'VIP - Semi-Annual'),
    ], null=True, blank=True)

    subscription_duration = models.IntegerField(null=True, blank=True)
    days_left = models.IntegerField(null=True, blank=True)
    subscription_from_date = models.DateField(null=True, blank=True)
    subscription_till_date = models.DateField(null=True, blank=True)
    subscription_status = models.CharField(max_length=50, choices=[
        ('active', 'Active'),
        ('stopped', 'Stopped'),
        ('subscription_canceled', 'Subscription Canceled')
    ], default='active')

    class Meta:
        verbose_name = 'Subscribed User Future Details'
        verbose_name_plural = 'Subscribed Users Future Details'

    def __str__(self):
        return f'Subscribed user future details of {self.subscribed_user_future.user.email}'


class SubscribedUsersFuturePaymentDetails(models.Model):
    subscribed_user_future = models.OneToOneField(SubscribedUsersFuture, on_delete=models.CASCADE,
                                                  related_name='subscribed_users_future_payment_details')
    charged_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    charged_date = models.DateField(blank=True, null=True)
    charged_time = models.TimeField(blank=True, null=True)
    is_charged = models.BooleanField(blank=True, null=True, default=False)
    payment_method = models.CharField(max_length=50, choices=[
        ('credit_card', 'Credit Card'),
        ('payme', 'PayMe'),
        ('click', 'Click')
    ], null=True, blank=True)
    payment_status = models.CharField(
        max_length=50, choices=[
            ('pending', 'Pending'),
            ('successful', 'Successful'),
            ('failed', 'Failed'),
        ],
        default='pending',
    )

    class Meta:
        verbose_name = 'Subscribed User Future Payment Details'
        verbose_name_plural = 'Subscribed Users Future Payment Details'

    def __str__(self):
        return f'Subscribed user future payment details of {self.subscribed_user_future.user.email}'


class SubscribedUsersFutureCardDetails(models.Model):
    subscribed_user_future = models.OneToOneField(SubscribedUsersFuture, on_delete=models.CASCADE,
                                                  related_name='subscribed_users_future_card_details')
    card_number = models.CharField(null=True, blank=True, max_length=420)
    expiry_date = models.CharField(null=True, blank=True, max_length=420)
    cvv = models.CharField(null=True, blank=True, max_length=420)
    card_holder_name = models.CharField(null=True, blank=True, max_length=420)
    added_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Subscribed User Future Card Details'
        verbose_name_plural = 'Subscribed Users Future Card Details'

    def __str__(self):
        return f'Subscribed user Future Card details of {self.subscribed_user_future.user.email}'


class SubscribedUsersFutureCardDetailsLastFourDigits(models.Model):
    subscribed_user_future = models.OneToOneField(SubscribedUsersFuture, on_delete=models.CASCADE,
                                                  related_name='subscribed_users_future_card_details_last_four_digits')
    last_four_digits = models.CharField(null=True, blank=True, max_length=100)
    added_date = models.DateField(null=True, blank=True)
    added_time = models.TimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Subscribed User Future Card Details Last Four Digits'
        verbose_name_plural = 'Subscribed Users Future Card Details Last Four Digits'

    def __str__(self):
        return f'Subscribed user Future Card details of {self.subscribed_user_future.user.email}'


class SubscribedUsersFutureStopped(models.Model):
    subscribed_user_future = models.OneToOneField(SubscribedUsersFuture, on_delete=models.CASCADE,
                                                  related_name='subscribed_users_future_stopped')

    stopped_duration = models.IntegerField(null=True, blank=True)
    subscription_stopped_days_left = models.IntegerField(null=True, blank=True)
    remaining_stop_attempts = models.IntegerField(null=True, blank=True)

    subscription_stopped_from_date = models.DateField(null=True, blank=True)
    subscription_stopped_till_date = models.DateField(null=True, blank=True)

    subscription_stopped_at = models.DateTimeField(null=True, blank=True)
    subscription_resumed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Subscribed User Future Stopped'
        verbose_name_plural = 'Subscribed Users Future Stopped'

    def __str__(self):
        return f'Subscribed user future stopped of {self.subscribed_user_future.user.email}'
