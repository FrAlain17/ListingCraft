from django.contrib import admin
from .models import Listing


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'user',
        'property_type',
        'city',
        'price',
        'get_specs_display',
        'is_favorite',
        'generation_count',
        'created_at',
    ]
    list_filter = [
        'property_type',
        'tone',
        'target_audience',
        'is_favorite',
        'created_at',
    ]
    search_fields = [
        'title',
        'city',
        'state',
        'address',
        'user__email',
        'generated_description',
    ]
    readonly_fields = ['slug', 'created_at', 'updated_at', 'generation_count']

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Property Info', {
            'fields': (
                'property_type',
                'title',
                'price',
            )
        }),
        ('Location', {
            'fields': (
                'address',
                'city',
                'state',
                'country',
                'zip_code',
            )
        }),
        ('Property Details', {
            'fields': (
                'bedrooms',
                'bathrooms',
                'square_feet',
                'lot_size',
                'year_built',
                'key_features',
            )
        }),
        ('Generation Settings', {
            'fields': (
                'tone',
                'target_audience',
                'additional_notes',
            )
        }),
        ('Generated Content', {
            'fields': (
                'generated_description',
                'edited_description',
            )
        }),
        ('Metadata', {
            'fields': (
                'slug',
                'is_favorite',
                'generation_count',
                'created_at',
                'updated_at',
            )
        }),
    )

    def get_specs_display(self, obj):
        """Display property specs in list view"""
        return obj.get_property_summary()
    get_specs_display.short_description = 'Specs'
