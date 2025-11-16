"""
Unit tests for listings app.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from unittest.mock import patch, Mock
import json

from apps.listings.models import Listing
from apps.listings.forms import ListingForm
from apps.listings.services import DeepSeekService, ListingService
from apps.subscriptions.models import SubscriptionPlan, UserSubscription, Usage

User = get_user_model()


def create_test_user(email='test@example.com', password='testpass123'):
    """Helper function to create test users with proper username."""
    username = email.split('@')[0]
    return User.objects.create_user(
        username=username,
        email=email,
        password=password
    )


class ListingModelTest(TestCase):
    """Test Listing model."""

    def setUp(self):
        """Set up test data."""
        self.user = create_test_user()

        self.listing = Listing.objects.create(
            user=self.user,
            property_type='APARTMENT',
            title='Luxury Downtown Apartment',
            city='New York',
            state='NY',
            country='USA',
            price=Decimal('500000.00'),
            bedrooms=2,
            bathrooms=Decimal('2.0'),
            square_feet=1200,
            year_built=2020,
            key_features=['pool', 'gym', 'parking'],
            tone='PROFESSIONAL',
            target_audience='FAMILIES',
            generated_description='Beautiful apartment with amazing views.'
        )

    def test_listing_creation(self):
        """Test creating a listing."""
        self.assertEqual(self.listing.user, self.user)
        self.assertEqual(self.listing.property_type, 'APARTMENT')
        self.assertEqual(self.listing.title, 'Luxury Downtown Apartment')
        self.assertEqual(self.listing.price, Decimal('500000.00'))
        self.assertEqual(self.listing.bedrooms, 2)
        self.assertEqual(self.listing.bathrooms, Decimal('2.0'))

    def test_listing_str_method(self):
        """Test string representation."""
        self.assertIn('Luxury Downtown Apartment', str(self.listing))

    def test_listing_slug_generation(self):
        """Test that slug is auto-generated."""
        self.assertIsNotNone(self.listing.slug)
        self.assertIn('luxury-downtown-apartment', self.listing.slug.lower())

    def test_listing_absolute_url(self):
        """Test get_absolute_url method."""
        url = self.listing.get_absolute_url()
        self.assertIn('/listings/', url)
        self.assertIn(self.listing.slug, url)

    def test_listing_key_features_json(self):
        """Test JSONField for key features."""
        self.assertIsInstance(self.listing.key_features, list)
        self.assertIn('pool', self.listing.key_features)
        self.assertEqual(len(self.listing.key_features), 3)

    def test_listing_property_type_choices(self):
        """Test property type choices."""
        valid_types = [
            'APARTMENT', 'HOUSE', 'VILLA', 'CONDO', 'TOWNHOUSE',
            'PENTHOUSE', 'STUDIO', 'LAND', 'COMMERCIAL', 'OTHER'
        ]
        self.assertIn(self.listing.property_type, valid_types)

    def test_listing_tone_choices(self):
        """Test tone choices."""
        valid_tones = ['PROFESSIONAL', 'CASUAL', 'LUXURY', 'FRIENDLY']
        self.assertIn(self.listing.tone, valid_tones)

    def test_listing_timestamps(self):
        """Test auto timestamp fields."""
        self.assertIsNotNone(self.listing.created_at)
        self.assertIsNotNone(self.listing.updated_at)

    def test_listing_generation_count(self):
        """Test generation count tracking."""
        self.assertEqual(self.listing.generation_count, 0)

        self.listing.generation_count += 1
        self.listing.save()

        self.listing.refresh_from_db()
        self.assertEqual(self.listing.generation_count, 1)

    def test_final_description_property(self):
        """Test final_description property."""
        # When no edited description, should return generated
        self.assertEqual(self.listing.final_description, self.listing.generated_description)

        # When edited description exists, should return edited
        self.listing.edited_description = 'Custom edited description'
        self.assertEqual(self.listing.final_description, 'Custom edited description')


class ListingFormTest(TestCase):
    """Test ListingForm."""

    def test_valid_form(self):
        """Test form with valid data."""
        form_data = {
            'property_type': 'APARTMENT',
            'title': 'Test Apartment',
            'city': 'Boston',
            'state': 'MA',
            'country': 'USA',
            'price': '300000',
            'bedrooms': 2,
            'bathrooms': '2.0',
            'square_feet': 1000,
            'year_built': 2020,
            'key_features_text': 'pool, gym, parking',
            'tone': 'PROFESSIONAL',
            'target_audience': 'FAMILIES'
        }
        form = ListingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_required(self):
        """Test form with missing required fields."""
        form_data = {
            'property_type': 'APARTMENT',
            # Missing title
            'city': 'Boston',
        }
        form = ListingForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_key_features_parsing(self):
        """Test parsing key features from text."""
        form_data = {
            'property_type': 'APARTMENT',
            'title': 'Test',
            'city': 'Boston',
            'state': 'MA',
            'country': 'USA',
            'price': '300000',
            'key_features_text': 'pool, gym, parking',
            'tone': 'PROFESSIONAL',
            'target_audience': 'FAMILIES'
        }
        form = ListingForm(data=form_data)
        self.assertTrue(form.is_valid())

        # The form should save with key_features populated
        listing = form.save(commit=False)
        self.assertEqual(len(listing.key_features), 3)
        self.assertIn('pool', listing.key_features)

    def test_form_widgets(self):
        """Test form widgets are properly configured."""
        form = ListingForm()
        # Check that widgets have proper CSS classes
        self.assertIn('class', form.fields['title'].widget.attrs)


class DeepSeekServiceTest(TestCase):
    """Test DeepSeekService."""

    def setUp(self):
        """Set up test data."""
        self.user = create_test_user()

        self.listing = Listing.objects.create(
            user=self.user,
            property_type='APARTMENT',
            title='Test Apartment',
            city='Boston',
            state='MA',
            country='USA',
            price=Decimal('300000.00'),
            bedrooms=2,
            bathrooms=Decimal('2.0'),
            square_feet=1000,
            key_features=['pool', 'gym'],
            tone='PROFESSIONAL',
            target_audience='FAMILIES'
        )

    def test_build_prompt(self):
        """Test building prompt for API."""
        prompt = DeepSeekService._build_prompt(self.listing)

        self.assertIn('APARTMENT', prompt)
        self.assertIn('Test Apartment', prompt)
        self.assertIn('Boston', prompt)
        self.assertIn('$300,000', prompt)
        self.assertIn('2 bedrooms', prompt)
        self.assertIn('pool', prompt)

    def test_get_system_prompt(self):
        """Test system prompt generation."""
        professional_prompt = DeepSeekService._get_system_prompt('PROFESSIONAL')
        self.assertIn('professional', professional_prompt.lower())

        luxury_prompt = DeepSeekService._get_system_prompt('LUXURY')
        self.assertIn('luxury', luxury_prompt.lower())

    @patch('requests.post')
    def test_generate_description_success(self, mock_post):
        """Test successful description generation."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': 'This is a beautiful apartment in the heart of Boston.'
                }
            }]
        }
        mock_post.return_value = mock_response

        initial_count = self.listing.generation_count
        description = DeepSeekService.generate_description(self.listing)

        self.assertIsNotNone(description)
        self.assertIn('beautiful', description.lower())

        # Check listing was updated
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.generated_description, description)
        self.assertEqual(self.listing.generation_count, initial_count + 1)

    @patch('requests.post')
    def test_generate_description_api_error(self, mock_post):
        """Test handling API errors."""
        mock_post.side_effect = Exception('API Error')

        with self.assertRaises(Exception):
            DeepSeekService.generate_description(self.listing)

    @patch('requests.post')
    def test_generate_description_timeout(self, mock_post):
        """Test handling timeouts."""
        import requests
        mock_post.side_effect = requests.Timeout('Request timeout')

        with self.assertRaises(requests.Timeout):
            DeepSeekService.generate_description(self.listing)


class ListingServiceTest(TestCase):
    """Test ListingService."""

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

    @patch('apps.listings.services.DeepSeekService.generate_description')
    def test_create_listing_with_description_success(self, mock_generate):
        """Test successful listing creation with description."""
        mock_generate.return_value = 'Beautiful apartment description.'

        listing_data = {
            'property_type': 'APARTMENT',
            'title': 'Test Apartment',
            'city': 'Boston',
            'state': 'MA',
            'country': 'USA',
            'price': Decimal('300000.00'),
            'bedrooms': 2,
            'bathrooms': Decimal('2.0'),
            'square_feet': 1000,
            'key_features': ['pool', 'gym'],
            'tone': 'PROFESSIONAL',
            'target_audience': 'FAMILIES'
        }

        listing, success, message = ListingService.create_listing_with_description(
            self.user, listing_data
        )

        self.assertTrue(success)
        self.assertIsNotNone(listing)
        self.assertEqual(listing.user, self.user)
        self.assertEqual(listing.generated_description, 'Beautiful apartment description.')

        # Check usage was incremented
        usage = Usage.get_or_create_current(self.user)
        self.assertEqual(usage.descriptions_generated, 1)

    def test_create_listing_quota_exceeded(self):
        """Test listing creation when quota exceeded."""
        # Use up all quota
        usage = Usage.get_or_create_current(self.user)
        usage.descriptions_generated = 50
        usage.save()

        listing_data = {
            'property_type': 'APARTMENT',
            'title': 'Test Apartment',
            'city': 'Boston',
            'tone': 'PROFESSIONAL',
            'target_audience': 'FAMILIES'
        }

        listing, success, message = ListingService.create_listing_with_description(
            self.user, listing_data
        )

        self.assertFalse(success)
        self.assertIsNone(listing)
        self.assertIn('quota', message.lower())

    @patch('apps.listings.services.DeepSeekService.generate_description')
    def test_create_listing_api_error(self, mock_generate):
        """Test handling API errors during creation."""
        mock_generate.side_effect = Exception('API Error')

        listing_data = {
            'property_type': 'APARTMENT',
            'title': 'Test Apartment',
            'city': 'Boston',
            'tone': 'PROFESSIONAL',
            'target_audience': 'FAMILIES'
        }

        listing, success, message = ListingService.create_listing_with_description(
            self.user, listing_data
        )

        self.assertFalse(success)
        self.assertIsNone(listing)
        self.assertIn('error', message.lower())


class ListingViewsTest(TestCase):
    """Test listing views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = create_test_user()

        # Create subscription
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

        self.listing = Listing.objects.create(
            user=self.user,
            property_type='APARTMENT',
            title='Test Apartment',
            city='Boston',
            state='MA',
            country='USA',
            price=Decimal('300000.00'),
            tone='PROFESSIONAL',
            target_audience='FAMILIES',
            generated_description='Test description'
        )

    def test_listing_list_requires_login(self):
        """Test listing list requires authentication."""
        response = self.client.get(reverse('listings:list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_listing_list_authenticated(self):
        """Test listing list for authenticated user."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('listings:list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Apartment')

    def test_listing_detail_view(self):
        """Test listing detail view."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(
            reverse('listings:detail', kwargs={'slug': self.listing.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Apartment')
        self.assertContains(response, 'Test description')

    def test_create_listing_requires_login(self):
        """Test create listing requires authentication."""
        response = self.client.get(reverse('listings:create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_create_listing_form_display(self):
        """Test create listing form displays correctly."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('listings:create'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'property_type')
        self.assertContains(response, 'title')

    @patch('apps.listings.services.ListingService.create_listing_with_description')
    def test_create_listing_post_success(self, mock_create):
        """Test successful listing creation via POST."""
        mock_listing = self.listing
        mock_create.return_value = (mock_listing, True, 'Success')

        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(reverse('listings:create'), {
            'property_type': 'APARTMENT',
            'title': 'New Apartment',
            'city': 'Boston',
            'state': 'MA',
            'country': 'USA',
            'price': '300000',
            'tone': 'PROFESSIONAL',
            'target_audience': 'FAMILIES'
        })

        # Should redirect on success
        self.assertEqual(response.status_code, 302)

    def test_edit_listing_view(self):
        """Test editing listing."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(
            reverse('listings:edit', kwargs={'slug': self.listing.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.listing.title)

    def test_edit_listing_post(self):
        """Test updating listing via POST."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(
            reverse('listings:edit', kwargs={'slug': self.listing.slug}),
            {
                'property_type': 'APARTMENT',
                'title': 'Updated Title',
                'city': 'Boston',
                'state': 'MA',
                'country': 'USA',
                'price': '350000',
                'tone': 'PROFESSIONAL',
                'target_audience': 'FAMILIES'
            }
        )

        self.listing.refresh_from_db()
        self.assertEqual(self.listing.title, 'Updated Title')

    def test_delete_listing(self):
        """Test deleting listing."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(
            reverse('listings:delete', kwargs={'slug': self.listing.slug})
        )

        # Should redirect after deletion
        self.assertEqual(response.status_code, 302)

        # Listing should be deleted
        self.assertFalse(
            Listing.objects.filter(slug=self.listing.slug).exists()
        )

    def test_user_can_only_view_own_listings(self):
        """Test users can only see their own listings."""
        # Create another user
        other_user = create_test_user(email='other@example.com')

        # Create listing for other user
        other_listing = Listing.objects.create(
            user=other_user,
            property_type='HOUSE',
            title='Other User House',
            city='Chicago',
            tone='PROFESSIONAL',
            target_audience='FAMILIES'
        )

        # Login as first user
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('listings:list'))

        # Should see own listing
        self.assertContains(response, 'Test Apartment')
        # Should NOT see other user's listing
        self.assertNotContains(response, 'Other User House')

    @patch('apps.listings.services.DeepSeekService.generate_description')
    def test_regenerate_description(self, mock_generate):
        """Test regenerating listing description."""
        mock_generate.return_value = 'Newly generated description.'

        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(
            reverse('listings:regenerate', kwargs={'slug': self.listing.slug})
        )

        self.listing.refresh_from_db()
        self.assertEqual(self.listing.generated_description, 'Newly generated description.')
