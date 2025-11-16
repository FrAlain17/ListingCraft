from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    # Plan selection
    path('plans/', views.plans_view, name='plans'),

    # Checkout
    path('checkout/<int:plan_id>/', views.create_checkout_session, name='checkout'),
    path('success/', views.subscription_success, name='success'),
    path('cancel/', views.subscription_cancel, name='cancel'),

    # Subscription management
    path('manage/', views.manage_subscription, name='manage'),
    path('billing-portal/', views.create_billing_portal_session, name='billing_portal'),
    path('cancel-subscription/', views.cancel_subscription, name='cancel_subscription'),

    # Webhook
    path('webhook/', views.stripe_webhook, name='webhook'),
]
