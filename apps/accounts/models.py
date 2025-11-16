from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Extended user profile for ListingCraft users.
    """

    class Role(models.TextChoices):
        CLIENT = 'CLIENT', 'Client'
        ADMIN = 'ADMIN', 'Admin'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CLIENT,
        help_text='User role in the system'
    )
    company_name = models.CharField(max_length=255, blank=True, help_text='Company or agency name')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} ({self.get_role_display()})"

    @property
    def is_client(self):
        """Check if user is a client."""
        return self.role == self.Role.CLIENT

    @property
    def is_admin_user(self):
        """Check if user is an admin (different from Django staff)."""
        return self.role == self.Role.ADMIN


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile when a User is created.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the UserProfile when the User is saved.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
