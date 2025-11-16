from django import forms
from .models import Listing


class ListingForm(forms.ModelForm):
    """
    Form for creating and editing listings.
    """

    # Override key_features to use a simple text field
    key_features_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Enter features separated by commas (e.g., Pool, Garage, Fireplace, Updated Kitchen)',
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
        }),
        label='Key Features',
        help_text='Separate multiple features with commas'
    )

    class Meta:
        model = Listing
        fields = [
            'property_type',
            'title',
            'address',
            'city',
            'state',
            'country',
            'zip_code',
            'price',
            'bedrooms',
            'bathrooms',
            'square_feet',
            'lot_size',
            'year_built',
            'tone',
            'target_audience',
            'additional_notes',
        ]

        widgets = {
            'property_type': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'title': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'e.g., Luxury Downtown Apartment'
            }),
            'address': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': '123 Main Street'
            }),
            'city': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'New York'
            }),
            'state': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'NY'
            }),
            'country': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': '10001'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': '500000'
            }),
            'bedrooms': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': '3'
            }),
            'bathrooms': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'step': '0.5',
                'placeholder': '2.5'
            }),
            'square_feet': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': '2000'
            }),
            'lot_size': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': '5000'
            }),
            'year_built': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': '2020'
            }),
            'tone': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'target_audience': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'additional_notes': forms.Textarea(attrs={
                'rows': 4,
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Any additional information you want to include in the description...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If editing an existing listing, populate key_features_text
        if self.instance and self.instance.pk and self.instance.key_features:
            self.fields['key_features_text'].initial = ', '.join(self.instance.key_features)

    def clean_key_features_text(self):
        """Convert comma-separated string to list"""
        text = self.cleaned_data.get('key_features_text', '')
        if text:
            # Split by comma and strip whitespace
            features = [f.strip() for f in text.split(',') if f.strip()]
            return features
        return []

    def save(self, commit=True):
        """Override save to handle key_features conversion"""
        instance = super().save(commit=False)

        # Convert key_features_text to JSON array
        features = self.clean_key_features_text()
        instance.key_features = features

        if commit:
            instance.save()

        return instance


class EditDescriptionForm(forms.ModelForm):
    """
    Form for editing the generated description.
    """

    class Meta:
        model = Listing
        fields = ['edited_description']

        widgets = {
            'edited_description': forms.Textarea(attrs={
                'rows': 10,
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 font-mono',
                'placeholder': 'Edit the generated description here...'
            }),
        }
