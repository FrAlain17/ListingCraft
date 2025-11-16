# ListingCraft - Project Plan & Task Checklist

**App Name:** ListingCraft
**Domain:** https://listingcraft.online/
**Type:** Django SaaS - Real Estate Listing Description Generator

---

## Tech Stack

- **Backend:** Django 5.x + Django ORM
- **Database:** SQLite (development) → PostgreSQL-ready structure (production)
- **Frontend:** Django Templates + Tailwind CSS (responsive, single adaptive view)
- **Admin:** Django Admin + django-unfold (modern Tailwind UI)
- **Payments:** Stripe (via dj-stripe)
- **Email:** Resend API (via django-anymail) + console backend (development)
- **AI API:** DeepSeek API for description generation
- **Background Tasks:** Celery + Redis
- **Deployment:** Docker + Coolify

---

## Project Structure

```
listingcraft/
├── config/                          # Project configuration
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                 # Common settings
│   │   ├── dev.py                  # Development settings
│   │   └── prod.py                 # Production settings
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                            # Django apps
│   ├── __init__.py
│   ├── accounts/                   # User authentication & profiles
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   └── admin.py
│   ├── landing/                    # Marketing/landing pages
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/
│   ├── dashboard/                  # Client dashboard
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/
│   ├── subscriptions/              # Subscription & payment logic
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── services.py
│   ├── listings/                   # Listing generation & management
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   ├── services.py            # DeepSeek API integration
│   │   └── admin.py
│   └── core/                       # Shared utilities & base models
│       ├── models.py              # Base models (TimestampedModel, etc.)
│       ├── utils.py
│       ├── middleware.py
│       └── context_processors.py
│
├── static/                          # Static files
│   ├── css/
│   ├── js/
│   ├── images/
│   └── theme/                      # django-tailwind theme app
│
├── templates/                       # Global templates
│   ├── base.html
│   ├── components/                 # Reusable components
│   │   ├── navbar.html
│   │   ├── footer.html
│   │   └── alerts.html
│   └── emails/                     # Email templates
│       ├── welcome.html
│       ├── password_reset.html
│       └── subscription_update.html
│
├── media/                           # User-uploaded files
├── docker/                          # Docker configuration
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   └── nginx/
│       └── nginx.conf
│
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
│
├── .env.example
├── .gitignore
├── manage.py
├── README.md
└── PLAN.md (this file)
```

---

## Complete Task Checklist

### Phase 1: Project Foundation ⏳

- [ ] **1.1** Create Django project structure
  - [ ] Create `config/` directory with settings split
  - [ ] Create `apps/` directory for all Django apps
  - [ ] Set up `requirements/` directory (base.txt, dev.txt, prod.txt)
  - [ ] Create `.env.example` file
  - [ ] Create `.gitignore` file

- [ ] **1.2** Set up virtual environment
  - [ ] Activate existing venv
  - [ ] Install Django 5.x
  - [ ] Install core dependencies
  - [ ] Create requirements files

- [ ] **1.3** Configure settings
  - [ ] Create `config/settings/base.py` (common settings)
  - [ ] Create `config/settings/dev.py` (development)
  - [ ] Create `config/settings/prod.py` (production)
  - [ ] Configure `INSTALLED_APPS`
  - [ ] Configure `MIDDLEWARE`
  - [ ] Configure `TEMPLATES`
  - [ ] Configure `DATABASES` (SQLite dev, PostgreSQL-ready)
  - [ ] Configure `STATIC_FILES` and `MEDIA_FILES`

- [ ] **1.4** Configure Tailwind CSS
  - [ ] Install django-tailwind
  - [ ] Create theme app
  - [ ] Configure Tailwind in settings
  - [ ] Set up Tailwind build process
  - [ ] Test Tailwind compilation

- [ ] **1.5** Create base templates
  - [ ] Create `templates/base.html` (responsive layout)
  - [ ] Create `templates/components/navbar.html`
  - [ ] Create `templates/components/footer.html`
  - [ ] Create `templates/components/alerts.html`
  - [ ] Set up responsive breakpoints

- [ ] **1.6** Configure environment variables
  - [ ] Create `.env.example` with all required variables
  - [ ] Install python-decouple
  - [ ] Configure SECRET_KEY
  - [ ] Configure DEBUG
  - [ ] Configure ALLOWED_HOSTS
  - [ ] Configure email settings placeholders
  - [ ] Configure Stripe keys placeholders
  - [ ] Configure DeepSeek API settings

- [ ] **1.7** Set up Docker
  - [ ] Create `Dockerfile`
  - [ ] Create `docker-compose.yml` (development)
  - [ ] Create `docker-compose.prod.yml` (production)
  - [ ] Create nginx configuration
  - [ ] Test Docker build
  - [ ] Test Docker deployment locally

---

### Phase 2: Authentication System 🔐

- [ ] **2.1** Install & configure django-allauth
  - [ ] Install django-allauth
  - [ ] Add to INSTALLED_APPS
  - [ ] Configure AUTHENTICATION_BACKENDS
  - [ ] Configure allauth settings
  - [ ] Add allauth URLs to main urls.py

- [ ] **2.2** Create accounts app
  - [ ] Create `apps/accounts/` app
  - [ ] Create custom User model (or extend default)
  - [ ] Add `role` field (choices: CLIENT, ADMIN)
  - [ ] Create UserProfile model (company_name, etc.)
  - [ ] Create migrations

- [ ] **2.3** Create authentication views
  - [ ] Customize signup template
  - [ ] Customize login template
  - [ ] Customize logout template
  - [ ] Create password reset templates
  - [ ] Add form styling with Tailwind

- [ ] **2.4** Configure email backend
  - [ ] Install django-anymail
  - [ ] Configure console backend (development)
  - [ ] Configure Resend backend (production)
  - [ ] Create email templates directory
  - [ ] Test email sending in development

- [ ] **2.5** Implement role-based access
  - [ ] Create decorators for role checking
  - [ ] Create middleware for role-based redirection
  - [ ] Protect client dashboard routes
  - [ ] Protect admin routes
  - [ ] Test access control

---

### Phase 3: Landing Page 🎨

- [ ] **3.1** Create landing app
  - [ ] Create `apps/landing/` app
  - [ ] Create views for landing page
  - [ ] Create URL patterns
  - [ ] Configure app in settings

- [ ] **3.2** Design hero section
  - [ ] Create hero section HTML
  - [ ] Add headline: "AI-Powered Real Estate Listing Descriptions"
  - [ ] Add subheadline
  - [ ] Add primary CTA: "Get Started"
  - [ ] Add secondary CTA: "View Pricing"
  - [ ] Style with Tailwind CSS
  - [ ] Make responsive

- [ ] **3.3** Create features section
  - [ ] List key features with icons
  - [ ] AI-generated descriptions
  - [ ] Property type tailoring
  - [ ] Multiple tone options
  - [ ] Multi-language placeholder
  - [ ] Team collaboration mention
  - [ ] Style with Tailwind grid/flex

- [ ] **3.4** Create "How It Works" section
  - [ ] Step 1: Add property details
  - [ ] Step 2: Click Generate
  - [ ] Step 3: Edit & copy description
  - [ ] Add visual flow (icons/numbers)
  - [ ] Make responsive

- [ ] **3.5** Create pricing section
  - [ ] Design pricing cards
  - [ ] Basic Plan (price, features, quota)
  - [ ] Pro Plan (price, features, quota)
  - [ ] Agency Plan (price, features, quota)
  - [ ] Highlight recommended plan
  - [ ] Add "Choose Plan" buttons
  - [ ] Make responsive (stack on mobile)

- [ ] **3.6** Create team section
  - [ ] Design team member cards
  - [ ] Add 5 team members (name, role, bio, avatar)
  - [ ] Use placeholder avatars
  - [ ] Make responsive (grid layout)

- [ ] **3.7** Create FAQ section
  - [ ] Add common SaaS questions
  - [ ] Add AI-related questions
  - [ ] Implement accordion/collapse UI
  - [ ] Style with Tailwind

- [ ] **3.8** Create footer
  - [ ] Add links: Terms, Privacy, Contact
  - [ ] Add Login, Sign Up links
  - [ ] Add social media placeholders
  - [ ] Add copyright notice
  - [ ] Make responsive

---

### Phase 4: Subscription System 💳

- [ ] **4.1** Install & configure dj-stripe
  - [ ] Install dj-stripe
  - [ ] Add to INSTALLED_APPS
  - [ ] Configure Stripe keys in settings
  - [ ] Run dj-stripe migrations
  - [ ] Set up Stripe test mode

- [ ] **4.2** Create subscription models
  - [ ] Create `apps/subscriptions/` app
  - [ ] Create SubscriptionPlan model
    - [ ] name (Basic, Pro, Agency)
    - [ ] stripe_price_id
    - [ ] price (monthly)
    - [ ] description_quota (monthly)
    - [ ] features (JSONField)
  - [ ] Create UserSubscription model
    - [ ] user (ForeignKey)
    - [ ] plan (ForeignKey)
    - [ ] stripe_subscription_id
    - [ ] status (active, canceled, past_due)
    - [ ] current_period_start
    - [ ] current_period_end
  - [ ] Create migrations

- [ ] **4.3** Create usage tracking model
  - [ ] Create Usage model
    - [ ] user (ForeignKey)
    - [ ] description_count (IntegerField)
    - [ ] period_start (DateTimeField)
    - [ ] period_end (DateTimeField)
  - [ ] Create service to track usage
  - [ ] Create service to check limits
  - [ ] Create service to reset monthly usage

- [ ] **4.4** Set up Stripe products/prices
  - [ ] Create Stripe products in dashboard
  - [ ] Create Stripe prices (monthly)
  - [ ] Add price IDs to database
  - [ ] Test product retrieval

- [ ] **4.5** Implement Stripe webhooks
  - [ ] Create webhook endpoint
  - [ ] Configure webhook signature verification
  - [ ] Handle `customer.subscription.created`
  - [ ] Handle `customer.subscription.updated`
  - [ ] Handle `customer.subscription.deleted`
  - [ ] Handle `invoice.payment_succeeded`
  - [ ] Handle `invoice.payment_failed`
  - [ ] Test webhooks with Stripe CLI

- [ ] **4.6** Create subscription views
  - [ ] Create plan selection page
  - [ ] Create Stripe Checkout session
  - [ ] Create subscription success page
  - [ ] Create subscription cancel page
  - [ ] Create billing portal redirect

---

### Phase 5: Client Dashboard 📊

- [ ] **5.1** Create dashboard app
  - [ ] Create `apps/dashboard/` app
  - [ ] Create base dashboard template
  - [ ] Create dashboard navigation
  - [ ] Set up URL patterns

- [ ] **5.2** Create overview page
  - [ ] Display current plan
  - [ ] Display descriptions generated this month
  - [ ] Display remaining quota
  - [ ] Display recent descriptions (last 5)
  - [ ] Add quick action buttons
  - [ ] Style with Tailwind cards

- [ ] **5.3** Create listings app
  - [ ] Create `apps/listings/` app
  - [ ] Create Listing model
    - [ ] user (ForeignKey)
    - [ ] property_title
    - [ ] property_type (choices)
    - [ ] location (city, neighborhood, country)
    - [ ] price
    - [ ] size_sqm
    - [ ] bedrooms
    - [ ] bathrooms
    - [ ] features (JSONField)
    - [ ] property_condition
    - [ ] tone (Professional, Friendly, Premium)
    - [ ] audience (Luxury, Families, Investors)
    - [ ] language
    - [ ] generated_description (TextField)
    - [ ] created_at, updated_at
  - [ ] Create migrations

- [ ] **5.4** Create "Generate Description" page
  - [ ] Create form with all property fields
  - [ ] Property Title (optional)
  - [ ] Property Type (dropdown)
  - [ ] Location fields
  - [ ] Price input
  - [ ] Size (m²)
  - [ ] Bedrooms, Bathrooms
  - [ ] Key features (multi-select or textarea)
  - [ ] Property condition (dropdown)
  - [ ] Audience/Tone options
  - [ ] Language dropdown
  - [ ] Style form with Tailwind
  - [ ] Add client-side validation

- [ ] **5.5** Integrate DeepSeek API
  - [ ] Create `apps/listings/services.py`
  - [ ] Create DeepSeek API client
  - [ ] Configure API key from environment
  - [ ] Create prompt builder function
  - [ ] Create description generation function
  - [ ] Add error handling
  - [ ] Add timeout handling
  - [ ] Test API integration

- [ ] **5.6** Implement generation flow
  - [ ] Handle form submission
  - [ ] Check user quota before generation
  - [ ] Show loading state (HTMX or Alpine.js)
  - [ ] Call DeepSeek API
  - [ ] Display generated description
  - [ ] Add "Copy to Clipboard" button
  - [ ] Add "Regenerate" button
  - [ ] Add "Save Description" button
  - [ ] Track usage after successful generation

- [ ] **5.7** Create "My Listings" page
  - [ ] Create list view with pagination
  - [ ] Display property title, type, location
  - [ ] Display date generated
  - [ ] Display description preview (truncated)
  - [ ] Add search/filter functionality
  - [ ] Add actions: View, Edit, Duplicate, Delete
  - [ ] Style with Tailwind table/cards
  - [ ] Make responsive

- [ ] **5.8** Create listing detail/edit page
  - [ ] Display full property details
  - [ ] Display full generated description
  - [ ] Allow in-place editing of description
  - [ ] Add save functionality
  - [ ] Add copy to clipboard
  - [ ] Add duplicate functionality
  - [ ] Add delete with confirmation

- [ ] **5.9** Create billing & subscription page
  - [ ] Display current plan details
  - [ ] Display next billing date
  - [ ] Display current usage
  - [ ] Add "Upgrade Plan" button
  - [ ] Add "Cancel Subscription" button
  - [ ] Integrate Stripe Customer Portal
  - [ ] Display invoice history (if available)

- [ ] **5.10** Create profile page
  - [ ] Display user information
  - [ ] Edit name
  - [ ] Edit company/agency name
  - [ ] Edit email
  - [ ] Change password (with confirmation)
  - [ ] Add form validation
  - [ ] Add success/error messages

---

### Phase 6: Admin System 🛠️

- [ ] **6.1** Install & configure django-unfold
  - [ ] Install django-unfold
  - [ ] Add to INSTALLED_APPS (before django.contrib.admin)
  - [ ] Configure unfold settings
  - [ ] Customize admin site title/header
  - [ ] Test admin UI

- [ ] **6.2** Customize admin dashboard
  - [ ] Create admin dashboard view
  - [ ] Display KPIs:
    - [ ] Total users
    - [ ] Active subscriptions
    - [ ] MRR (placeholder)
    - [ ] Total descriptions generated
  - [ ] Display recent signups
  - [ ] Display recent activity
  - [ ] Style with unfold components

- [ ] **6.3** User management in admin
  - [ ] Register User model in admin
  - [ ] Customize user list display (name, email, role, status, plan)
  - [ ] Add filters (role, status, plan)
  - [ ] Add search (name, email)
  - [ ] Add actions:
    - [ ] Activate/Deactivate user
    - [ ] Change role
    - [ ] Send password reset email
  - [ ] Create user detail view
  - [ ] Display user's subscription
  - [ ] Display user's usage stats

- [ ] **6.4** Subscription & plan management
  - [ ] Register SubscriptionPlan in admin
  - [ ] Allow creating/editing plans
  - [ ] Display plan features
  - [ ] Link to Stripe price IDs
  - [ ] Register UserSubscription in admin
  - [ ] Display subscription status
  - [ ] Add filters and search

- [ ] **6.5** Payment & invoice management
  - [ ] Use dj-stripe admin models
  - [ ] Customize payment list view
  - [ ] Display user, amount, status, date
  - [ ] Add filters (status, date range)
  - [ ] Add search

- [ ] **6.6** Listings management
  - [ ] Register Listing model in admin
  - [ ] Display property details
  - [ ] Display generated description
  - [ ] Add filters (user, property_type, date)
  - [ ] Add search

- [ ] **6.7** System settings
  - [ ] Create settings management (via environment variables)
  - [ ] Document DeepSeek API configuration
  - [ ] Document email configuration
  - [ ] Create admin page for system info
  - [ ] Display current settings (read-only)

- [ ] **6.8** Usage analytics
  - [ ] Create analytics dashboard in admin
  - [ ] Display usage by user
  - [ ] Display usage by plan
  - [ ] Display usage over time (chart)
  - [ ] Export usage data (CSV)

---

### Phase 7: Email System 📧

- [ ] **7.1** Configure email templates
  - [ ] Create base email template (HTML)
  - [ ] Style with inline CSS (email-safe)
  - [ ] Add company branding placeholders

- [ ] **7.2** Welcome email
  - [ ] Create welcome email template
  - [ ] Send on user signup
  - [ ] Include getting started guide
  - [ ] Test sending

- [ ] **7.3** Password reset email
  - [ ] Customize password reset template
  - [ ] Test reset flow
  - [ ] Ensure links work correctly

- [ ] **7.4** Subscription event emails
  - [ ] Create subscription created email
  - [ ] Create subscription updated email
  - [ ] Create subscription canceled email
  - [ ] Create payment failed email
  - [ ] Trigger emails from webhook handlers

- [ ] **7.5** Usage limit notifications
  - [ ] Create usage warning email (80% quota)
  - [ ] Create quota exceeded email
  - [ ] Trigger from usage tracking service
  - [ ] Test notification flow

- [ ] **7.6** Configure Resend for production
  - [ ] Add Resend API key to environment
  - [ ] Configure ANYMAIL settings for Resend
  - [ ] Verify domain in Resend dashboard
  - [ ] Test sending in production mode
  - [ ] Set up email tracking (optional)

---

### Phase 8: Security & Polish 🔒

- [ ] **8.1** Implement rate limiting
  - [ ] Install django-ratelimit
  - [ ] Add rate limiting to description generation (per user)
  - [ ] Add rate limiting to API endpoints
  - [ ] Add rate limiting to login/signup
  - [ ] Test rate limiting

- [ ] **8.2** Configure production security
  - [ ] Set `DEBUG = False` in prod settings
  - [ ] Configure `ALLOWED_HOSTS` properly
  - [ ] Set `SECRET_KEY` from environment
  - [ ] Enable `SECURE_SSL_REDIRECT`
  - [ ] Enable `SESSION_COOKIE_SECURE`
  - [ ] Enable `CSRF_COOKIE_SECURE`
  - [ ] Configure `SECURE_BROWSER_XSS_FILTER`
  - [ ] Configure `SECURE_CONTENT_TYPE_NOSNIFF`
  - [ ] Configure `X_FRAME_OPTIONS = 'DENY'`
  - [ ] Configure `CSRF_TRUSTED_ORIGINS`

- [ ] **8.3** Password security
  - [ ] Configure AUTH_PASSWORD_VALIDATORS
  - [ ] Set minimum password length (12+)
  - [ ] Require password complexity
  - [ ] Test password validation

- [ ] **8.4** Input validation & sanitization
  - [ ] Validate all form inputs
  - [ ] Sanitize user-generated content
  - [ ] Prevent XSS attacks
  - [ ] Prevent SQL injection (ORM handles this)
  - [ ] Validate file uploads (if any)

- [ ] **8.5** CSRF protection
  - [ ] Ensure {% csrf_token %} in all forms
  - [ ] Configure CSRF settings
  - [ ] Test CSRF protection

- [ ] **8.6** Error handling & logging
  - [ ] Configure Django logging
  - [ ] Log security events
  - [ ] Log API errors
  - [ ] Log payment errors
  - [ ] Create custom error pages (404, 500)
  - [ ] Test error pages

- [ ] **8.7** Add success/error toasts
  - [ ] Implement toast notification system
  - [ ] Style with Tailwind
  - [ ] Add to all forms
  - [ ] Add to all actions
  - [ ] Test notifications

- [ ] **8.8** Responsive design polish
  - [ ] Test on desktop (1920px, 1366px)
  - [ ] Test on tablet (768px, 1024px)
  - [ ] Test on mobile (375px, 414px)
  - [ ] Fix responsive issues
  - [ ] Optimize for touch devices

- [ ] **8.9** Accessibility improvements
  - [ ] Add ARIA labels
  - [ ] Ensure keyboard navigation
  - [ ] Test with screen reader
  - [ ] Fix contrast issues
  - [ ] Add focus states

---

### Phase 9: Testing & Deployment 🚀

- [ ] **9.1** Manual testing
  - [ ] Test user registration flow
  - [ ] Test login/logout flow
  - [ ] Test password reset flow
  - [ ] Test plan selection
  - [ ] Test Stripe checkout
  - [ ] Test description generation
  - [ ] Test quota limits
  - [ ] Test saving listings
  - [ ] Test editing listings
  - [ ] Test deleting listings
  - [ ] Test subscription cancellation
  - [ ] Test profile updates
  - [ ] Test admin user management
  - [ ] Test admin analytics

- [ ] **9.2** Payment testing
  - [ ] Test Stripe test mode
  - [ ] Test successful payment
  - [ ] Test failed payment
  - [ ] Test subscription creation
  - [ ] Test subscription update
  - [ ] Test subscription cancellation
  - [ ] Test webhook handling (use Stripe CLI)

- [ ] **9.3** DeepSeek API testing
  - [ ] Test API connection
  - [ ] Test description generation with various inputs
  - [ ] Test error handling (invalid API key)
  - [ ] Test timeout handling
  - [ ] Test rate limiting

- [ ] **9.4** Email testing
  - [ ] Test welcome email
  - [ ] Test password reset email
  - [ ] Test subscription emails
  - [ ] Test usage notification emails
  - [ ] Verify email formatting (desktop, mobile)

- [ ] **9.5** Security testing
  - [ ] Test rate limiting
  - [ ] Test CSRF protection
  - [ ] Test XSS prevention
  - [ ] Test authentication protection
  - [ ] Test role-based access control
  - [ ] Test input validation

- [ ] **9.6** Docker setup
  - [ ] Finalize Dockerfile
  - [ ] Finalize docker-compose.yml
  - [ ] Test Docker build locally
  - [ ] Test Docker deployment locally
  - [ ] Set up nginx configuration
  - [ ] Test nginx reverse proxy
  - [ ] Set up static file serving
  - [ ] Test media file uploads

- [ ] **9.7** Environment variables
  - [ ] Update .env.example with all variables
  - [ ] Document each variable
  - [ ] Create .env for development
  - [ ] Test with environment variables
  - [ ] Verify no hardcoded secrets

- [ ] **9.8** Database migration preparation
  - [ ] Review all migrations
  - [ ] Test migration from SQLite to PostgreSQL
  - [ ] Document migration steps
  - [ ] Create backup script

- [ ] **9.9** Performance optimization
  - [ ] Add database indexes
  - [ ] Optimize queries (select_related, prefetch_related)
  - [ ] Configure caching (Redis)
  - [ ] Optimize static files (compression, CDN-ready)
  - [ ] Test page load times

---

### Phase 10: Documentation 📚

- [ ] **10.1** Create/Update README.md
  - [ ] Project description
  - [ ] Features list
  - [ ] Tech stack
  - [ ] Prerequisites
  - [ ] Installation instructions
  - [ ] Development setup
  - [ ] Running the app locally
  - [ ] Running with Docker
  - [ ] Environment variables explanation
  - [ ] Testing instructions
  - [ ] Deployment instructions

- [ ] **10.2** Environment variables documentation
  - [ ] List all required variables
  - [ ] Explain each variable
  - [ ] Provide example values
  - [ ] Security notes

- [ ] **10.3** Deployment guide
  - [ ] Docker deployment steps
  - [ ] Coolify deployment steps
  - [ ] Database setup (PostgreSQL)
  - [ ] Domain configuration
  - [ ] SSL/HTTPS setup
  - [ ] Environment variables setup
  - [ ] First-time setup (superuser, plans)
  - [ ] Webhook configuration

- [ ] **10.4** Admin user guide
  - [ ] How to access admin panel
  - [ ] How to manage users
  - [ ] How to manage plans
  - [ ] How to view analytics
  - [ ] How to configure system settings

- [ ] **10.5** API documentation (if applicable)
  - [ ] Document DeepSeek API integration
  - [ ] Document Stripe API integration
  - [ ] Document webhook endpoints

- [ ] **10.6** Update PLAN.md
  - [ ] Mark completed tasks
  - [ ] Add any additional tasks discovered
  - [ ] Update timeline estimates
  - [ ] Add lessons learned section

---

## Key Packages & Dependencies

### Core Dependencies (requirements/base.txt)
```
Django>=5.0,<5.1
psycopg2-binary>=2.9.9  # PostgreSQL adapter
python-decouple>=3.8    # Environment variables
django-allauth>=0.57.0  # Authentication
dj-stripe>=2.8.0        # Stripe integration
django-tailwind>=3.8.0  # Tailwind CSS
django-anymail[resend]>=10.2  # Email (Resend)
django-unfold>=0.16.0   # Admin UI
django-ratelimit>=4.1.0 # Rate limiting
celery>=5.3.4           # Background tasks
redis>=5.0.1            # Caching & Celery broker
requests>=2.31.0        # HTTP client for DeepSeek API
Pillow>=10.1.0          # Image handling
```

### Development Dependencies (requirements/dev.txt)
```
-r base.txt
django-debug-toolbar>=4.2.0
black>=23.12.0
flake8>=6.1.0
isort>=5.13.0
pytest>=7.4.3
pytest-django>=4.7.0
```

### Production Dependencies (requirements/prod.txt)
```
-r base.txt
gunicorn>=21.2.0
whitenoise>=6.6.0  # Static file serving
sentry-sdk>=1.39.0  # Error tracking (optional)
```

---

## Database Schema Overview

### User & Authentication
- **User** (Django default or custom)
  - id, username, email, password, etc.
  - role (CLIENT, ADMIN)

- **UserProfile**
  - user_id (OneToOne)
  - company_name
  - phone
  - avatar
  - created_at, updated_at

### Subscriptions
- **SubscriptionPlan**
  - id, name, stripe_price_id
  - price, currency
  - description_quota
  - features (JSON)
  - is_active

- **UserSubscription**
  - id, user_id
  - plan_id
  - stripe_subscription_id
  - status
  - current_period_start, current_period_end
  - created_at, updated_at

### Usage Tracking
- **Usage**
  - id, user_id
  - description_count
  - period_start, period_end
  - created_at

### Listings
- **Listing**
  - id, user_id
  - property_title
  - property_type
  - location (city, neighborhood, country)
  - price, size_sqm
  - bedrooms, bathrooms
  - features (JSON)
  - property_condition
  - tone, audience, language
  - generated_description
  - created_at, updated_at

### Stripe Models (via dj-stripe)
- Customer
- Subscription
- Price
- Product
- Invoice
- PaymentMethod
- etc.

---

## API Integrations

### DeepSeek API
- **Endpoint:** https://api.deepseek.com/v1/chat/completions
- **Authentication:** Bearer token (API key)
- **Method:** POST
- **Payload:**
  ```json
  {
    "model": "deepseek-chat",
    "messages": [
      {"role": "system", "content": "You are a professional real estate copywriter..."},
      {"role": "user", "content": "Generate a listing description for..."}
    ],
    "temperature": 0.7
  }
  ```
- **Response:** JSON with generated text

### Stripe API (via dj-stripe)
- **Checkout Sessions:** Create payment sessions
- **Customer Portal:** Manage subscriptions
- **Webhooks:** Handle subscription events
- **Products & Prices:** Manage plans

### Resend API (via django-anymail)
- **Send Email:** Transactional emails
- **Templates:** HTML email templates
- **Tracking:** Open/click tracking (optional)

---

## Deployment Checklist

### Pre-Deployment
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set strong `SECRET_KEY`
- [ ] Configure PostgreSQL database
- [ ] Configure Redis for caching
- [ ] Set up Stripe production keys
- [ ] Set up Resend production API key
- [ ] Set up DeepSeek API key
- [ ] Configure email domain verification
- [ ] Set up SSL/HTTPS
- [ ] Configure CORS (if needed)
- [ ] Run security checklist (`python manage.py check --deploy`)

### Deployment to Coolify
- [ ] Create new project in Coolify
- [ ] Connect Git repository
- [ ] Configure environment variables
- [ ] Set up PostgreSQL service
- [ ] Set up Redis service
- [ ] Configure domain (listingcraft.online)
- [ ] Build Docker image
- [ ] Deploy application
- [ ] Run migrations
- [ ] Create superuser
- [ ] Create subscription plans
- [ ] Configure Stripe webhooks (production URL)
- [ ] Test application

### Post-Deployment
- [ ] Verify all pages load correctly
- [ ] Test user registration
- [ ] Test payment flow
- [ ] Test description generation
- [ ] Test email sending
- [ ] Verify webhooks are working
- [ ] Set up monitoring (Sentry, uptime monitoring)
- [ ] Set up backups (database, media)
- [ ] Configure CDN (optional)
- [ ] Performance testing
- [ ] Security audit

---

## Development Commands

```bash
# Activate virtual environment
source venv/bin/activate  # or your venv path

# Install dependencies
pip install -r requirements/dev.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run Tailwind (in separate terminal)
python manage.py tailwind start

# Collect static files
python manage.py collectstatic

# Run Celery worker (in separate terminal)
celery -A config worker -l INFO

# Run Celery beat (in separate terminal)
celery -A config beat -l INFO

# Test Stripe webhooks
stripe listen --forward-to localhost:8000/webhooks/stripe/

# Run tests
pytest

# Code formatting
black .
isort .
flake8
```

---

## Docker Commands

```bash
# Build Docker image
docker-compose build

# Run services
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Stop services
docker-compose down

# Production build
docker-compose -f docker-compose.prod.yml up -d
```

---

## Timeline Estimate

**Total Estimated Time: 4-6 weeks (full-time development)**

- **Phase 1:** Project Foundation - 3-5 days
- **Phase 2:** Authentication - 2-3 days
- **Phase 3:** Landing Page - 3-4 days
- **Phase 4:** Subscription System - 5-7 days
- **Phase 5:** Client Dashboard - 7-10 days
- **Phase 6:** Admin System - 4-5 days
- **Phase 7:** Email System - 2-3 days
- **Phase 8:** Security & Polish - 3-4 days
- **Phase 9:** Testing & Deployment - 3-5 days
- **Phase 10:** Documentation - 2-3 days

---

## Success Criteria

✅ **Functional Requirements:**
- Users can sign up, log in, reset password
- Users can select and subscribe to plans via Stripe
- Users can generate AI-powered listing descriptions
- Usage limits are enforced based on subscription plan
- Admin can manage users, subscriptions, and view analytics
- Emails are sent for key events
- Application is deployed and accessible at listingcraft.online

✅ **Technical Requirements:**
- Responsive design works on desktop, tablet, mobile
- Application is secure (HTTPS, CSRF, XSS protection)
- Docker deployment works on Coolify
- All API integrations work (DeepSeek, Stripe, Resend)
- Code is well-organized and maintainable

✅ **Business Requirements:**
- Landing page effectively communicates value proposition
- Payment flow is smooth and reliable
- AI-generated descriptions are high quality
- Admin can monitor business metrics

---

## Next Steps

1. ✅ Review and approve this plan
2. ⏳ Begin Phase 1: Project Foundation
3. ⏳ Set up development environment
4. ⏳ Start building!

---

**Last Updated:** 2025-11-15
**Status:** Planning Complete, Ready to Build
