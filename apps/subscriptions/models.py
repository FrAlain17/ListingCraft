from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta


class SubscriptionPlan(models.Model):
    """
    Subscription plans for ListingCraft.
    Corresponds to Stripe products/prices.
    """

    class PlanType(models.TextChoices):
        BASIC = 'BASIC', 'Basic'
        PRO = 'PRO', 'Pro'
        AGENCY = 'AGENCY', 'Agency'

    name = models.CharField(max_length=100, unique=True)
    plan_type = models.CharField(max_length=10, choices=PlanType.choices)
    stripe_price_id = models.CharField(max_length=100, blank=True, help_text='Stripe Price ID')
    stripe_product_id = models.CharField(max_length=100, blank=True, help_text='Stripe Product ID')

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Monthly price in USD')

    # Limits
    description_quota = models.IntegerField(
        help_text='Monthly description generation quota. -1 for unlimited'
    )

    # Features (stored as JSON for flexibility)
    features = models.JSONField(default=list, help_text='List of features for this plan')

    # Status
    is_active = models.BooleanField(default=True)

    # Metadata
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'
        ordering = ['price']

    def __str__(self):
        return f"{self.name} - ${self.price}/month"

    @property
    def is_unlimited(self):
        """Check if plan has unlimited descriptions."""
        return self.description_quota == -1


class UserSubscription(models.Model):
    """
    User's active subscription.
    Links users to their Stripe subscriptions.
    """

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        TRIALING = 'TRIALING', 'Trialing'
        PAST_DUE = 'PAST_DUE', 'Past Due'
        CANCELED = 'CANCELED', 'Canceled'
        UNPAID = 'UNPAID', 'Unpaid'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='subscriptions')

    # Stripe data
    stripe_subscription_id = models.CharField(max_length=100, blank=True, help_text='Stripe Subscription ID')
    stripe_customer_id = models.CharField(max_length=100, blank=True, help_text='Stripe Customer ID')

    # Status
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.TRIALING)

    # Billing period
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)

    # Cancellation
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Subscription'
        verbose_name_plural = 'User Subscriptions'

    def __str__(self):
        return f"{self.user.email} - {self.plan.name} ({self.status})"

    @property
    def is_active(self):
        """Check if subscription is active or trialing."""
        return self.status in [self.Status.ACTIVE, self.Status.TRIALING]

    @property
    def days_until_renewal(self):
        """Calculate days until next renewal."""
        if self.current_period_end:
            delta = self.current_period_end - timezone.now()
            return max(0, delta.days)
        return 0


class Usage(models.Model):
    """
    Track user's monthly usage for quota enforcement.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usage_records')

    # Usage metrics
    descriptions_generated = models.IntegerField(default=0)

    # Period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Usage Record'
        verbose_name_plural = 'Usage Records'
        ordering = ['-period_start']
        indexes = [
            models.Index(fields=['user', 'period_start']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.descriptions_generated} descriptions ({self.period_start.strftime('%Y-%m')})"

    @property
    def is_current_period(self):
        """Check if this is the current billing period."""
        now = timezone.now()
        return self.period_start <= now <= self.period_end

    @classmethod
    def get_or_create_current(cls, user):
        """
        Get or create usage record for current billing period.
        """
        now = timezone.now()

        # Calculate period boundaries (monthly)
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Next month
        if period_start.month == 12:
            period_end = period_start.replace(year=period_start.year + 1, month=1)
        else:
            period_end = period_start.replace(month=period_start.month + 1)

        period_end = period_end - timedelta(seconds=1)

        usage, created = cls.objects.get_or_create(
            user=user,
            period_start__lte=now,
            period_end__gte=now,
            defaults={
                'period_start': period_start,
                'period_end': period_end,
                'descriptions_generated': 0,
            }
        )

        return usage

    def increment_usage(self, count=1):
        """Increment description count."""
        self.descriptions_generated += count
        self.save()

    def get_remaining_quota(self):
        """Get remaining quota for this period."""
        try:
            subscription = self.user.subscription
            if subscription.plan.is_unlimited:
                return float('inf')

            quota = subscription.plan.description_quota
            return max(0, quota - self.descriptions_generated)
        except UserSubscription.DoesNotExist:
            return 0

    def has_quota_remaining(self):
        """Check if user has quota remaining."""
        remaining = self.get_remaining_quota()
        return remaining > 0 or remaining == float('inf')
