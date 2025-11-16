from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from datetime import timedelta
from django.utils import timezone

from apps.accounts.decorators import client_required
from apps.listings.models import Listing
from apps.subscriptions.models import Usage


@login_required
@client_required
def dashboard_overview(request):
    """
    Main dashboard view with stats and recent listings.
    """
    user = request.user

    # Get subscription info
    subscription = None
    usage = None
    quota_percentage = 0
    quota_remaining = 0

    if hasattr(user, 'subscription'):
        subscription = user.subscription
        usage = Usage.get_or_create_current(user)

        # Calculate quota usage
        if subscription.plan.description_quota == -1:  # Unlimited
            quota_percentage = 0
            quota_remaining = 'Unlimited'
        else:
            quota_percentage = (usage.descriptions_generated / subscription.plan.description_quota) * 100
            quota_remaining = subscription.plan.description_quota - usage.descriptions_generated

    # Get listing stats
    total_listings = Listing.objects.filter(user=user).count()
    favorite_listings = Listing.objects.filter(user=user, is_favorite=True).count()

    # Recent listings (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_listings_count = Listing.objects.filter(
        user=user,
        created_at__gte=week_ago
    ).count()

    # Get recent listings
    recent_listings = Listing.objects.filter(user=user)[:5]

    # Property type breakdown
    property_type_stats = Listing.objects.filter(user=user).values('property_type').annotate(
        count=Count('property_type')
    ).order_by('-count')

    context = {
        'subscription': subscription,
        'usage': usage,
        'quota_percentage': quota_percentage,
        'quota_remaining': quota_remaining,
        'total_listings': total_listings,
        'favorite_listings': favorite_listings,
        'recent_listings_count': recent_listings_count,
        'recent_listings': recent_listings,
        'property_type_stats': property_type_stats,
    }

    return render(request, 'dashboard/overview.html', context)
