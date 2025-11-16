"""
Email notification service for user-related emails.
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


class EmailService:
    """
    Service for sending email notifications.
    """

    @staticmethod
    def send_welcome_email(user):
        """
        Send welcome email to new users.
        """
        subject = 'Welcome to ListingCraft!'

        html_message = render_to_string('emails/welcome.html', {
            'user': user,
            'login_url': f"{settings.SITE_URL}/accounts/login/" if hasattr(settings, 'SITE_URL') else '/accounts/login/',
        })

        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

    @staticmethod
    def send_subscription_confirmation(user, subscription):
        """
        Send email when user subscribes to a plan.
        """
        subject = f'Subscription Confirmed - {subscription.plan.name} Plan'

        html_message = render_to_string('emails/subscription_confirmed.html', {
            'user': user,
            'subscription': subscription,
            'dashboard_url': f"{settings.SITE_URL}/dashboard/" if hasattr(settings, 'SITE_URL') else '/dashboard/',
        })

        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

    @staticmethod
    def send_subscription_cancelled(user, subscription):
        """
        Send email when subscription is cancelled.
        """
        subject = 'Subscription Cancelled - ListingCraft'

        html_message = render_to_string('emails/subscription_cancelled.html', {
            'user': user,
            'subscription': subscription,
            'plans_url': f"{settings.SITE_URL}/subscriptions/plans/" if hasattr(settings, 'SITE_URL') else '/subscriptions/plans/',
        })

        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

    @staticmethod
    def send_payment_failed(user, subscription):
        """
        Send email when payment fails.
        """
        subject = 'Payment Failed - Action Required'

        html_message = render_to_string('emails/payment_failed.html', {
            'user': user,
            'subscription': subscription,
            'billing_url': f"{settings.SITE_URL}/subscriptions/billing-portal/" if hasattr(settings, 'SITE_URL') else '/subscriptions/billing-portal/',
        })

        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

    @staticmethod
    def send_quota_warning(user, usage, subscription):
        """
        Send email when user is approaching quota limit (80%, 90%, 100%).
        """
        quota = subscription.plan.description_quota
        percentage = (usage.descriptions_generated / quota) * 100 if quota > 0 else 0

        if percentage >= 100:
            subject = 'Quota Limit Reached - Upgrade Your Plan'
        elif percentage >= 90:
            subject = 'Quota Almost Exhausted - 90% Used'
        else:
            subject = 'Quota Warning - 80% Used'

        html_message = render_to_string('emails/quota_warning.html', {
            'user': user,
            'usage': usage,
            'subscription': subscription,
            'percentage': round(percentage, 1),
            'remaining': quota - usage.descriptions_generated,
            'plans_url': f"{settings.SITE_URL}/subscriptions/plans/" if hasattr(settings, 'SITE_URL') else '/subscriptions/plans/',
        })

        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

    @staticmethod
    def send_trial_ending_soon(user, subscription):
        """
        Send email 3 days before trial ends.
        """
        subject = 'Your Trial Ends Soon - ListingCraft'

        html_message = render_to_string('emails/trial_ending.html', {
            'user': user,
            'subscription': subscription,
            'billing_url': f"{settings.SITE_URL}/subscriptions/billing-portal/" if hasattr(settings, 'SITE_URL') else '/subscriptions/billing-portal/',
        })

        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

    @staticmethod
    def send_receipt(user, subscription, amount):
        """
        Send payment receipt email.
        """
        subject = f'Payment Receipt - ${amount}'

        html_message = render_to_string('emails/receipt.html', {
            'user': user,
            'subscription': subscription,
            'amount': amount,
            'manage_url': f"{settings.SITE_URL}/subscriptions/manage/" if hasattr(settings, 'SITE_URL') else '/subscriptions/manage/',
        })

        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
