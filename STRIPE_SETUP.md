# Stripe Integration Setup Guide

This guide will help you set up Stripe for ListingCraft's subscription system.

## Prerequisites

- Stripe account (sign up at https://stripe.com)
- Access to Stripe Dashboard

## Step 1: Get Stripe API Keys

1. Log in to your Stripe Dashboard
2. Navigate to **Developers** → **API keys**
3. Copy your keys:
   - **Test Mode**: Publishable key and Secret key (starts with `pk_test_` and `sk_test_`)
   - **Live Mode**: Publishable key and Secret key (starts with `pk_live_` and `sk_live_`)

4. Add these to your `.env` file:
   ```bash
   # Stripe Configuration
   STRIPE_LIVE_MODE=False  # Set to True for production

   # Test Keys (for development)
   STRIPE_TEST_PUBLIC_KEY=pk_test_your_key_here
   STRIPE_TEST_SECRET_KEY=sk_test_your_key_here

   # Live Keys (for production)
   STRIPE_LIVE_PUBLIC_KEY=pk_live_your_key_here
   STRIPE_LIVE_SECRET_KEY=sk_live_your_key_here
   ```

## Step 2: Create Products and Prices in Stripe

You need to create 3 products in Stripe Dashboard, one for each plan:

### Basic Plan
1. Go to **Products** → **Add Product**
2. Fill in:
   - **Name**: Basic
   - **Description**: Perfect for individual agents
   - **Pricing**: $29.00 / month (Recurring)
   - **Billing period**: Monthly
3. Click **Save product**
4. Copy the **Price ID** (starts with `price_`) and **Product ID** (starts with `prod_`)

### Pro Plan
1. Create another product:
   - **Name**: Pro
   - **Description**: Great for small agencies
   - **Pricing**: $79.00 / month (Recurring)
   - **Billing period**: Monthly
2. Copy the **Price ID** and **Product ID**

### Agency Plan
1. Create another product:
   - **Name**: Agency
   - **Description**: For large agencies and teams
   - **Pricing**: $199.00 / month (Recurring)
   - **Billing period**: Monthly
2. Copy the **Price ID** and **Product ID**

## Step 3: Update Database with Stripe IDs

After creating products in Stripe, update the subscription plans in your database:

1. Access Django Admin: http://localhost:8000/admin/
2. Navigate to **Subscriptions** → **Subscription Plans**
3. For each plan, update:
   - **Stripe Price ID**: (the `price_` ID from Stripe)
   - **Stripe Product ID**: (the `prod_` ID from Stripe)
4. Save each plan

Alternatively, you can update directly via Django shell:

```python
python manage.py shell

from apps.subscriptions.models import SubscriptionPlan

# Update Basic Plan
basic = SubscriptionPlan.objects.get(plan_type='BASIC')
basic.stripe_price_id = 'price_xxxxxxxxxxxxx'
basic.stripe_product_id = 'prod_xxxxxxxxxxxxx'
basic.save()

# Update Pro Plan
pro = SubscriptionPlan.objects.get(plan_type='PRO')
pro.stripe_price_id = 'price_xxxxxxxxxxxxx'
pro.stripe_product_id = 'prod_xxxxxxxxxxxxx'
pro.save()

# Update Agency Plan
agency = SubscriptionPlan.objects.get(plan_type='AGENCY')
agency.stripe_price_id = 'price_xxxxxxxxxxxxx'
agency.stripe_product_id = 'prod_xxxxxxxxxxxxx'
agency.save()
```

## Step 4: Set Up Webhook Endpoint

Webhooks allow Stripe to notify your app about subscription events (payments, cancellations, etc.).

### For Development (using Stripe CLI)

1. Install Stripe CLI: https://stripe.com/docs/stripe-cli
2. Login to Stripe CLI:
   ```bash
   stripe login
   ```
3. Forward webhooks to your local server:
   ```bash
   stripe listen --forward-to localhost:8000/subscriptions/webhook/
   ```
4. Copy the webhook signing secret (starts with `whsec_`) and add to `.env`:
   ```bash
   DJSTRIPE_WEBHOOK_SECRET=whsec_your_secret_here
   ```

### For Production

1. Go to **Developers** → **Webhooks** in Stripe Dashboard
2. Click **Add endpoint**
3. Enter your webhook URL: `https://yourdomain.com/subscriptions/webhook/`
4. Select events to listen for:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_failed`
   - `invoice.payment_succeeded`
5. Click **Add endpoint**
6. Copy the **Signing secret** and add to your production `.env`:
   ```bash
   DJSTRIPE_WEBHOOK_SECRET=whsec_your_production_secret_here
   ```

## Step 5: Configure Customer Portal (Optional)

The Customer Portal allows users to manage their subscriptions, update payment methods, etc.

1. Go to **Settings** → **Billing** → **Customer portal** in Stripe Dashboard
2. Enable the portal and configure:
   - Allow customers to update payment methods: ✓
   - Allow customers to cancel subscriptions: ✓
   - Allow customers to switch plans: ✓ (optional)
3. Save settings

## Step 6: Test the Integration

1. Start your development server:
   ```bash
   python manage.py runserver
   ```

2. In another terminal, start Stripe webhook forwarding:
   ```bash
   stripe listen --forward-to localhost:8000/subscriptions/webhook/
   ```

3. Test the flow:
   - Sign up for a new account
   - Go to subscription plans: http://localhost:8000/subscriptions/plans/
   - Click "Get Started" on a plan
   - Use Stripe test card: `4242 4242 4242 4242`
   - Any future date for expiry
   - Any 3-digit CVC
   - Complete checkout
   - Verify subscription is created in Django Admin and Stripe Dashboard

## Test Card Numbers

Stripe provides test cards for different scenarios:

- **Success**: `4242 4242 4242 4242`
- **Requires authentication**: `4000 0025 0000 3155`
- **Declined**: `4000 0000 0000 9995`
- **Insufficient funds**: `4000 0000 0000 9995`

More test cards: https://stripe.com/docs/testing

## Troubleshooting

### Webhook not receiving events
- Ensure Stripe CLI is running (`stripe listen`)
- Check webhook secret matches in `.env`
- Verify webhook URL is correct

### Checkout session fails
- Verify Stripe Price IDs are correct in database
- Check Stripe API keys are valid
- Look for errors in Django logs

### Subscription not created after payment
- Check webhook logs in Stripe Dashboard
- Verify webhook endpoint is accessible
- Check Django logs for errors in webhook handler

## Going Live

Before going live:

1. Switch to live mode:
   ```bash
   STRIPE_LIVE_MODE=True
   ```

2. Use live API keys in `.env`

3. Set up production webhook endpoint in Stripe Dashboard

4. Test thoroughly with small real payments first

5. Enable Stripe Radar for fraud prevention (recommended)

6. Review Stripe best practices: https://stripe.com/docs/security/best-practices

## Support

- Stripe Documentation: https://stripe.com/docs
- Stripe Support: https://support.stripe.com
- dj-stripe Documentation: https://dj-stripe.readthedocs.io
