"""
Subscription service layer for handling Stripe webhook events and business logic.
"""
from datetime import datetime
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import SubscriptionPlan, UserSubscription, Usage

User = get_user_model()

# Import email service for notifications
try:
    from apps.accounts.email_service import EmailService
    EMAIL_ENABLED = True
except ImportError:
    EMAIL_ENABLED = False


class SubscriptionService:
    """
    Service class for managing subscriptions and handling Stripe events.
    """

    @staticmethod
    def handle_checkout_session_completed(session_data):
        """
        Handle successful checkout session completion.
        Creates or updates UserSubscription when customer completes checkout.
        """
        # Extract metadata
        user_id = session_data.get('metadata', {}).get('user_id')
        plan_id = session_data.get('metadata', {}).get('plan_id')
        customer_id = session_data.get('customer')
        subscription_id = session_data.get('subscription')

        if not all([user_id, plan_id, customer_id, subscription_id]):
            raise ValueError('Missing required data from checkout session')

        # Get user and plan
        user = User.objects.get(id=user_id)
        plan = SubscriptionPlan.objects.get(id=plan_id)

        # Get subscription details from Stripe
        import stripe
        stripe_subscription = stripe.Subscription.retrieve(subscription_id)

        # Create or update UserSubscription
        subscription, created = UserSubscription.objects.update_or_create(
            user=user,
            defaults={
                'plan': plan,
                'stripe_subscription_id': subscription_id,
                'stripe_customer_id': customer_id,
                'status': SubscriptionService._map_stripe_status(stripe_subscription.status),
                'current_period_start': datetime.fromtimestamp(
                    stripe_subscription.current_period_start,
                    tz=timezone.utc
                ),
                'current_period_end': datetime.fromtimestamp(
                    stripe_subscription.current_period_end,
                    tz=timezone.utc
                ),
                'trial_end': datetime.fromtimestamp(
                    stripe_subscription.trial_end,
                    tz=timezone.utc
                ) if stripe_subscription.trial_end else None,
                'cancel_at_period_end': False,
                'canceled_at': None,
            }
        )

        # Create initial usage record
        if created:
            Usage.get_or_create_current(user)

        # Send confirmation email
        if EMAIL_ENABLED and created:
            try:
                EmailService.send_subscription_confirmation(user, subscription)
            except Exception as e:
                # Log error but don't fail the subscription
                print(f"Failed to send subscription confirmation email: {e}")

        return subscription

    @staticmethod
    def handle_subscription_updated(subscription_data):
        """
        Handle subscription update events.
        Updates local subscription when Stripe subscription changes.
        """
        subscription_id = subscription_data.get('id')

        try:
            subscription = UserSubscription.objects.get(stripe_subscription_id=subscription_id)

            # Update subscription details
            subscription.status = SubscriptionService._map_stripe_status(subscription_data.get('status'))
            subscription.current_period_start = datetime.fromtimestamp(
                subscription_data.get('current_period_start'),
                tz=timezone.utc
            )
            subscription.current_period_end = datetime.fromtimestamp(
                subscription_data.get('current_period_end'),
                tz=timezone.utc
            )
            subscription.cancel_at_period_end = subscription_data.get('cancel_at_period_end', False)

            if subscription_data.get('canceled_at'):
                subscription.canceled_at = datetime.fromtimestamp(
                    subscription_data.get('canceled_at'),
                    tz=timezone.utc
                )

            subscription.save()

            return subscription

        except UserSubscription.DoesNotExist:
            # Subscription not found in database
            pass

    @staticmethod
    def handle_subscription_deleted(subscription_data):
        """
        Handle subscription cancellation/deletion.
        Marks subscription as canceled when Stripe subscription ends.
        """
        subscription_id = subscription_data.get('id')

        try:
            subscription = UserSubscription.objects.get(stripe_subscription_id=subscription_id)
            subscription.status = 'CANCELED'
            subscription.canceled_at = timezone.now()
            subscription.save()

            # Send cancellation email
            if EMAIL_ENABLED:
                try:
                    EmailService.send_subscription_cancelled(subscription.user, subscription)
                except Exception as e:
                    print(f"Failed to send cancellation email: {e}")

            return subscription

        except UserSubscription.DoesNotExist:
            pass

    @staticmethod
    def handle_payment_failed(invoice_data):
        """
        Handle failed payment attempts.
        Updates subscription status when payment fails.
        """
        subscription_id = invoice_data.get('subscription')

        if not subscription_id:
            return

        try:
            subscription = UserSubscription.objects.get(stripe_subscription_id=subscription_id)
            subscription.status = 'PAST_DUE'
            subscription.save()

            # Send payment failure email
            if EMAIL_ENABLED:
                try:
                    EmailService.send_payment_failed(subscription.user, subscription)
                except Exception as e:
                    print(f"Failed to send payment failure email: {e}")

            return subscription

        except UserSubscription.DoesNotExist:
            pass

    @staticmethod
    def handle_payment_succeeded(invoice_data):
        """
        Handle successful payment.
        Updates subscription status and creates new usage period.
        """
        subscription_id = invoice_data.get('subscription')

        if not subscription_id:
            return

        try:
            subscription = UserSubscription.objects.get(stripe_subscription_id=subscription_id)

            # Update subscription status
            if subscription.status in ['PAST_DUE', 'UNPAID']:
                subscription.status = 'ACTIVE'
                subscription.save()

            # Create new usage record for the new billing period
            Usage.get_or_create_current(subscription.user)

            # TODO: Send receipt email to user

            return subscription

        except UserSubscription.DoesNotExist:
            pass

    @staticmethod
    def _map_stripe_status(stripe_status):
        """
        Map Stripe subscription status to our model status.
        """
        status_map = {
            'active': 'ACTIVE',
            'trialing': 'TRIALING',
            'past_due': 'PAST_DUE',
            'canceled': 'CANCELED',
            'unpaid': 'UNPAID',
        }
        return status_map.get(stripe_status, 'CANCELED')

    @staticmethod
    def check_usage_quota(user):
        """
        Check if user has remaining quota for generating descriptions.
        Returns (has_quota: bool, remaining: int or 'unlimited')
        """
        if not hasattr(user, 'subscription'):
            return False, 0

        subscription = user.subscription

        # Check if subscription is active
        if subscription.status not in ['ACTIVE', 'TRIALING']:
            return False, 0

        # Get current usage
        usage = Usage.get_or_create_current(user)

        # Check quota
        if subscription.plan.description_quota == -1:  # Unlimited
            return True, 'unlimited'

        remaining = subscription.plan.description_quota - usage.descriptions_generated

        return remaining > 0, remaining

    @staticmethod
    def increment_usage(user):
        """
        Increment description generation count for user.
        Returns True if successful, False if quota exceeded.
        Sends quota warning emails at 80%, 90%, and 100%.
        """
        has_quota, remaining = SubscriptionService.check_usage_quota(user)

        if not has_quota:
            return False

        # Get current usage and increment
        usage = Usage.get_or_create_current(user)
        usage.descriptions_generated += 1
        usage.save()

        # Check if we should send quota warning email
        if EMAIL_ENABLED and hasattr(user, 'subscription'):
            subscription = user.subscription
            quota = subscription.plan.description_quota

            if quota > 0:  # Not unlimited
                percentage = (usage.descriptions_generated / quota) * 100

                # Send warnings at 80%, 90%, and 100%
                if percentage >= 100 or percentage >= 90 or (percentage >= 80 and usage.descriptions_generated % 10 == 0):
                    try:
                        EmailService.send_quota_warning(user, usage, subscription)
                    except Exception as e:
                        print(f"Failed to send quota warning email: {e}")

        return True
