# Security Documentation

This document outlines the security measures implemented in ListingCraft and provides guidelines for maintaining security.

## Table of Contents
- [Security Features](#security-features)
- [Configuration](#configuration)
- [Best Practices](#best-practices)
- [Deployment Checklist](#deployment-checklist)
- [Incident Response](#incident-response)

## Security Features

### 1. HTTPS & SSL/TLS
- ✅ Forced HTTPS redirects in production
- ✅ HSTS (HTTP Strict Transport Security) enabled
- ✅ HSTS preload ready
- ✅ Secure cookie flags (Secure, HttpOnly, SameSite)

### 2. Authentication & Authorization
- ✅ Django's built-in authentication system
- ✅ django-allauth for secure email-based auth
- ✅ Role-based access control (CLIENT/ADMIN)
- ✅ Password validation (minimum 10 characters in prod)
- ✅ Secure password hashing (PBKDF2-SHA256)
- ✅ Session management with secure cookies

### 3. CSRF Protection
- ✅ Django CSRF middleware enabled
- ✅ CSRF tokens required for all POST requests
- ✅ SameSite cookie attribute set
- ✅ CSRF trusted origins configured

### 4. XSS Protection
- ✅ Content Security Policy headers
- ✅ X-XSS-Protection header
- ✅ X-Content-Type-Options: nosniff
- ✅ Input sanitization utilities
- ✅ HTML escaping in templates (Django auto-escaping)

### 5. SQL Injection Prevention
- ✅ Django ORM (prevents SQL injection by default)
- ✅ Parameterized queries
- ✅ Input validation utilities
- ✅ No raw SQL queries

### 6. Rate Limiting
- ✅ Global rate limiting middleware (100 req/min)
- ✅ API-specific rate limiting (10 req/min for AI endpoints)
- ✅ IP-based and user-based rate limiting
- ✅ Cache-based implementation (Redis)

### 7. Security Headers
```
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
X-Frame-Options: DENY
Referrer-Policy: same-origin
Content-Security-Policy: [configured]
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### 8. Data Protection
- ✅ Encrypted connections (HTTPS)
- ✅ Secure session storage (Redis)
- ✅ Sensitive data not logged
- ✅ Stripe handles payment data (PCI compliant)
- ✅ No credit card data stored locally

### 9. Logging & Monitoring
- ✅ Request logging middleware
- ✅ Security event logging
- ✅ Failed login attempt logging
- ✅ Slow request detection
- ✅ Error logging to file and console

### 10. Third-Party Security
- ✅ Stripe webhooks with signature verification
- ✅ DeepSeek API key secured in environment variables
- ✅ All API keys in `.env` (not in code)
- ✅ Dependencies regularly updated

## Configuration

### Environment Variables (Required)

```bash
# Django
SECRET_KEY=<strong-random-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=listingcraft
DB_USER=listingcraft
DB_PASSWORD=<strong-password>
DB_HOST=localhost
DB_PORT=5432

# Email
RESEND_API_KEY=<your-resend-api-key>

# Stripe
STRIPE_LIVE_MODE=True
STRIPE_LIVE_PUBLIC_KEY=<your-stripe-public-key>
STRIPE_LIVE_SECRET_KEY=<your-stripe-secret-key>
DJSTRIPE_WEBHOOK_SECRET=<your-webhook-secret>

# DeepSeek
DEEPSEEK_API_KEY=<your-deepseek-api-key>

# Redis
REDIS_URL=redis://127.0.0.1:6379/1

# Security
SECURE_SSL_REDIRECT=True
```

### Rate Limiting Configuration

Add to settings (optional, defaults shown):
```python
RATE_LIMIT_REQUESTS = 100  # requests per period
RATE_LIMIT_PERIOD = 60     # seconds

API_RATE_LIMIT_REQUESTS = 10  # AI endpoint requests
API_RATE_LIMIT_PERIOD = 60    # seconds
```

## Best Practices

### For Developers

1. **Never commit secrets**
   - Use `.env` files (in `.gitignore`)
   - Use environment variables
   - Rotate keys regularly

2. **Input Validation**
   ```python
   from apps.core.validators import sanitize_text_input, validate_no_sql_injection

   cleaned_input = sanitize_text_input(user_input)
   validate_no_sql_injection(cleaned_input)
   ```

3. **Secure Redirects**
   ```python
   from apps.core.security import sanitize_redirect_url

   redirect_url = sanitize_redirect_url(next_url, fallback='/')
   ```

4. **API Key Usage**
   ```python
   # Always use from settings, never hardcode
   api_key = settings.DEEPSEEK_API_KEY
   ```

5. **Logging Sensitive Data**
   ```python
   # DON'T log passwords, API keys, credit cards
   logger.info(f"User {user.email} logged in")  # OK
   logger.info(f"API Key: {api_key}")  # NEVER DO THIS
   ```

### For Administrators

1. **Regular Updates**
   - Update dependencies monthly
   - Monitor security advisories
   - Apply security patches promptly

2. **Access Control**
   - Use strong passwords (minimum 10 characters)
   - Limit admin users
   - Regularly audit user permissions
   - Remove inactive accounts

3. **Monitoring**
   - Check logs daily for suspicious activity
   - Monitor failed login attempts
   - Watch for rate limit violations
   - Set up alerts for errors

4. **Backups**
   - Daily database backups
   - Store backups securely
   - Test restore procedures
   - Keep backups for 30 days

5. **SSL/TLS**
   - Use Let's Encrypt or paid certificate
   - Auto-renew certificates
   - Monitor expiration dates
   - Use strong cipher suites

## Deployment Checklist

Before deploying to production:

### Django Settings
- [ ] `DEBUG = False`
- [ ] `SECRET_KEY` is strong and random
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] `CSRF_TRUSTED_ORIGINS` set
- [ ] Database credentials secured
- [ ] All API keys in environment variables

### Security Headers
- [ ] HTTPS enabled
- [ ] HSTS configured
- [ ] Security headers middleware enabled
- [ ] Content Security Policy configured

### Database
- [ ] PostgreSQL (not SQLite)
- [ ] Strong database password
- [ ] Database backups configured
- [ ] Connection pooling enabled

### Logging
- [ ] Logs directory exists
- [ ] Log rotation configured
- [ ] Sensitive data not logged
- [ ] Error notifications set up

### Third-Party Services
- [ ] Stripe webhooks configured
- [ ] Webhook signatures verified
- [ ] Email service configured (Resend)
- [ ] Redis cache configured

### Monitoring
- [ ] Application monitoring (e.g., Sentry)
- [ ] Uptime monitoring
- [ ] SSL certificate monitoring
- [ ] Log aggregation

### Access Control
- [ ] Admin accounts secured
- [ ] Staff users limited
- [ ] Regular access audits scheduled

## Incident Response

### If Security Breach Suspected

1. **Immediate Actions**
   - Isolate affected systems
   - Preserve logs
   - Change all credentials
   - Notify users if data compromised

2. **Investigation**
   - Review logs for attack vector
   - Identify compromised data
   - Document timeline
   - Assess impact

3. **Remediation**
   - Patch vulnerabilities
   - Restore from clean backups if needed
   - Update security measures
   - Monitor for repeat attacks

4. **Communication**
   - Notify affected users
   - Report to authorities if required (GDPR, etc.)
   - Document incident
   - Update security policies

### Common Issues

**Failed Login Attempts**
```bash
# Check logs
grep "Failed login" logs/django.log

# Check rate limits
# Redis: GET rate_limit:<ip>
```

**Rate Limit Exceeded**
```bash
# Clear rate limit for IP
# Redis: DEL rate_limit:<ip>

# Or wait for expiration (60 seconds default)
```

**Suspicious Activity**
```bash
# Check security logs
grep "Suspicious" logs/django.log
grep "WARNING" logs/django.log
```

## Security Contacts

- **Security Issues**: security@listingcraft.online
- **Bug Bounty**: Not currently available
- **Responsible Disclosure**: security@listingcraft.online

## Updates

This document should be reviewed and updated:
- After security incidents
- When new features are added
- Quarterly as part of security audit
- When security best practices change

---

**Last Updated**: 2025-01-15
**Version**: 1.0
