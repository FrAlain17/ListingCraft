"""
Admin-specific dashboard views for system monitoring and user management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta

from apps.accounts.decorators import admin_required
from apps.listings.models import Listing
from apps.subscriptions.models import SubscriptionPlan, UserSubscription, Usage

User = get_user_model()


@login_required
@admin_required
def admin_dashboard(request):
    """
    Main admin dashboard with system-wide statistics.
    """
    # User statistics
    total_users = User.objects.count()
    active_subscriptions = UserSubscription.objects.filter(
        status__in=['ACTIVE', 'TRIALING']
    ).count()

    # Recent signups (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_signups = User.objects.filter(date_joined__gte=week_ago).count()

    # Listing statistics
    total_listings = Listing.objects.count()
    listings_this_week = Listing.objects.filter(created_at__gte=week_ago).count()

    # Revenue statistics (approximate based on subscriptions)
    subscription_revenue = 0
    active_subs = UserSubscription.objects.filter(status__in=['ACTIVE', 'TRIALING']).select_related('plan')
    for sub in active_subs:
        subscription_revenue += float(sub.plan.price)

    # Usage statistics
    total_descriptions = Usage.objects.aggregate(total=Sum('descriptions_generated'))['total'] or 0
    descriptions_this_week = 0
    recent_usage = Usage.objects.filter(period_start__gte=week_ago)
    for usage in recent_usage:
        descriptions_this_week += usage.descriptions_generated

    # Subscription breakdown by plan
    subscription_breakdown = UserSubscription.objects.filter(
        status__in=['ACTIVE', 'TRIALING']
    ).values('plan__name').annotate(
        count=Count('id')
    ).order_by('-count')

    # Recent users
    recent_users = User.objects.order_by('-date_joined')[:10]

    # Recent listings
    recent_listings = Listing.objects.select_related('user').order_by('-created_at')[:10]

    # Property type distribution
    property_types = Listing.objects.values('property_type').annotate(
        count=Count('property_type')
    ).order_by('-count')[:5]

    context = {
        'total_users': total_users,
        'active_subscriptions': active_subscriptions,
        'recent_signups': recent_signups,
        'total_listings': total_listings,
        'listings_this_week': listings_this_week,
        'subscription_revenue': subscription_revenue,
        'total_descriptions': total_descriptions,
        'descriptions_this_week': descriptions_this_week,
        'subscription_breakdown': subscription_breakdown,
        'recent_users': recent_users,
        'recent_listings': recent_listings,
        'property_types': property_types,
    }

    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
@admin_required
def user_management(request):
    """
    User management view for admins.
    """
    # Get all users with their subscription info
    users = User.objects.all().select_related('profile').order_by('-date_joined')

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) |
            Q(profile__company_name__icontains=search_query)
        )

    # Filter by subscription status
    subscription_filter = request.GET.get('subscription')
    if subscription_filter == 'active':
        users = users.filter(subscription__status__in=['ACTIVE', 'TRIALING'])
    elif subscription_filter == 'inactive':
        users = users.filter(
            Q(subscription__isnull=True) |
            Q(subscription__status__in=['CANCELED', 'PAST_DUE', 'UNPAID'])
        )

    # Pagination-like limiting
    page = request.GET.get('page', 1)
    try:
        page = int(page)
    except ValueError:
        page = 1

    per_page = 20
    start = (page - 1) * per_page
    end = start + per_page

    users_page = users[start:end]
    has_next = users.count() > end
    has_prev = page > 1

    context = {
        'users': users_page,
        'search_query': search_query,
        'subscription_filter': subscription_filter,
        'page': page,
        'has_next': has_next,
        'has_prev': has_prev,
        'total_users': users.count(),
    }

    return render(request, 'dashboard/user_management.html', context)


@login_required
@admin_required
def user_detail(request, user_id):
    """
    Detailed view of a specific user.
    """
    user = get_object_or_404(User, id=user_id)

    # Get user's subscription
    subscription = None
    usage = None
    if hasattr(user, 'subscription'):
        subscription = user.subscription
        usage = Usage.get_or_create_current(user)

    # Get user's listings
    listings = Listing.objects.filter(user=user).order_by('-created_at')

    # Usage history
    usage_history = Usage.objects.filter(user=user).order_by('-period_start')[:6]

    # Total descriptions generated
    total_descriptions = Usage.objects.filter(user=user).aggregate(
        total=Sum('descriptions_generated')
    )['total'] or 0

    context = {
        'profile_user': user,
        'subscription': subscription,
        'usage': usage,
        'listings': listings,
        'usage_history': usage_history,
        'total_descriptions': total_descriptions,
    }

    return render(request, 'dashboard/user_detail.html', context)


@login_required
@admin_required
def analytics(request):
    """
    Analytics and reporting view.
    """
    # Date range setup
    today = timezone.now()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)

    # User growth
    users_by_day = []
    for i in range(30, -1, -1):
        date = today - timedelta(days=i)
        count = User.objects.filter(date_joined__date=date.date()).count()
        users_by_day.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })

    # Listing creation trend
    listings_by_day = []
    for i in range(30, -1, -1):
        date = today - timedelta(days=i)
        count = Listing.objects.filter(created_at__date=date.date()).count()
        listings_by_day.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })

    # Subscription statistics
    total_revenue = 0
    active_subs = UserSubscription.objects.filter(status__in=['ACTIVE', 'TRIALING']).select_related('plan')
    for sub in active_subs:
        total_revenue += float(sub.plan.price)

    monthly_recurring_revenue = total_revenue

    # Churn rate (simplified)
    canceled_this_month = UserSubscription.objects.filter(
        canceled_at__gte=last_30_days
    ).count()

    total_subs = UserSubscription.objects.filter(status__in=['ACTIVE', 'TRIALING']).count()
    churn_rate = (canceled_this_month / total_subs * 100) if total_subs > 0 else 0

    # Average descriptions per user
    avg_descriptions = Usage.objects.aggregate(
        avg=Avg('descriptions_generated')
    )['avg'] or 0

    # Top users by descriptions
    top_users = Usage.objects.values('user__email').annotate(
        total=Sum('descriptions_generated')
    ).order_by('-total')[:10]

    context = {
        'users_by_day': users_by_day,
        'listings_by_day': listings_by_day,
        'monthly_recurring_revenue': monthly_recurring_revenue,
        'churn_rate': round(churn_rate, 2),
        'avg_descriptions': round(avg_descriptions, 2),
        'top_users': top_users,
    }

    return render(request, 'dashboard/analytics.html', context)


@login_required
@admin_required
def subscription_management(request):
    """
    Manage subscription plans.
    """
    plans = SubscriptionPlan.objects.all().order_by('price')

    # Get subscription counts for each plan
    plan_stats = []
    for plan in plans:
        active_count = UserSubscription.objects.filter(
            plan=plan,
            status__in=['ACTIVE', 'TRIALING']
        ).count()

        total_count = UserSubscription.objects.filter(plan=plan).count()

        plan_stats.append({
            'plan': plan,
            'active_subscriptions': active_count,
            'total_subscriptions': total_count,
            'revenue': float(plan.price) * active_count,
        })

    context = {
        'plan_stats': plan_stats,
    }

    return render(request, 'dashboard/subscription_management.html', context)
