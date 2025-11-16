# ListingCraft

**AI-Powered Real Estate Listing Description Generator**

ListingCraft is a production-ready SaaS web application built with Django that helps real estate agencies generate compelling, SEO-friendly property listing descriptions using AI (DeepSeek API).

---

## Features

- **AI-Powered Descriptions**: Generate high-quality listing descriptions using DeepSeek API
- **User Authentication**: Secure signup, login, and password reset with django-allauth
- **Subscription Management**: Stripe integration for subscription-based billing
- **Usage Tracking**: Monitor and limit API usage based on subscription plans
- **Responsive Design**: Beautiful, mobile-friendly UI with Tailwind CSS
- **Admin Dashboard**: Modern admin interface with django-unfold
- **Email Notifications**: Automated emails for user events (Resend API)
- **Docker Ready**: Easy deployment with Docker and Coolify support

---

## Tech Stack

- **Backend**: Django 5.0, Python 3.13
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: Django Templates, Tailwind CSS, Alpine.js
- **Payments**: Stripe (via dj-stripe)
- **Email**: Resend (via django-anymail)
- **Background Tasks**: Celery + Redis
- **Admin**: Django Admin + django-unfold
- **Deployment**: Docker, Gunicorn, Nginx

---

## Project Structure

```
listingcraft/
├── config/                 # Django project configuration
│   ├── settings/
│   │   ├── base.py        # Shared settings
│   │   ├── dev.py         # Development settings
│   │   └── prod.py        # Production settings
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                   # Django apps
│   ├── accounts/          # Authentication & user profiles
│   ├── landing/           # Marketing pages
│   ├── dashboard/         # Client dashboard
│   ├── subscriptions/     # Plans & payments
│   ├── listings/          # Listing generation
│   └── core/              # Shared utilities
├── templates/             # Global templates
│   ├── base.html
│   └── components/
├── static/                # Static files
├── media/                 # User uploads
├── docker/                # Docker configuration
├── requirements/          # Python dependencies
├── .env.example          # Environment variables template
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Development Docker setup
├── docker-compose.prod.yml # Production Docker setup
├── manage.py
├── PLAN.md              # Detailed project plan
└── README.md            # This file
```

---

## Prerequisites

- Python 3.13+
- Node.js 18+ (for Tailwind CSS)
- PostgreSQL 15+ (for production)
- Redis 7+ (for Celery)
- Docker & Docker Compose (optional, for containerized deployment)

---

## Installation & Setup

### 1. Clone the Repository

```bash
cd ListingCraft
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements/dev.txt
```

### 4. Configure Environment Variables

Copy the example environment file and update it with your credentials:

```bash
cp .env.example .env
```

Edit `.env` and set:
- `SECRET_KEY`: Generate a secure secret key
- `DEEPSEEK_API_KEY`: Your DeepSeek API key
- `STRIPE_TEST_SECRET_KEY`: Your Stripe test secret key
- `STRIPE_TEST_PUBLIC_KEY`: Your Stripe test public key
- `RESEND_API_KEY`: Your Resend API key (for production emails)

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Build Tailwind CSS

In a separate terminal:

```bash
python manage.py tailwind install
python manage.py tailwind start
```

### 8. Run Development Server

```bash
python manage.py runserver
```

Visit [http://localhost:8000](http://localhost:8000)

---

## Development Commands

### Run Development Server

```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Tailwind CSS (watch mode)
python manage.py tailwind start

# Terminal 3 (optional): Celery worker
celery -A config worker -l INFO

# Terminal 4 (optional): Celery beat
celery -A config beat -l INFO
```

### Database Operations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Reset database (CAUTION: deletes all data)
rm db.sqlite3
python manage.py migrate
```

### Static Files

```bash
# Collect static files
python manage.py collectstatic

# Build Tailwind CSS for production
python manage.py tailwind build
```

### Code Quality

```bash
# Format code with black
black .

# Sort imports
isort .

# Lint code
flake8

# Run tests
pytest
```

---

## Docker Deployment

### Development with Docker

```bash
# Build and start services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f web

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Stop services
docker-compose down
```

### Production with Docker

```bash
# Build and start production services
docker-compose -f docker-compose.prod.yml up --build -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down
```

---

## Deployment to Coolify

### Prerequisites

1. Coolify instance set up and accessible
2. Domain name configured (`listingcraft.online`)
3. PostgreSQL database provisioned
4. Redis instance provisioned

### Steps

1. **Create New Project** in Coolify
2. **Connect Git Repository**
3. **Configure Environment Variables** in Coolify:
   - Add all variables from `.env.example`
   - Set production values for:
     - `SECRET_KEY`
     - `DEBUG=False`
     - `ALLOWED_HOSTS=listingcraft.online,www.listingcraft.online`
     - `DJANGO_SETTINGS_MODULE=config.settings.prod`
     - Database credentials
     - Stripe production keys
     - Resend API key

4. **Configure Services**:
   - Main App: Uses `Dockerfile`
   - Database: PostgreSQL 15
   - Cache: Redis 7

5. **Deploy**:
   - Coolify will build the Docker image
   - Run migrations: `python manage.py migrate`
   - Create superuser: `python manage.py createsuperuser`
   - Create subscription plans in admin

6. **Post-Deployment**:
   - Configure Stripe webhooks (point to `https://listingcraft.online/webhooks/stripe/`)
   - Verify domain DNS settings
   - Test payment flow
   - Test email sending

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `your-secret-key-here` |
| `DEBUG` | Debug mode (True/False) | `False` |
| `ALLOWED_HOSTS` | Allowed hosts | `listingcraft.online,www.listingcraft.online` |
| `DEEPSEEK_API_KEY` | DeepSeek API key | `sk-...` |
| `STRIPE_TEST_SECRET_KEY` | Stripe test secret key | `sk_test_...` |
| `STRIPE_TEST_PUBLIC_KEY` | Stripe test public key | `pk_test_...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_NAME` | PostgreSQL database name | `listingcraft` |
| `DB_USER` | PostgreSQL user | `listingcraft` |
| `DB_PASSWORD` | PostgreSQL password | - |
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `REDIS_URL` | Redis connection URL | `redis://127.0.0.1:6379/1` |
| `RESEND_API_KEY` | Resend API key | - |
| `STRIPE_LIVE_SECRET_KEY` | Stripe live secret key | - |
| `STRIPE_LIVE_PUBLIC_KEY` | Stripe live public key | - |

See `.env.example` for all available variables.

---

## API Integrations

### DeepSeek API

The application uses DeepSeek API for generating listing descriptions.

**Configuration**:
- Set `DEEPSEEK_API_KEY` in `.env`
- Default endpoint: `https://api.deepseek.com/v1/chat/completions`
- Model: `deepseek-chat`

### Stripe

Subscription management and payments via Stripe.

**Setup**:
1. Create products and prices in Stripe Dashboard
2. Add price IDs to `SubscriptionPlan` models
3. Configure webhook endpoint: `https://your-domain.com/webhooks/stripe/`
4. Set `DJSTRIPE_WEBHOOK_SECRET`

### Resend

Transactional email delivery.

**Setup**:
1. Sign up at [resend.com](https://resend.com)
2. Verify your domain
3. Get API key and set `RESEND_API_KEY`

---

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps

# Run specific test file
pytest apps/listings/tests.py

# Run with verbose output
pytest -v
```

### Test Stripe Webhooks

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login to Stripe
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:8000/webhooks/stripe/
```

---

## Project Roadmap

See [PLAN.md](PLAN.md) for detailed project plan and task checklist.

### Phase 1: Foundation (Completed)
- ✅ Django project structure
- ✅ Tailwind CSS setup
- ✅ Base templates
- ✅ Docker configuration

### Phase 2: Authentication (Completed)
- ✅ django-allauth integration
- ✅ User profile models with role-based access
- ✅ Email-based authentication
- ✅ Custom decorators for client/admin roles

### Phase 3: Landing Page (Completed)
- ✅ Hero section
- ✅ Features section
- ✅ Pricing section
- ✅ Testimonials section
- ✅ FAQ section
- ✅ CTA sections

### Phase 4: Subscriptions (Completed)
- ✅ Stripe integration via dj-stripe
- ✅ Subscription plans (Basic, Pro, Agency)
- ✅ Usage tracking and quota enforcement
- ✅ Webhook handling for payment events

### Phase 5: Client Dashboard (Completed)
- ✅ Dashboard overview with statistics
- ✅ Listing creation form
- ✅ DeepSeek API integration for AI descriptions
- ✅ Listing management (CRUD operations)
- ✅ Usage quota display

### Phase 6: Admin Dashboard (Completed)
- ✅ System-wide statistics
- ✅ User management interface
- ✅ Revenue tracking and analytics
- ✅ Subscription management

### Phase 7: Email Notifications (Completed)
- ✅ Welcome emails
- ✅ Subscription confirmation
- ✅ Quota warning emails
- ✅ Password reset emails
- ✅ HTML email templates

### Phase 8: Security Hardening (Completed)
- ✅ HTTPS and HSTS configuration
- ✅ Rate limiting middleware
- ✅ Input sanitization and validation
- ✅ Security headers (CSP, X-Frame-Options, etc.)
- ✅ SQL injection and XSS prevention
- ✅ Security audit logging

### Phase 9: Testing & Documentation (Completed)
- ✅ Unit tests for models, views, and services
- ✅ Comprehensive documentation (README, SECURITY.md)
- ✅ API integration testing framework

### Phase 10: Deployment - See DEPLOYMENT.md for complete guide

---

## Contributing

This is a commercial SaaS project. For contributions or issues, please contact the development team.

---

## Security

- Never commit `.env` files or secrets to version control
- Use environment variables for all sensitive configuration
- Keep Django `SECRET_KEY` secure
- Enable HTTPS in production
- Regularly update dependencies: `pip list --outdated`
- Run security checks: `python manage.py check --deploy`

---

## License

Proprietary - All rights reserved

---

## Support

For questions or support:
- Email: support@listingcraft.online
- Documentation: See PLAN.md
- Issues: Contact the development team

---

## Credits

Built with:
- [Django](https://www.djangoproject.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [dj-stripe](https://dj-stripe.dev/)
- [django-allauth](https://django-allauth.readthedocs.io/)
- [Celery](https://docs.celeryproject.org/)
- [DeepSeek API](https://deepseek.com/)

---

**ListingCraft** - Transforming Real Estate Listings with AI
