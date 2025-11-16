"""
Management command to initialize subscription plans.
Run with: python manage.py init_plans
"""
from django.core.management.base import BaseCommand
from decimal import Decimal
from apps.subscriptions.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Initialize subscription plans for ListingCraft'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing plans and recreate them',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('Deleting existing plans...'))
            SubscriptionPlan.objects.all().delete()

        # Define subscription plans
        plans = [
            {
                'name': 'Basic',
                'plan_type': 'BASIC',
                'price': Decimal('9.99'),
                'description_quota': 10,
                'features': [
                    'AI-powered descriptions',
                    '10 listings per month',
                    'Email support',
                    'Basic customization',
                ],
                'description': 'Perfect for individual agents getting started with AI-powered listings.',
                'stripe_price_id': '',  # Add your Stripe price ID
                'stripe_product_id': '',  # Add your Stripe product ID
            },
            {
                'name': 'Professional',
                'plan_type': 'PRO',
                'price': Decimal('29.99'),
                'description_quota': 50,
                'features': [
                    'AI-powered descriptions',
                    '50 listings per month',
                    'Priority email support',
                    'Advanced customization',
                    'Tone & audience targeting',
                    'Description history',
                    'Export to multiple formats',
                ],
                'description': 'Ideal for busy real estate professionals who need more listings.',
                'stripe_price_id': '',  # Add your Stripe price ID
                'stripe_product_id': '',  # Add your Stripe product ID
            },
            {
                'name': 'Agency',
                'plan_type': 'AGENCY',
                'price': Decimal('99.99'),
                'description_quota': -1,  # Unlimited
                'features': [
                    'AI-powered descriptions',
                    'Unlimited listings',
                    '24/7 priority support',
                    'Full customization',
                    'Tone & audience targeting',
                    'Description history',
                    'Export to multiple formats',
                    'Team collaboration (coming soon)',
                    'White-label option (coming soon)',
                    'API access (coming soon)',
                ],
                'description': 'Complete solution for real estate agencies and teams.',
                'stripe_price_id': '',  # Add your Stripe price ID
                'stripe_product_id': '',  # Add your Stripe product ID
            },
        ]

        created_count = 0
        updated_count = 0

        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.update_or_create(
                plan_type=plan_data['plan_type'],
                defaults=plan_data
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created plan: {plan.name} (${plan.price}/month)'
                    )
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'→ Updated plan: {plan.name} (${plan.price}/month)'
                    )
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(
            self.style.SUCCESS(
                f'Subscription plans initialized successfully!'
            )
        )
        self.stdout.write(self.style.SUCCESS(f'  - Created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'  - Updated: {updated_count}'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')

        if not any(p['stripe_price_id'] for p in plans):
            self.stdout.write(
                self.style.WARNING(
                    'WARNING: Stripe Price IDs not set. Please update them in:'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    '  - Django Admin: /admin/subscriptions/subscriptionplan/'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    '  - Or update the command in: apps/subscriptions/management/commands/init_plans.py'
                )
            )
