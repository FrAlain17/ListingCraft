"""
Service layer for AI description generation using DeepSeek API.
"""
import requests
from django.conf import settings
from .models import Listing


class DeepSeekService:
    """
    Service class for interacting with DeepSeek API to generate property descriptions.
    """

    API_URL = "https://api.deepseek.com/v1/chat/completions"

    @staticmethod
    def generate_description(listing):
        """
        Generate a property description using DeepSeek API.

        Args:
            listing: Listing model instance with property details

        Returns:
            str: Generated description or error message
        """
        # Build the prompt based on listing details
        prompt = DeepSeekService._build_prompt(listing)

        # Prepare API request
        headers = {
            "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": DeepSeekService._get_system_prompt(listing.tone)
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500,
        }

        try:
            response = requests.post(
                DeepSeekService.API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            # Extract the generated description
            description = data['choices'][0]['message']['content'].strip()

            # Update listing
            listing.generated_description = description
            listing.generation_count += 1
            listing.save()

            return description

        except requests.exceptions.RequestException as e:
            error_msg = f"API Error: {str(e)}"
            if hasattr(e.response, 'text'):
                error_msg += f" - {e.response.text}"
            return error_msg

        except (KeyError, IndexError) as e:
            return f"Error parsing API response: {str(e)}"

    @staticmethod
    def _get_system_prompt(tone):
        """
        Get system prompt based on selected tone.
        """
        tone_prompts = {
            'PROFESSIONAL': (
                "You are a professional real estate copywriter. Generate compelling, "
                "accurate, and professional property descriptions that highlight key features "
                "and benefits. Use industry-standard terminology and maintain a professional tone."
            ),
            'LUXURY': (
                "You are a luxury real estate copywriter. Create elegant, sophisticated "
                "descriptions that evoke exclusivity and prestige. Use rich, descriptive language "
                "that appeals to high-end buyers. Emphasize luxury features, quality, and lifestyle."
            ),
            'FRIENDLY': (
                "You are a friendly and approachable real estate copywriter. Write warm, "
                "inviting descriptions that make potential buyers feel at home. Use conversational "
                "language while remaining informative and honest."
            ),
            'CONCISE': (
                "You are a concise real estate copywriter. Create brief, punchy descriptions "
                "that get straight to the point. Highlight only the most important features "
                "in a clear, direct manner. Keep descriptions under 150 words."
            ),
            'DETAILED': (
                "You are a detailed real estate copywriter. Provide comprehensive, thorough "
                "descriptions that cover all aspects of the property. Include specific details "
                "about features, layout, and amenities. Paint a complete picture for buyers."
            ),
        }
        return tone_prompts.get(tone, tone_prompts['PROFESSIONAL'])

    @staticmethod
    def _build_prompt(listing):
        """
        Build the user prompt with all property details.
        """
        prompt_parts = [
            f"Generate a compelling property description for the following {listing.get_property_type_display().lower()}:",
            ""
        ]

        # Basic info
        prompt_parts.append(f"**Property Type:** {listing.get_property_type_display()}")
        prompt_parts.append(f"**Location:** {listing.get_location_display()}")
        prompt_parts.append(f"**Price:** ${listing.price:,.2f}")

        # Property specs
        if listing.bedrooms:
            prompt_parts.append(f"**Bedrooms:** {listing.bedrooms}")
        if listing.bathrooms:
            prompt_parts.append(f"**Bathrooms:** {listing.bathrooms}")
        if listing.square_feet:
            prompt_parts.append(f"**Square Footage:** {listing.square_feet:,} sqft")
        if listing.lot_size:
            prompt_parts.append(f"**Lot Size:** {listing.lot_size:,} sqft")
        if listing.year_built:
            prompt_parts.append(f"**Year Built:** {listing.year_built}")

        # Key features
        if listing.key_features:
            features_str = ", ".join(listing.key_features)
            prompt_parts.append(f"**Key Features:** {features_str}")

        # Target audience
        prompt_parts.append(f"**Target Audience:** {listing.get_target_audience_display()}")

        # Additional notes
        if listing.additional_notes:
            prompt_parts.append(f"**Additional Information:** {listing.additional_notes}")

        prompt_parts.append("")
        prompt_parts.append(
            "Create an SEO-optimized description that highlights the property's best features "
            "and appeals to the target audience. Focus on benefits and lifestyle. "
            "Do not include a title or heading - just the description text."
        )

        return "\n".join(prompt_parts)


class ListingService:
    """
    Service class for listing-related business logic.
    """

    @staticmethod
    def create_listing_with_description(user, listing_data):
        """
        Create a new listing and generate its description.

        Args:
            user: User instance
            listing_data: Dictionary of listing fields

        Returns:
            tuple: (listing, success, message)
        """
        from apps.subscriptions.services import SubscriptionService

        # Check quota
        has_quota, remaining = SubscriptionService.check_usage_quota(user)

        if not has_quota:
            return None, False, "You have exceeded your monthly description quota. Please upgrade your plan or wait for your quota to reset."

        try:
            # Create listing
            listing = Listing.objects.create(user=user, **listing_data)

            # Generate description
            description = DeepSeekService.generate_description(listing)

            if description.startswith("API Error") or description.startswith("Error"):
                return listing, False, f"Listing created but description generation failed: {description}"

            # Increment usage
            SubscriptionService.increment_usage(user)

            return listing, True, "Listing created and description generated successfully!"

        except Exception as e:
            return None, False, f"Error creating listing: {str(e)}"

    @staticmethod
    def regenerate_description(listing):
        """
        Regenerate description for an existing listing.

        Args:
            listing: Listing instance

        Returns:
            tuple: (success, message)
        """
        from apps.subscriptions.services import SubscriptionService

        # Check quota
        has_quota, remaining = SubscriptionService.check_usage_quota(listing.user)

        if not has_quota:
            return False, "You have exceeded your monthly description quota. Please upgrade your plan or wait for your quota to reset."

        try:
            # Generate description
            description = DeepSeekService.generate_description(listing)

            if description.startswith("API Error") or description.startswith("Error"):
                return False, f"Description generation failed: {description}"

            # Increment usage
            SubscriptionService.increment_usage(listing.user)

            return True, "Description regenerated successfully!"

        except Exception as e:
            return False, f"Error regenerating description: {str(e)}"
