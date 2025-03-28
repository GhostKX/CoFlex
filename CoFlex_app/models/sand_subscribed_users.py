from datetime import timedelta
from django.db import models
from django.utils.timezone import now
from .verified_user_profile_details import VerifiedUsers


# Sand Subscribed Users table for storing user data
# that could not purchase the subscription successfully
class SandSubscribedUsers(models.Model):
    user = models.ForeignKey(VerifiedUsers, on_delete=models.CASCADE, related_name='sand_subscribed_users')
    subscription_datetime = models.DateTimeField(null=True, blank=True)
    subscription_expiry = models.DateTimeField(null=True, blank=True)

    is_subscribed = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Sand Subscribed User'
        verbose_name_plural = 'Sand Subscribed Users'

    def __str__(self):
        return self.user.email


# Sand Subscribed Users table for storing verification code
class SandSubscribedUsersVerificationCode(models.Model):
    user = models.OneToOneField(SandSubscribedUsers, on_delete=models.CASCADE,
                                related_name='sand_subscribed_users_verification_code')
    verification_code = models.CharField(max_length=100, null=True, blank=True)
    is_code_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = 'Sand Subscribed User Verification Code'
        verbose_name_plural = 'Sand Subscribed Users Verification Codes'

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = now() + timedelta(minutes=1)
        super().save(*args, **kwargs)

    def is_expired(self):
        return self.expires_at < now()

    def __str__(self):
        return f'Sand Verification code for {self.user.user.email}'


# Sand Subscribed Users Details table
class SandSubscribedUsersDetails(models.Model):
    user = models.OneToOneField(SandSubscribedUsers, on_delete=models.CASCADE, related_name='sand_subscribed_users_details')
    type_of_subscription = models.CharField(max_length=50, choices=[
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
    duration = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Sand Subscribed User Details'
        verbose_name_plural = 'Sand Subscribed Users Details'

    def __str__(self):
        return f'Sand Subscribed user details of {self.user.user.email}'


# Sand Subscribed Users Payment Details table
class SandSubscribedUsersPaymentDetails(models.Model):
    user = models.OneToOneField(SandSubscribedUsers, on_delete=models.CASCADE,
                                related_name='sand_subscribed_users_payment_details')
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
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending',
    )

    class Meta:
        verbose_name = 'Sand Subscribed User Payment Details'
        verbose_name_plural = 'Sand Subscribed Users Payment Details'

        def __str__(self):
            return f'Sand Subscribed user payment details of {self.user.user.email}'


# Sand Subscribed Users Card Details table
class SandSubscribedUserCardDetails(models.Model):
    user = models.OneToOneField(SandSubscribedUsers, on_delete=models.CASCADE, related_name='sand_subscribed_users_card_details')
    card_number = models.CharField(null=True, blank=True, max_length=250)
    expiry_date = models.CharField(null=True, blank=True, max_length=250)
    cvv = models.CharField(null=True, blank=True, max_length=250)
    card_holder_name = models.CharField(null=True, blank=True, max_length=250)
    added_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Sand Subscribed User Card Details'
        verbose_name_plural = 'Sand Subscribed Users Card Details'

    def __str__(self):
        return f'Sand Subscribed user Card details of {self.user.user.email}'


# Sand Subscribed Users Card Details Last Four Digits table
class SandSubscribedUserCardDetailsLastFourDigits(models.Model):
    user = models.OneToOneField(SandSubscribedUsers, on_delete=models.CASCADE,
                                related_name='sand_subscribed_users_card_details_last_four_digits')
    last_four_digits = models.CharField(null=True, blank=True, max_length=100)
    added_date = models.DateField(null=True, blank=True)
    added_time = models.TimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Sand Subscribed User Card Details Last Four Digits'
        verbose_name_plural = 'Sand Subscribed Users Card Details Last Four Digits'

    def __str__(self):
        return f'Sand Subscribed user Card details of {self.user.user.email}'


# Subscribed Users table
class SubscribedUsers(models.Model):
    user = models.OneToOneField(VerifiedUsers, on_delete=models.CASCADE, related_name='subscribed_users')
    subscription_datetime = models.DateTimeField(null=True, blank=True)
    subscription_expiry = models.DateTimeField(null=True, blank=True)

    is_subscribed = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Subscribed User'
        verbose_name_plural = 'Subscribed Users'

    def __str__(self):
        return self.user.email


# Subscribed Users Details table
class SubscribedUsersDetails(models.Model):
    user = models.OneToOneField(SubscribedUsers, on_delete=models.CASCADE, related_name='subscribed_users_details')
    type_of_subscription = models.CharField(max_length=50, choices=[
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
    duration = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Subscribed User Details'
        verbose_name_plural = 'Subscribed Users Details'

    def __str__(self):
        return f'Subscribed user details of {self.user.user.email}'


# Subscribed Users Payment Details table
class SubscribedUsersPaymentDetails(models.Model):
    user = models.OneToOneField(SubscribedUsers, on_delete=models.CASCADE, related_name='subscribed_users_payment_details')
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
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending',
    )

    class Meta:
        verbose_name = 'Subscribed User Payment Details'
        verbose_name_plural = 'Subscribed Users Payment Details'

        def __str__(self):
            return f'Subscribed user payment details of {self.user.user.email}'


# Subscribed Users Card Details table
class SubscribedUserCardDetails(models.Model):
    user = models.OneToOneField(SubscribedUsers, on_delete=models.CASCADE, related_name='subscribed_users_card_details')
    card_number = models.CharField(null=True, blank=True, max_length=420)
    expiry_date = models.CharField(null=True, blank=True, max_length=420)
    cvv = models.CharField(null=True, blank=True, max_length=420)
    card_holder_name = models.CharField(null=True, blank=True, max_length=420)
    added_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Subscribed User Card Details'
        verbose_name_plural = 'Subscribed Users Card Details'

    def __str__(self):
        return f'Subscribed user Card details of {self.user.user.email}'


# Subscribed Users Last Four Digits table
class SubscribedUserCardDetailsLastFourDigits(models.Model):
    user = models.OneToOneField(SubscribedUsers, on_delete=models.CASCADE, related_name='subscribed_users_card_details_last_four_digits')
    last_four_digits = models.CharField(null=True, blank=True, max_length=100)
    added_date = models.DateField(null=True, blank=True)
    added_time = models.TimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Subscribed User Card Details Last Four Digits'
        verbose_name_plural = 'Subscribed Users Card Details Last Four Digits'

    def __str__(self):
        return f'Subscribed user Card details of {self.user.user.email}'


# Subscribed Users Subscription History table
class SubscribedUsersSubscriptionHistory(models.Model):
    user = models.ForeignKey(SubscribedUsers, on_delete=models.CASCADE, related_name='subscribed_users_subscription_history')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    subscription_type = models.CharField(max_length=50, null=True, blank=True)
    subscription_status = models.CharField(max_length=50, choices=[
        ('not_subscribed', 'Not Subscribed'),
        ('subscribed', 'Subscribed'),
        ('updated', 'Updated'),
        ('canceled', 'Canceled')
    ], null=True, blank=True, default='not_subscribed')

    class Meta:
        verbose_name = 'Subscribed User History'
        verbose_name_plural = 'Subscribed Users History'

    def __str__(self):
        return f'Subscribed user history of {self.user.user.email}'