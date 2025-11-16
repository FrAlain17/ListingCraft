# ListingCraft Deployment Guide

Complete guide for deploying ListingCraft to production using Docker and Coolify.

## Table of Contents
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Production Environment Setup](#production-environment-setup)
- [Docker Deployment](#docker-deployment)
- [Coolify Deployment](#coolify-deployment)
- [Post-Deployment](#post-deployment)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

### Code Preparation

- [ ] All phases completed (1-9)
- [ ] Tests passing (`python manage.py test`)
- [ ] No debug statements in code
- [ ] All TODO comments resolved
- [ ] Security check passed (`python manage.py check --deploy`)
- [ ] Static files collected (`python manage.py collectstatic`)
- [ ] Migrations up to date

### Third-Party Services

- [ ] **Domain Name**
  - Domain purchased and configured
  - DNS records ready
  - SSL certificate (Let's Encrypt recommended)

- [ ] **DeepSeek API**
  - API key obtained from [https://deepseek.com](https://deepseek.com)
  - API limits understood
  - Production API key (not test key)

- [ ] **Stripe**
  - Stripe account created
  - Products and prices created
  - Live API keys obtained (not test keys)
  - Webhook secret obtained
  - Business information verified

- [ ] **Resend (Email)**
  - Account created at [https://resend.com](https://resend.com)
  - Domain verified
  - API key obtained
  - From email address configured

- [ ] **Database & Cache**
  - PostgreSQL 15+ database provisioned
  - Redis 7+ instance provisioned
  - Connection details secured

### Security

- [ ] Strong `SECRET_KEY` generated (50+ characters)
- [ ] All API keys secured in environment variables
- [ ] `.env` file NOT in version control
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] Database credentials secured
- [ ] Backup strategy defined

---

## Production Environment Setup

### 1. Server Requirements

**Minimum Specifications:**
- CPU: 2 cores
- RAM: 4 GB
- Storage: 20 GB SSD
- OS: Ubuntu 22.04 LTS or Docker-compatible OS

**Recommended Specifications:**
- CPU: 4 cores
- RAM: 8 GB
- Storage: 50 GB SSD
- OS: Ubuntu 22.04 LTS

### 2. Required Services

**PostgreSQL Database:**
```bash
# Connection details needed:
DB_NAME=listingcraft
DB_USER=listingcraft
DB_PASSWORD=YyB@QSQpsM5Xb6@7
DB_HOST=localhost
DB_PORT=5432
```

**Redis Cache:**
```bash
# Connection string needed:
REDIS_URL=redis://<redis-host>:6379/1
```

### 3. Environment Variables

Create production `.env` file with these variables:

```bash
# Django Core
SECRET_KEY=<generate-50-char-random-string>
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.prod
ALLOWED_HOSTS=listingcraft.online,www.listingcraft.online
CSRF_TRUSTED_ORIGINS=https://listingcraft.online,https://www.listingcraft.online

# Database (PostgreSQL)
DB_NAME=listingcraft
DB_USER=listingcraft
DB_PASSWORD=<your-db-password>
DB_HOST=<your-db-host>
DB_PORT=5432

# Cache (Redis)
REDIS_URL=redis://<your-redis-host>:6379/1

# DeepSeek API
DEEPSEEK_API_KEY=<your-deepseek-api-key>

# Stripe (Production Keys)
STRIPE_LIVE_MODE=True
STRIPE_LIVE_PUBLIC_KEY=pk_live_...
STRIPE_LIVE_SECRET_KEY=sk_live_...
DJSTRIPE_WEBHOOK_SECRET=whsec_...

# Email (Resend)
RESEND_API_KEY=re_...
DEFAULT_FROM_EMAIL=noreply@listingcraft.online

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
API_RATE_LIMIT_REQUESTS=10
API_RATE_LIMIT_PERIOD=60
```

### 4. Generate SECRET_KEY

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Or use:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

---

## Docker Deployment

### 1. Build Docker Image

```bash
# Build production image
docker build -f Dockerfile -t listingcraft:latest .

# Test image locally
docker run -it --rm \
  --env-file .env.prod \
  -p 8000:8000 \
  listingcraft:latest
```

### 2. Docker Compose Production

The project includes `docker-compose.prod.yml` for production deployment:

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### 3. Nginx Configuration (if not using Coolify)

Create `/etc/nginx/sites-available/listingcraft`:

```nginx
upstream listingcraft {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name listingcraft.online www.listingcraft.online;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name listingcraft.online www.listingcraft.online;

    ssl_certificate /etc/letsencrypt/live/listingcraft.online/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/listingcraft.online/privkey.pem;

    client_max_body_size 10M;

    location /static/ {
        alias /var/www/listingcraft/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/listingcraft/media/;
        expires 30d;
    }

    location / {
        proxy_pass http://listingcraft;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/listingcraft /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Coolify Deployment

### 1. Prerequisites

- Coolify instance running
- Domain DNS configured
- Git repository accessible

### 2. Create New Project

1. Login to Coolify dashboard
2. Click "New Project"
3. Enter project name: "ListingCraft"
4. Select environment: "Production"

### 3. Connect Repository

1. Click "New Resource"
2. Select "Git Repository"
3. Choose your Git provider
4. Select the ListingCraft repository
5. Branch: `main` or `master`

### 4. Configure Build Settings

**Dockerfile:**
- Build Pack: `Dockerfile`
- Dockerfile Location: `./Dockerfile`
- Build Context: `.`

**Port:**
- Publish Port: `8000`

### 5. Environment Variables

Add all production environment variables in Coolify:

Go to **Environment Variables** section and add:

```
SECRET_KEY=<your-secret-key>
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.prod
ALLOWED_HOSTS=listingcraft.online,www.listingcraft.online
CSRF_TRUSTED_ORIGINS=https://listingcraft.online,https://www.listingcraft.online

DB_NAME=<from-coolify-postgres>
DB_USER=<from-coolify-postgres>
DB_PASSWORD=<from-coolify-postgres>
DB_HOST=<from-coolify-postgres>
DB_PORT=5432

REDIS_URL=<from-coolify-redis>

DEEPSEEK_API_KEY=<your-key>

STRIPE_LIVE_MODE=True
STRIPE_LIVE_PUBLIC_KEY=<your-key>
STRIPE_LIVE_SECRET_KEY=<your-key>
DJSTRIPE_WEBHOOK_SECRET=<your-secret>

RESEND_API_KEY=<your-key>
DEFAULT_FROM_EMAIL=noreply@listingcraft.online

SECURE_SSL_REDIRECT=True
```

### 6. Add Database (PostgreSQL)

1. Go to "Resources" > "New Resource"
2. Select "PostgreSQL"
3. Version: 15 or latest
4. Note the connection details
5. Add to environment variables

### 7. Add Cache (Redis)

1. Go to "Resources" > "New Resource"
2. Select "Redis"
3. Version: 7 or latest
4. Note the connection URL
5. Add to environment variables

### 8. Configure Domain

1. Go to "Domains" section
2. Add custom domain: `listingcraft.online`
3. Coolify will auto-provision SSL certificate
4. Update DNS:
   - Type: A
   - Name: @
   - Value: `<coolify-server-ip>`

   - Type: A
   - Name: www
   - Value: `<coolify-server-ip>`

### 9. Deploy

1. Click "Deploy" button
2. Monitor build logs
3. Wait for deployment to complete

### 10. Post-Deployment Commands

Run these commands in Coolify's terminal:

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Create subscription plans
python manage.py shell
>>> from apps.subscriptions.models import SubscriptionPlan
>>> SubscriptionPlan.objects.create(...)
```

---

## Post-Deployment

### 1. Create Subscription Plans

Login to Django admin at `https://listingcraft.online/admin/`:

Create 3 plans:

**Basic Plan:**
- Name: "Basic"
- Plan Type: BASIC
- Price: $9.99
- Description Quota: 10
- Stripe Price ID: `price_xxx`
- Features: `["AI descriptions", "10 listings/month", "Email support"]`

**Pro Plan:**
- Name: "Professional"
- Plan Type: PRO
- Price: $29.99
- Description Quota: 50
- Stripe Price ID: `price_yyy`
- Features: `["AI descriptions", "50 listings/month", "Priority support", "Advanced customization"]`

**Agency Plan:**
- Name: "Agency"
- Plan Type: AGENCY
- Price: $99.99
- Description Quota: -1 (unlimited)
- Stripe Price ID: `price_zzz`
- Features: `["AI descriptions", "Unlimited listings", "Priority support", "Team accounts", "White-label option"]`

### 2. Configure Stripe Webhooks

1. Go to Stripe Dashboard > Developers > Webhooks
2. Click "Add endpoint"
3. Endpoint URL: `https://listingcraft.online/webhooks/stripe/`
4. Events to send:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy webhook signing secret
6. Update `DJSTRIPE_WEBHOOK_SECRET` in environment

### 3. Test Payment Flow

1. Create test account
2. Subscribe to Basic plan
3. Complete Stripe checkout
4. Verify subscription created
5. Test description generation
6. Verify quota tracking

### 4. Test Email Sending

1. Sign up new user
2. Verify welcome email received
3. Test password reset
4. Test quota warning emails

### 5. Verify Security

```bash
# Run Django security check
python manage.py check --deploy

# Verify HTTPS
curl -I https://listingcraft.online

# Check security headers
curl -I https://listingcraft.online | grep -i "strict-transport-security"
```

### 6. Create Admin User

1. Set superuser's profile role to ADMIN
2. Test admin dashboard access
3. Verify user management functions

---

## Monitoring & Maintenance

### 1. Monitoring Setup

**Application Monitoring:**
- Use Sentry for error tracking
- Configure in `config/settings/prod.py`:

```python
if not DEBUG:
    import sentry_sdk
    sentry_sdk.init(
        dsn="your-sentry-dsn",
        traces_sample_rate=1.0,
    )
```

**Server Monitoring:**
- CPU, RAM, Disk usage
- Use Coolify's built-in monitoring
- Set up alerts for high usage

**Database Monitoring:**
- Connection pool
- Slow queries
- Database size

### 2. Backups

**Database Backups:**
```bash
# Daily automated backup
0 2 * * * pg_dump -U listingcraft listingcraft > /backups/listingcraft_$(date +\%Y\%m\%d).sql
```

**Media Files Backup:**
```bash
# Weekly backup
0 3 * * 0 tar -czf /backups/media_$(date +\%Y\%m\%d).tar.gz /var/www/listingcraft/media/
```

**Backup Retention:**
- Daily: Keep 7 days
- Weekly: Keep 4 weeks
- Monthly: Keep 12 months

### 3. Log Management

**Application Logs:**
```bash
# View Django logs
docker-compose -f docker-compose.prod.yml logs -f web

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

**Log Rotation:**
Configure in `/etc/logrotate.d/listingcraft`:
```
/var/log/listingcraft/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

### 4. Regular Maintenance Tasks

**Weekly:**
- [ ] Review error logs
- [ ] Check disk space
- [ ] Monitor API usage
- [ ] Review failed payments

**Monthly:**
- [ ] Update dependencies
- [ ] Security patch check
- [ ] Database optimization
- [ ] Backup verification
- [ ] Performance review

**Quarterly:**
- [ ] Security audit
- [ ] Load testing
- [ ] Disaster recovery test
- [ ] Documentation update

---

## Troubleshooting

### Common Issues

**1. Static Files Not Loading**
```bash
# Collect static files again
python manage.py collectstatic --noinput --clear

# Check permissions
sudo chown -R www-data:www-data /var/www/listingcraft/staticfiles/
```

**2. Database Connection Errors**
```bash
# Test database connection
python manage.py dbshell

# Check environment variables
echo $DB_HOST
echo $DB_NAME

# Verify PostgreSQL is running
sudo systemctl status postgresql
```

**3. Email Not Sending**
```bash
# Test Resend API
curl -X POST https://api.resend.com/emails \
  -H "Authorization: Bearer $RESEND_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "noreply@listingcraft.online",
    "to": "test@example.com",
    "subject": "Test",
    "html": "<p>Test email</p>"
  }'

# Check logs
grep "email" logs/django.log
```

**4. Stripe Webhooks Failing**
```bash
# Check webhook endpoint
curl https://listingcraft.online/webhooks/stripe/

# Verify webhook secret
echo $DJSTRIPE_WEBHOOK_SECRET

# Test with Stripe CLI
stripe listen --forward-to https://listingcraft.online/webhooks/stripe/
```

**5. Rate Limiting Too Aggressive**
```env
# Adjust in .env
RATE_LIMIT_REQUESTS=200  # Increase from 100
RATE_LIMIT_PERIOD=60

API_RATE_LIMIT_REQUESTS=20  # Increase from 10
API_RATE_LIMIT_PERIOD=60
```

**6. High Memory Usage**
```bash
# Check running processes
docker stats

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Clear cache
docker-compose -f docker-compose.prod.yml exec web python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

### Health Checks

**Application Health:**
```bash
curl https://listingcraft.online/
# Should return 200 OK
```

**Database Health:**
```bash
python manage.py dbshell
\l  # List databases
\dt  # List tables
```

**Redis Health:**
```bash
redis-cli -h $REDIS_HOST ping
# Should return PONG
```

### Emergency Procedures

**1. Site Down - Quick Recovery**
```bash
# Check all services
docker-compose -f docker-compose.prod.yml ps

# Restart all services
docker-compose -f docker-compose.prod.yml restart

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

**2. Database Corruption**
```bash
# Restore from backup
pg_restore -U listingcraft -d listingcraft /backups/latest.sql

# Run migrations
python manage.py migrate
```

**3. Security Breach Suspected**
```bash
# Immediate actions:
# 1. Take site offline
sudo systemctl stop nginx

# 2. Change all credentials
# - SECRET_KEY
# - Database password
# - API keys

# 3. Review logs
grep "suspicious" logs/django.log

# 4. Restore from clean backup

# 5. Update security patches
pip install --upgrade -r requirements/prod.txt

# 6. Bring site back online
sudo systemctl start nginx
```

### Getting Help

**Resources:**
- Django Documentation: [https://docs.djangoproject.com](https://docs.djangoproject.com)
- Coolify Documentation: [https://coolify.io/docs](https://coolify.io/docs)
- Stripe Documentation: [https://stripe.com/docs](https://stripe.com/docs)
- Project SECURITY.md for security guidelines

**Support Channels:**
- Emergency: security@listingcraft.online
- General: support@listingcraft.online

---

**Deployment Complete!** 🎉

Your ListingCraft SaaS application is now live and ready to transform real estate listings with AI-powered descriptions.
