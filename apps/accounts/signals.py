"""
Signal handlers for account-related events.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

# Import email service
try:
    from .email_service import EmailService
    EMAIL_ENABLED = True
except ImportError:
    EMAIL_ENABLED = False


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create UserProfile when a new User is created.
    Also send welcome email.
    """
    if created:
        # Create profile if it doesn't exist
        if not hasattr(instance, 'profile'):
            UserProfile.objects.create(user=instance)

        # Send welcome email
        if EMAIL_ENABLED:
            try:
                EmailService.send_welcome_email(instance)
            except Exception as e:
                # Log error but don't fail user creation
                print(f"Failed to send welcome email: {e}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save UserProfile when User is saved (if profile exists).
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
