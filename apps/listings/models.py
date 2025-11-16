from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


class Listing(models.Model):
    """
    Model to store property listings and generated descriptions.
    """

    class PropertyType(models.TextChoices):
        APARTMENT = 'APARTMENT', 'Apartment'
        HOUSE = 'HOUSE', 'House'
        VILLA = 'VILLA', 'Villa'
        STUDIO = 'STUDIO', 'Studio'
        TOWNHOUSE = 'TOWNHOUSE', 'Townhouse'
        PENTHOUSE = 'PENTHOUSE', 'Penthouse'
        COMMERCIAL = 'COMMERCIAL', 'Commercial'
        LAND = 'LAND', 'Land'
        OTHER = 'OTHER', 'Other'

    class ToneType(models.TextChoices):
        PROFESSIONAL = 'PROFESSIONAL', 'Professional'
        LUXURY = 'LUXURY', 'Luxury'
        FRIENDLY = 'FRIENDLY', 'Friendly'
        CONCISE = 'CONCISE', 'Concise'
        DETAILED = 'DETAILED', 'Detailed'

    class TargetAudience(models.TextChoices):
        FAMILIES = 'FAMILIES', 'Families'
        YOUNG_PROFESSIONALS = 'YOUNG_PROFESSIONALS', 'Young Professionals'
        RETIREES = 'RETIREES', 'Retirees'
        INVESTORS = 'INVESTORS', 'Investors'
        LUXURY_BUYERS = 'LUXURY_BUYERS', 'Luxury Buyers'
        FIRST_TIME_BUYERS = 'FIRST_TIME_BUYERS', 'First-time Buyers'
        GENERAL = 'GENERAL', 'General'

    # User relationship
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')

    # Property basic info
    property_type = models.CharField(max_length=20, choices=PropertyType.choices)
    title = models.CharField(max_length=255, help_text='Internal title for your reference')

    # Location
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='USA')
    zip_code = models.CharField(max_length=20, blank=True)

    # Property details
    price = models.DecimalField(max_digits=12, decimal_places=2, help_text='Property price')
    bedrooms = models.IntegerField(null=True, blank=True)
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    square_feet = models.IntegerField(null=True, blank=True, help_text='Total square footage')
    lot_size = models.IntegerField(null=True, blank=True, help_text='Lot size in square feet')
    year_built = models.IntegerField(null=True, blank=True)

    # Features (stored as JSON array)
    key_features = models.JSONField(
        default=list,
        blank=True,
        help_text='List of key features (e.g., pool, garage, fireplace)'
    )

    # Description generation inputs
    tone = models.CharField(
        max_length=20,
        choices=ToneType.choices,
        default=ToneType.PROFESSIONAL
    )
    target_audience = models.CharField(
        max_length=30,
        choices=TargetAudience.choices,
        default=TargetAudience.GENERAL
    )
    additional_notes = models.TextField(
        blank=True,
        help_text='Any additional information to include in the description'
    )

    # Generated content
    generated_description = models.TextField(
        blank=True,
        help_text='AI-generated property description'
    )
    edited_description = models.TextField(
        blank=True,
        help_text='User-edited version of the description'
    )

    # Metadata
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    is_favorite = models.BooleanField(default=False)
    generation_count = models.IntegerField(
        default=0,
        help_text='Number of times description was regenerated'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Listing'
        verbose_name_plural = 'Listings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_favorite']),
        ]

    def __str__(self):
        return f"{self.title} - {self.city}"

    def save(self, *args, **kwargs):
        """Generate slug if not provided"""
        if not self.slug:
            base_slug = slugify(f"{self.title}-{self.city}")
            slug = base_slug
            counter = 1
            while Listing.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_final_description(self):
        """Get the final description (edited if available, otherwise generated)"""
        return self.edited_description or self.generated_description

    def get_location_display(self):
        """Return formatted location string"""
        parts = [self.city]
        if self.state:
            parts.append(self.state)
        if self.country and self.country != 'USA':
            parts.append(self.country)
        return ', '.join(parts)

    def get_property_summary(self):
        """Return a summary of property specs"""
        summary_parts = []

        if self.bedrooms:
            summary_parts.append(f"{self.bedrooms} bed")
        if self.bathrooms:
            summary_parts.append(f"{self.bathrooms} bath")
        if self.square_feet:
            summary_parts.append(f"{self.square_feet:,} sqft")

        return ' | '.join(summary_parts) if summary_parts else 'No specs available'
