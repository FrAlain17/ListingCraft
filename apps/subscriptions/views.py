from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse
import stripe

from .models import SubscriptionPlan, UserSubscription


stripe.api_key = settings.STRIPE_TEST_SECRET_KEY if not settings.STRIPE_LIVE_MODE else settings.STRIPE_LIVE_SECRET_KEY


@login_required
def plans_view(request):
    """
    Display all available subscription plans.
    """
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')

    # Get user's current subscription if exists
    current_subscription = None
    if hasattr(request.user, 'subscription'):
        current_subscription = request.user.subscription

    context = {
        'plans': plans,
        'current_subscription': current_subscription,
    }
    return render(request, 'subscriptions/plans.html', context)


@login_required
def create_checkout_session(request, plan_id):
    """
    Create a Stripe Checkout session for the selected plan.
    """
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)

    # Check if user already has an active subscription
    if hasattr(request.user, 'subscription') and request.user.subscription.status in ['ACTIVE', 'TRIALING']:
        messages.warning(request, 'You already have an active subscription. Please cancel it before subscribing to a new plan.')
        return redirect('subscriptions:plans')

    try:
        # Create or get Stripe customer
        if hasattr(request.user, 'subscription') and request.user.subscription.stripe_customer_id:
            customer_id = request.user.subscription.stripe_customer_id
        else:
            customer = stripe.Customer.create(
                email=request.user.email,
                metadata={
                    'user_id': request.user.id,
                }
            )
            customer_id = customer.id

        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': plan.stripe_price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.build_absolute_uri(reverse('subscriptions:success')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('subscriptions:cancel')),
            metadata={
                'user_id': request.user.id,
                'plan_id': plan.id,
            },
            subscription_data={
                'trial_period_days': 14,  # 14-day free trial
                'metadata': {
                    'user_id': request.user.id,
                    'plan_id': plan.id,
                }
            }
        )

        return redirect(checkout_session.url)

    except Exception as e:
        messages.error(request, f'Error creating checkout session: {str(e)}')
        return redirect('subscriptions:plans')


@login_required
def subscription_success(request):
    """
    Handle successful subscription creation.
    """
    session_id = request.GET.get('session_id')

    if session_id:
        try:
            # Retrieve the session to verify it was successful
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == 'paid' or session.status == 'complete':
                messages.success(request, 'Subscription successful! Welcome to your 14-day free trial.')
            else:
                messages.info(request, 'Your subscription is being processed.')

        except Exception as e:
            messages.warning(request, 'Subscription created, but there was an error retrieving details.')

    return render(request, 'subscriptions/success.html')


@login_required
def subscription_cancel(request):
    """
    Handle cancelled checkout.
    """
    messages.info(request, 'Checkout cancelled. You can subscribe anytime.')
    return render(request, 'subscriptions/cancel.html')


@login_required
def manage_subscription(request):
    """
    Display subscription management page with usage stats.
    """
    if not hasattr(request.user, 'subscription'):
        messages.info(request, 'You don\'t have an active subscription. Choose a plan to get started.')
        return redirect('subscriptions:plans')

    subscription = request.user.subscription

    # Get current usage
    from .models import Usage
    usage = Usage.get_or_create_current(request.user)

    # Calculate usage percentage
    if subscription.plan.description_quota == -1:  # Unlimited
        usage_percentage = 0
        quota_remaining = 'Unlimited'
    else:
        usage_percentage = (usage.descriptions_generated / subscription.plan.description_quota) * 100
        quota_remaining = subscription.plan.description_quota - usage.descriptions_generated

    context = {
        'subscription': subscription,
        'usage': usage,
        'usage_percentage': usage_percentage,
        'quota_remaining': quota_remaining,
    }
    return render(request, 'subscriptions/manage.html', context)


@login_required
def create_billing_portal_session(request):
    """
    Create a Stripe Customer Portal session for subscription management.
    """
    if not hasattr(request.user, 'subscription') or not request.user.subscription.stripe_customer_id:
        messages.error(request, 'No subscription found.')
        return redirect('subscriptions:plans')

    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=request.user.subscription.stripe_customer_id,
            return_url=request.build_absolute_uri(reverse('subscriptions:manage')),
        )
        return redirect(portal_session.url)

    except Exception as e:
        messages.error(request, f'Error creating billing portal session: {str(e)}')
        return redirect('subscriptions:manage')


@login_required
@require_POST
def cancel_subscription(request):
    """
    Cancel user's subscription at period end.
    """
    if not hasattr(request.user, 'subscription'):
        messages.error(request, 'No subscription found.')
        return redirect('subscriptions:plans')

    subscription = request.user.subscription

    if not subscription.stripe_subscription_id:
        messages.error(request, 'Invalid subscription.')
        return redirect('subscriptions:manage')

    try:
        # Cancel at period end
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True
        )

        # Update local subscription
        subscription.cancel_at_period_end = True
        subscription.save()

        messages.success(request, 'Your subscription will be cancelled at the end of the current billing period.')
        return redirect('subscriptions:manage')

    except Exception as e:
        messages.error(request, f'Error cancelling subscription: {str(e)}')
        return redirect('subscriptions:manage')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhooks for subscription events.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = settings.DJSTRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    from .services import SubscriptionService

    event_type = event['type']
    data = event['data']['object']

    try:
        if event_type == 'checkout.session.completed':
            SubscriptionService.handle_checkout_session_completed(data)

        elif event_type == 'customer.subscription.updated':
            SubscriptionService.handle_subscription_updated(data)

        elif event_type == 'customer.subscription.deleted':
            SubscriptionService.handle_subscription_deleted(data)

        elif event_type == 'invoice.payment_failed':
            SubscriptionService.handle_payment_failed(data)

        elif event_type == 'invoice.payment_succeeded':
            SubscriptionService.handle_payment_succeeded(data)

        return JsonResponse({'status': 'success'})

    except Exception as e:
        print(f'Webhook error: {str(e)}')
        return HttpResponse(status=500)
