from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription, Usage


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'price', 'description_quota', 'is_active', 'created_at')
    list_filter = ('plan_type', 'is_active')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'plan_type', 'description', 'is_active')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_price_id', 'stripe_product_id')
        }),
        ('Pricing & Limits', {
            'fields': ('price', 'description_quota')
        }),
        ('Features', {
            'fields': ('features',),
            'description': 'Enter features as a JSON list, e.g., ["Feature 1", "Feature 2"]'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'plan', 'status', 'current_period_end', 'cancel_at_period_end', 'created_at')
    list_filter = ('status', 'plan', 'cancel_at_period_end')
    search_fields = ('user__email', 'stripe_subscription_id', 'stripe_customer_id')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user',)

    fieldsets = (
        ('User & Plan', {
            'fields': ('user', 'plan')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_subscription_id', 'stripe_customer_id')
        }),
        ('Status', {
            'fields': ('status', 'cancel_at_period_end', 'canceled_at')
        }),
        ('Billing Period', {
            'fields': ('current_period_start', 'current_period_end', 'trial_end')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'


@admin.register(Usage)
class UsageAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'descriptions_generated', 'get_quota', 'period_start', 'period_end', 'is_current_period')
    list_filter = ('period_start',)
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at', 'is_current_period')
    raw_id_fields = ('user',)
    date_hierarchy = 'period_start'

    fieldsets = (
        ('User & Usage', {
            'fields': ('user', 'descriptions_generated')
        }),
        ('Period', {
            'fields': ('period_start', 'period_end', 'is_current_period')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'

    def get_quota(self, obj):
        remaining = obj.get_remaining_quota()
        if remaining == float('inf'):
            return 'Unlimited'
        try:
            total = obj.user.subscription.plan.description_quota
            return f"{obj.descriptions_generated}/{total}"
        except:
            return '-'
    get_quota.short_description = 'Usage/Quota'
