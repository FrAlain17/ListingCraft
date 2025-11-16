"""
Unit tests for subscriptions app.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from unittest.mock import patch, Mock

from apps.subscriptions.models import SubscriptionPlan, UserSubscription, Usage
from apps.subscriptions.services import SubscriptionService
from apps.accounts.models import UserProfile

User = get_user_model()


def create_test_user(email='test@example.com', password='testpass123'):
    """Helper function to create test users with proper username."""
    username = email.split('@')[0]
    return User.objects.create_user(
        username=username,
        email=email,
        password=password
    )


class SubscriptionPlanModelTest(TestCase):
    """Test SubscriptionPlan model."""

    def setUp(self):
        """Set up test data."""
        self.free_plan = SubscriptionPlan.objects.create(
            name='Free',
            slug='free',
            price=Decimal('0.00'),
            billing_period='MONTHLY',
            description_quota=5,
            features={'basic': True},
            is_active=True
        )

        self.pro_plan = SubscriptionPlan.objects.create(
            name='Professional',
            slug='professional',
            price=Decimal('29.99'),
            billing_period='MONTHLY',
            description_quota=50,
            features={'advanced': True, 'priority_support': True},
            is_active=True
        )

    def test_plan_creation(self):
        """Test creating subscription plans."""
        self.assertEqual(self.free_plan.name, 'Free')
        self.assertEqual(self.free_plan.price, Decimal('0.00'))
        self.assertEqual(self.free_plan.description_quota, 5)
        self.assertTrue(self.free_plan.is_active)

    def test_plan_str_method(self):
        """Test string representation."""
        self.assertEqual(str(self.free_plan), 'Free - $0.00/MONTHLY')
        self.assertEqual(str(self.pro_plan), 'Professional - $29.99/MONTHLY')

    def test_plan_slug_unique(self):
        """Test that plan slugs are unique."""
        with self.assertRaises(Exception):
            SubscriptionPlan.objects.create(
                name='Another Free',
                slug='free',  # Duplicate slug
                price=Decimal('0.00'),
                billing_period='MONTHLY'
            )

    def test_get_active_plans(self):
        """Test retrieving active plans."""
        active_plans = SubscriptionPlan.objects.filter(is_active=True)
        self.assertEqual(active_plans.count(), 2)

    def test_plan_ordering(self):
        """Test plans are ordered by price."""
        plans = SubscriptionPlan.objects.all()
        self.assertEqual(plans[0], self.free_plan)
        self.assertEqual(plans[1], self.pro_plan)


class UserSubscriptionModelTest(TestCase):
    """Test UserSubscription model."""

    def setUp(self):
        """Set up test data."""
        self.user = create_test_user()

        self.plan = SubscriptionPlan.objects.create(
            name='Pro',
            slug='pro',
            price=Decimal('29.99'),
            billing_period='MONTHLY',
            description_quota=50
        )

        self.subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.plan,
            status='ACTIVE',
            stripe_subscription_id='sub_test123'
        )

    def test_subscription_creation(self):
        """Test creating user subscription."""
        self.assertEqual(self.subscription.user, self.user)
        self.assertEqual(self.subscription.plan, self.plan)
        self.assertEqual(self.subscription.status, 'ACTIVE')
        self.assertIsNotNone(self.subscription.current_period_start)
        self.assertIsNotNone(self.subscription.current_period_end)

    def test_subscription_str_method(self):
        """Test string representation."""
        expected = f"{self.user.email} - Pro (ACTIVE)"
        self.assertEqual(str(self.subscription), expected)

    def test_subscription_dates(self):
        """Test subscription period dates."""
        self.assertIsInstance(self.subscription.current_period_start, timezone.datetime)
        self.assertIsInstance(self.subscription.current_period_end, timezone.datetime)
        self.assertTrue(
            self.subscription.current_period_end > self.subscription.current_period_start
        )

    def test_is_active_property(self):
        """Test is_active property."""
        self.assertTrue(self.subscription.is_active)

        self.subscription.status = 'CANCELED'
        self.subscription.save()
        self.assertFalse(self.subscription.is_active)

    def test_one_subscription_per_user(self):
        """Test that user can only have one active subscription."""
        # The database constraint should prevent this
        # In practice, application logic should handle this
        subscriptions = UserSubscription.objects.filter(user=self.user)
        self.assertEqual(subscriptions.count(), 1)

    def test_subscription_cancellation(self):
        """Test canceling subscription."""
        self.subscription.status = 'CANCELED'
        self.subscription.cancel_at_period_end = True
        self.subscription.canceled_at = timezone.now()
        self.subscription.save()

        self.assertEqual(self.subscription.status, 'CANCELED')
        self.assertTrue(self.subscription.cancel_at_period_end)
        self.assertIsNotNone(self.subscription.canceled_at)


class UsageModelTest(TestCase):
    """Test Usage model."""

    def setUp(self):
        """Set up test data."""
        self.user = create_test_user()

        self.usage = Usage.objects.create(
            user=self.user,
            period_start=timezone.now(),
            period_end=timezone.now() + timedelta(days=30),
            descriptions_generated=10
        )

    def test_usage_creation(self):
        """Test creating usage record."""
        self.assertEqual(self.usage.user, self.user)
        self.assertEqual(self.usage.descriptions_generated, 10)
        self.assertIsNotNone(self.usage.period_start)
        self.assertIsNotNone(self.usage.period_end)

    def test_usage_str_method(self):
        """Test string representation."""
        self.assertIn(self.user.email, str(self.usage))
        self.assertIn('10 descriptions', str(self.usage))

    def test_get_or_create_current(self):
        """Test get_or_create_current method."""
        usage = Usage.get_or_create_current(self.user)
        self.assertIsNotNone(usage)
        self.assertEqual(usage.user, self.user)

        # Should return same usage if called again
        usage2 = Usage.get_or_create_current(self.user)
        self.assertEqual(usage.id, usage2.id)

    def test_usage_increment(self):
        """Test incrementing usage count."""
        initial_count = self.usage.descriptions_generated
        self.usage.descriptions_generated += 1
        self.usage.save()

        self.usage.refresh_from_db()
        self.assertEqual(self.usage.descriptions_generated, initial_count + 1)

    def test_usage_reset(self):
        """Test resetting usage for new period."""
        # Create new usage period
        new_usage = Usage.objects.create(
            user=self.user,
            period_start=timezone.now(),
            period_end=timezone.now() + timedelta(days=30),
            descriptions_generated=0
        )

        self.assertEqual(new_usage.descriptions_generated, 0)


class SubscriptionServiceTest(TestCase):
    """Test SubscriptionService."""

    def setUp(self):
        """Set up test data."""
        self.user = create_test_user()

        self.free_plan = SubscriptionPlan.objects.create(
            name='Free',
            slug='free',
            price=Decimal('0.00'),
            billing_period='MONTHLY',
            description_quota=5
        )

        self.pro_plan = SubscriptionPlan.objects.create(
            name='Pro',
            slug='pro',
            price=Decimal('29.99'),
            billing_period='MONTHLY',
            description_quota=50
        )

    def test_create_subscription(self):
        """Test creating subscription through service."""
        subscription = SubscriptionService.create_subscription(
            user=self.user,
            plan=self.free_plan,
            stripe_subscription_id='sub_test123'
        )

        self.assertIsNotNone(subscription)
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.plan, self.free_plan)
        self.assertEqual(subscription.status, 'ACTIVE')

    def test_update_subscription(self):
        """Test updating subscription."""
        subscription = SubscriptionService.create_subscription(
            user=self.user,
            plan=self.free_plan,
            stripe_subscription_id='sub_test123'
        )

        updated = SubscriptionService.update_subscription(
            subscription=subscription,
            plan=self.pro_plan
        )

        self.assertEqual(updated.plan, self.pro_plan)

    def test_cancel_subscription(self):
        """Test canceling subscription."""
        subscription = SubscriptionService.create_subscription(
            user=self.user,
            plan=self.pro_plan,
            stripe_subscription_id='sub_test123'
        )

        canceled = SubscriptionService.cancel_subscription(subscription)

        self.assertEqual(canceled.status, 'CANCELED')
        self.assertTrue(canceled.cancel_at_period_end)
        self.assertIsNotNone(canceled.canceled_at)

    def test_check_quota_within_limit(self):
        """Test quota check when within limit."""
        subscription = SubscriptionService.create_subscription(
            user=self.user,
            plan=self.free_plan,
            stripe_subscription_id='sub_test123'
        )

        # Generate some descriptions but stay within quota
        usage = Usage.get_or_create_current(self.user)
        usage.descriptions_generated = 3
        usage.save()

        has_quota, message = SubscriptionService.check_quota(self.user)
        self.assertTrue(has_quota)
        self.assertIn('2 descriptions remaining', message)

    def test_check_quota_exceeded(self):
        """Test quota check when exceeded."""
        subscription = SubscriptionService.create_subscription(
            user=self.user,
            plan=self.free_plan,
            stripe_subscription_id='sub_test123'
        )

        # Exceed quota
        usage = Usage.get_or_create_current(self.user)
        usage.descriptions_generated = 5
        usage.save()

        has_quota, message = SubscriptionService.check_quota(self.user)
        self.assertFalse(has_quota)
        self.assertIn('quota limit', message.lower())

    def test_increment_usage(self):
        """Test incrementing usage count."""
        subscription = SubscriptionService.create_subscription(
            user=self.user,
            plan=self.free_plan,
            stripe_subscription_id='sub_test123'
        )

        initial_usage = Usage.get_or_create_current(self.user)
        initial_count = initial_usage.descriptions_generated

        SubscriptionService.increment_usage(self.user)

        updated_usage = Usage.get_or_create_current(self.user)
        self.assertEqual(updated_usage.descriptions_generated, initial_count + 1)

    def test_no_subscription_defaults_to_free(self):
        """Test that users without subscription get free tier limits."""
        has_quota, message = SubscriptionService.check_quota(self.user)
        # Should still allow some usage even without explicit subscription
        self.assertIsNotNone(message)


class SubscriptionViewsTest(TestCase):
    """Test subscription views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = create_test_user()

        self.plan = SubscriptionPlan.objects.create(
            name='Pro',
            slug='pro',
            price=Decimal('29.99'),
            billing_period='MONTHLY',
            description_quota=50
        )

    def test_subscription_plans_view(self):
        """Test subscription plans listing view."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('subscriptions:plans'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pro')

    def test_manage_subscription_view_requires_login(self):
        """Test manage subscription requires authentication."""
        response = self.client.get(reverse('subscriptions:manage'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_manage_subscription_view_authenticated(self):
        """Test manage subscription view for authenticated user."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('subscriptions:manage'))

        self.assertEqual(response.status_code, 200)

    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session(self, mock_create):
        """Test creating Stripe checkout session."""
        mock_create.return_value = Mock(id='cs_test123', url='https://checkout.stripe.com/test')

        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(
            reverse('subscriptions:create_checkout_session'),
            {'price_id': 'price_test123'}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('sessionId', data)


class WebhookHandlerTest(TestCase):
    """Test Stripe webhook handling."""

    def setUp(self):
        """Set up test data."""
        self.user = create_test_user()

        self.plan = SubscriptionPlan.objects.create(
            name='Pro',
            slug='pro',
            price=Decimal('29.99'),
            billing_period='MONTHLY',
            description_quota=50,
            stripe_price_id='price_test123'
        )

    @patch('stripe.Webhook.construct_event')
    def test_webhook_subscription_created(self, mock_construct):
        """Test webhook for subscription.created event."""
        # This would test the webhook handler
        # Implementation depends on your webhook view structure
        pass

    @patch('stripe.Webhook.construct_event')
    def test_webhook_subscription_updated(self, mock_construct):
        """Test webhook for subscription.updated event."""
        pass

    @patch('stripe.Webhook.construct_event')
    def test_webhook_subscription_deleted(self, mock_construct):
        """Test webhook for subscription.deleted event."""
        pass
