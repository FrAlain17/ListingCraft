"""
Management command to seed subscription plans.
Usage: python manage.py seed_plans
"""
from django.core.management.base import BaseCommand
from apps.subscriptions.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Seeds subscription plans in the database'

    def handle(self, *args, **options):
        plans_data = [
            {
                'name': 'Basic',
                'plan_type': 'BASIC',
                'price': 29.00,
                'description_quota': 50,
                'description': 'Perfect for individual agents',
                'features': [
                    '50 descriptions per month',
                    'All property types',
                    'Multiple tone options',
                    'Email support',
                    'Copy & save descriptions',
                ],
                'stripe_price_id': '',  # Add Stripe Price ID here after creating in Stripe
                'stripe_product_id': '',  # Add Stripe Product ID here after creating in Stripe
            },
            {
                'name': 'Pro',
                'plan_type': 'PRO',
                'price': 79.00,
                'description_quota': 200,
                'description': 'Great for small agencies',
                'features': [
                    '200 descriptions per month',
                    'All property types',
                    'Multiple tone options',
                    'Priority email support',
                    'Copy & save descriptions',
                    'Advanced customization',
                ],
                'stripe_price_id': '',  # Add Stripe Price ID here after creating in Stripe
                'stripe_product_id': '',  # Add Stripe Product ID here after creating in Stripe
            },
            {
                'name': 'Agency',
                'plan_type': 'AGENCY',
                'price': 199.00,
                'description_quota': -1,  # Unlimited
                'description': 'For large agencies and teams',
                'features': [
                    'Unlimited descriptions',
                    'All property types',
                    'Multiple tone options',
                    '24/7 priority support',
                    'Copy & save descriptions',
                    'Advanced customization',
                    'Team collaboration',
                    'API access',
                ],
                'stripe_price_id': '',  # Add Stripe Price ID here after creating in Stripe
                'stripe_product_id': '',  # Add Stripe Product ID here after creating in Stripe
            },
        ]

        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.update_or_create(
                plan_type=plan_data['plan_type'],
                defaults={
                    'name': plan_data['name'],
                    'price': plan_data['price'],
                    'description_quota': plan_data['description_quota'],
                    'description': plan_data['description'],
                    'features': plan_data['features'],
                    'stripe_price_id': plan_data['stripe_price_id'],
                    'stripe_product_id': plan_data['stripe_product_id'],
                    'is_active': True,
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created plan: {plan.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Updated plan: {plan.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('\nSuccessfully seeded subscription plans!')
        )
        self.stdout.write(
            self.style.WARNING('\nIMPORTANT: Remember to update Stripe Price IDs and Product IDs in the database after creating products in Stripe Dashboard.')
        )
