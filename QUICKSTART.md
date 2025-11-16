# ListingCraft Quick Start Guide

Get ListingCraft up and running in under 10 minutes.

## For Development

### 1. Prerequisites

- Python 3.13+
- Node.js 18+ (for Tailwind CSS)
- Git

### 2. Clone & Setup

```bash
# Clone repository
git clone <your-repo-url>
cd ListingCraft

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/dev.txt
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set:
# - SECRET_KEY (generate with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
# - DEEPSEEK_API_KEY (get from https://deepseek.com)
# - STRIPE_TEST_SECRET_KEY (get from https://stripe.com/test)
# - STRIPE_TEST_PUBLIC_KEY
```

### 4. Initialize Database

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Initialize subscription plans
python manage.py init_plans
```

### 5. Build Frontend

```bash
# Install Tailwind
python manage.py tailwind install

# In a separate terminal, start Tailwind watch mode
python manage.py tailwind start
```

### 6. Run Development Server

```bash
# In your main terminal
python manage.py runserver
```

Visit [http://localhost:8000](http://localhost:8000)

---

## For Production (Docker)

### 1. Prerequisites

- Docker & Docker Compose
- Domain name with DNS configured
- SSL certificate (Let's Encrypt recommended)

### 2. Prepare Environment

```bash
# Copy production environment template
cp .env.production.example .env

# Edit .env and fill in all production values:
nano .env
```

**Critical settings to update:**
- `SECRET_KEY` - Generate a strong random key
- `DEBUG=False`
- `ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com`
- `DB_PASSWORD` - Strong database password
- `DEEPSEEK_API_KEY` - Production API key
- `STRIPE_LIVE_SECRET_KEY` - Live Stripe keys
- `STRIPE_LIVE_MODE=True`
- `RESEND_API_KEY` - Production email API key
- `SECURE_SSL_REDIRECT=True`

### 3. Run Deployment Checklist

```bash
chmod +x scripts/deployment_checklist.sh
./scripts/deployment_checklist.sh
```

Fix any issues reported before proceeding.

### 4. Build & Deploy

```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up --build -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Initialize subscription plans
docker-compose -f docker-compose.prod.yml exec web python manage.py init_plans

# Create superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### 5. Configure Stripe Webhooks

1. Go to Stripe Dashboard > Developers > Webhooks
2. Add endpoint: `https://yourdomain.com/webhooks/stripe/`
3. Select events:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
4. Copy webhook signing secret
5. Update `DJSTRIPE_WEBHOOK_SECRET` in `.env`
6. Restart web service:
   ```bash
   docker-compose -f docker-compose.prod.yml restart web
   ```

### 6. Update Subscription Plans with Stripe IDs

1. Create products in Stripe Dashboard
2. Copy price IDs
3. Update in Django Admin:
   - Login: `https://yourdomain.com/admin/`
   - Go to Subscriptions > Subscription Plans
   - Update each plan with Stripe Price ID

### 7. Verify Deployment

```bash
# Check all services are running
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f web

# Test the site
curl https://yourdomain.com
```

---

## For Coolify Deployment

### 1. Prerequisites

- Coolify instance set up
- Domain configured
- Git repository accessible

### 2. Create New Project in Coolify

1. Login to Coolify
2. New Project → Name: "ListingCraft"
3. New Resource → Git Repository
4. Select your repository

### 3. Configure Environment

Add all variables from `.env.production.example` in Coolify's Environment Variables section.

### 4. Add Services

**PostgreSQL:**
- Type: PostgreSQL 15
- Note connection details

**Redis:**
- Type: Redis 7
- Note connection URL

Update environment variables with database and Redis connection details.

### 5. Configure Build

- Build Pack: Dockerfile
- Dockerfile Path: `./Dockerfile`
- Port: 8000

### 6. Deploy

1. Click "Deploy"
2. Wait for build to complete
3. Run post-deployment commands in Coolify terminal:

```bash
python manage.py migrate
python manage.py init_plans
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 7. Configure Domain

1. Add custom domain in Coolify
2. SSL will be auto-provisioned
3. Update DNS:
   - A record: `@` → `<coolify-ip>`
   - A record: `www` → `<coolify-ip>`

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'django'"

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements/dev.txt
```

### "CSRF verification failed"

```bash
# Check CSRF_TRUSTED_ORIGINS in .env
# Should match your domain(s)
```

### "Stripe webhook failing"

```bash
# Test webhook locally with Stripe CLI
stripe listen --forward-to localhost:8000/webhooks/stripe/

# Verify DJSTRIPE_WEBHOOK_SECRET matches Stripe
```

### "Static files not loading"

```bash
# Development
python manage.py tailwind build

# Production
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### "Database connection error"

```bash
# Check database is running
docker-compose -f docker-compose.prod.yml ps db

# Check environment variables
echo $DB_HOST
echo $DB_NAME

# Test connection
docker-compose -f docker-compose.prod.yml exec web python manage.py dbshell
```

---

## Next Steps

1. **Review SECURITY.md** - Understand security measures
2. **Read DEPLOYMENT.md** - Comprehensive deployment guide
3. **Check PLAN.md** - Project roadmap and features
4. **Configure Monitoring** - Set up Sentry (optional)
5. **Set up Backups** - Configure automated backups
6. **Test Payment Flow** - Create test subscription
7. **Launch!** 🚀

---

## Support

- Documentation: See README.md, SECURITY.md, DEPLOYMENT.md
- Issues: Check troubleshooting section above
- Email: support@listingcraft.online

---

**ListingCraft** - Transforming Real Estate Listings with AI
