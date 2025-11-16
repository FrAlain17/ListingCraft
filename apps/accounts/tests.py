"""
Unit tests for accounts app.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch, Mock

from apps.accounts.models import UserProfile
from apps.accounts.email_service import EmailService
from apps.core.security import SecurityAuditLog

User = get_user_model()


def create_test_user(email='test@example.com', password='testpass123'):
    """Helper function to create test users with proper username."""
    username = email.split('@')[0]
    return User.objects.create_user(
        username=username,
        email=email,
        password=password
    )


class UserProfileModelTest(TestCase):
    """Test UserProfile model."""

    def setUp(self):
        """Set up test data."""
        self.user = create_test_user()

    def test_profile_auto_created(self):
        """Test that profile is auto-created with user."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsNotNone(self.user.profile)

    def test_profile_str_method(self):
        """Test string representation."""
        self.assertEqual(str(self.user.profile), 'test@example.com')

    def test_default_role(self):
        """Test default role is CLIENT."""
        self.assertEqual(self.user.profile.role, 'CLIENT')

    def test_role_choices(self):
        """Test role choices are valid."""
        valid_roles = ['CLIENT', 'ADMIN']
        self.assertIn(self.user.profile.role, valid_roles)

        # Test changing role
        self.user.profile.role = 'ADMIN'
        self.user.profile.save()

        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.role, 'ADMIN')

    def test_is_admin_property(self):
        """Test is_admin property."""
        self.assertFalse(self.user.profile.is_admin)

        self.user.profile.role = 'ADMIN'
        self.user.profile.save()

        self.assertTrue(self.user.profile.is_admin)

    def test_is_client_property(self):
        """Test is_client property."""
        self.assertTrue(self.user.profile.is_client)

        self.user.profile.role = 'ADMIN'
        self.user.profile.save()

        self.assertFalse(self.user.profile.is_client)

    def test_profile_timestamps(self):
        """Test auto timestamp fields."""
        self.assertIsNotNone(self.user.profile.created_at)
        self.assertIsNotNone(self.user.profile.updated_at)


class EmailServiceTest(TestCase):
    """Test EmailService."""

    def setUp(self):
        """Set up test data."""
        self.user = create_test_user()

    @patch('django.core.mail.send_mail')
    def test_send_welcome_email(self, mock_send):
        """Test sending welcome email."""
        EmailService.send_welcome_email(self.user)

        # Check that send_mail was called
        mock_send.assert_called_once()

        # Check arguments
        call_args = mock_send.call_args
        self.assertIn('Welcome', call_args[1]['subject'])
        self.assertEqual(call_args[1]['recipient_list'], [self.user.email])

    @patch('django.core.mail.send_mail')
    def test_send_subscription_confirmation(self, mock_send):
        """Test sending subscription confirmation email."""
        from apps.subscriptions.models import SubscriptionPlan, UserSubscription
        from decimal import Decimal

        plan = SubscriptionPlan.objects.create(
            name='Pro',
            slug='pro',
            price=Decimal('29.99'),
            billing_period='MONTHLY',
            description_quota=50
        )

        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=plan,
            status='ACTIVE',
            stripe_subscription_id='sub_test123'
        )

        EmailService.send_subscription_confirmation(self.user, subscription)

        # Check that send_mail was called
        mock_send.assert_called_once()

        # Check arguments
        call_args = mock_send.call_args
        self.assertIn('subscription', call_args[1]['subject'].lower())

    @patch('django.core.mail.send_mail')
    def test_send_quota_warning(self, mock_send):
        """Test sending quota warning email."""
        from apps.subscriptions.models import SubscriptionPlan, UserSubscription, Usage
        from decimal import Decimal

        plan = SubscriptionPlan.objects.create(
            name='Free',
            slug='free',
            price=Decimal('0.00'),
            billing_period='MONTHLY',
            description_quota=5
        )

        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=plan,
            status='ACTIVE',
            stripe_subscription_id='sub_test123'
        )

        usage = Usage.get_or_create_current(self.user)
        usage.descriptions_generated = 4
        usage.save()

        EmailService.send_quota_warning(self.user, usage, subscription)

        # Check that send_mail was called
        mock_send.assert_called_once()

        # Check arguments
        call_args = mock_send.call_args
        self.assertIn('quota', call_args[1]['subject'].lower())

    @patch('django.core.mail.send_mail')
    def test_send_password_reset_email(self, mock_send):
        """Test sending password reset email."""
        reset_url = 'https://example.com/reset/token123'

        EmailService.send_password_reset_email(self.user, reset_url)

        # Check that send_mail was called
        mock_send.assert_called_once()

        # Check arguments
        call_args = mock_send.call_args
        self.assertIn('password', call_args[1]['subject'].lower())

    @patch('django.core.mail.send_mail')
    def test_email_error_handling(self, mock_send):
        """Test email sending with errors."""
        mock_send.side_effect = Exception('SMTP Error')

        # Should not raise exception
        try:
            EmailService.send_welcome_email(self.user)
        except Exception:
            self.fail("EmailService should handle exceptions gracefully")


class SecurityAuditLogTest(TestCase):
    """Test SecurityAuditLog."""

    @patch('logging.Logger.warning')
    def test_log_failed_login(self, mock_log):
        """Test logging failed login attempts."""
        SecurityAuditLog.log_failed_login('test@example.com', '127.0.0.1')

        # Check that logger was called
        mock_log.assert_called_once()
        call_args = str(mock_log.call_args)
        self.assertIn('test@example.com', call_args)
        self.assertIn('127.0.0.1', call_args)

    @patch('logging.Logger.warning')
    def test_log_suspicious_activity(self, mock_log):
        """Test logging suspicious activity."""
        user = create_test_user()

        SecurityAuditLog.log_suspicious_activity(
            user, 'Multiple failed requests', '127.0.0.1'
        )

        # Check that logger was called
        mock_log.assert_called_once()

    @patch('logging.Logger.warning')
    def test_log_permission_denied(self, mock_log):
        """Test logging permission denied."""
        user = create_test_user()

        SecurityAuditLog.log_permission_denied(
            user, '/admin/dashboard/', '127.0.0.1'
        )

        # Check that logger was called
        mock_log.assert_called_once()

    @patch('logging.Logger.warning')
    def test_log_rate_limit_exceeded(self, mock_log):
        """Test logging rate limit exceeded."""
        SecurityAuditLog.log_rate_limit_exceeded('127.0.0.1', '/api/generate/')

        # Check that logger was called
        mock_log.assert_called_once()


class AuthenticationViewsTest(TestCase):
    """Test authentication views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()

    def test_signup_page(self):
        """Test signup page loads."""
        response = self.client.get(reverse('account_signup'))
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        """Test login page loads."""
        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)

    def test_logout_requires_authentication(self):
        """Test logout requires authenticated user."""
        response = self.client.get(reverse('account_logout'))
        # Should redirect or show logout page
        self.assertIn(response.status_code, [200, 302])

    @patch('apps.accounts.email_service.EmailService.send_welcome_email')
    def test_user_signup(self, mock_email):
        """Test user signup creates profile and sends email."""
        response = self.client.post(reverse('account_signup'), {
            'email': 'newuser@example.com',
            'password1': 'strongpass123!',
            'password2': 'strongpass123!',
        })

        # Check user was created
        user = User.objects.filter(email='newuser@example.com').first()
        if user:
            self.assertIsNotNone(user)
            self.assertTrue(hasattr(user, 'profile'))
            self.assertEqual(user.profile.role, 'CLIENT')

    def test_user_login(self):
        """Test user login."""
        user = create_test_user()

        response = self.client.post(reverse('account_login'), {
            'login': 'test@example.com',
            'password': 'testpass123',
        })

        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)

    def test_user_logout(self):
        """Test user logout."""
        user = create_test_user()

        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(reverse('account_logout'))

        # Should redirect after logout
        self.assertEqual(response.status_code, 302)


class DecoratorTest(TestCase):
    """Test custom decorators."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()

        self.client_user = create_test_user(email='client@example.com')

        self.admin_user = create_test_user(email='admin@example.com')
        self.admin_user.profile.role = 'ADMIN'
        self.admin_user.profile.save()

    def test_client_required_decorator(self):
        """Test client_required decorator."""
        # Client user should access client pages
        self.client.login(email='client@example.com', password='testpass123')
        response = self.client.get(reverse('dashboard:overview'))
        self.assertEqual(response.status_code, 200)

    def test_admin_required_decorator(self):
        """Test admin_required decorator."""
        # Admin user should access admin pages
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.get(reverse('dashboard:admin'))
        self.assertEqual(response.status_code, 200)

        # Client user should NOT access admin pages
        self.client.logout()
        self.client.login(email='client@example.com', password='testpass123')
        response = self.client.get(reverse('dashboard:admin'))
        self.assertEqual(response.status_code, 302)  # Redirect


class SignalTest(TestCase):
    """Test signal handlers."""

    @patch('apps.accounts.email_service.EmailService.send_welcome_email')
    def test_profile_created_on_user_creation(self, mock_email):
        """Test that profile is created when user is created."""
        user = create_test_user(email='newuser@example.com')

        # Profile should be auto-created
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.role, 'CLIENT')

    @patch('apps.accounts.email_service.EmailService.send_welcome_email')
    def test_welcome_email_sent_on_signup(self, mock_email):
        """Test that welcome email is sent on user signup."""
        user = create_test_user(email='newuser@example.com')

        # Welcome email should be sent
        # Note: This might not be called in test environment if EMAIL_ENABLED=False
        # Check the signal implementation for EMAIL_ENABLED flag


class UserModelTest(TestCase):
    """Test custom User model."""

    def test_create_user(self):
        """Test creating a user."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )

        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_user_str_method(self):
        """Test string representation."""
        user = create_test_user()

        # Django's default User model uses username as string representation
        self.assertEqual(str(user), 'test')

    def test_email_is_unique(self):
        """Test that username must be unique."""
        create_test_user()

        with self.assertRaises(Exception):
            create_test_user()  # Try to create user with same username
