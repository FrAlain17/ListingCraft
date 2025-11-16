"""
Security utilities and helper functions.
"""
import secrets
import hashlib
import hmac
from django.conf import settings
from django.core.signing import Signer, BadSignature
import logging

logger = logging.getLogger(__name__)


def generate_secure_token(length=32):
    """
    Generate a cryptographically secure random token.
    """
    return secrets.token_urlsafe(length)


def verify_webhook_signature(payload, signature, secret):
    """
    Verify webhook signature (e.g., for Stripe webhooks).
    Returns True if signature is valid.
    """
    try:
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)
    except Exception as e:
        logger.error(f'Webhook signature verification failed: {e}')
        return False


def sign_data(data):
    """
    Sign data with Django's signing module.
    Returns signed string.
    """
    signer = Signer()
    return signer.sign(data)


def unsign_data(signed_data):
    """
    Unsign and verify data.
    Returns original data if valid, None if invalid.
    """
    try:
        signer = Signer()
        return signer.unsign(signed_data)
    except BadSignature:
        logger.warning('Invalid signature detected')
        return None


def hash_api_key(api_key):
    """
    Hash API key for secure storage.
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def constant_time_compare(val1, val2):
    """
    Constant-time string comparison to prevent timing attacks.
    """
    return hmac.compare_digest(str(val1), str(val2))


class SecurityAuditLog:
    """
    Log security-related events for auditing.
    """

    @staticmethod
    def log_failed_login(email, ip_address):
        """Log failed login attempt."""
        logger.warning(
            f'Failed login attempt - Email: {email}, IP: {ip_address}'
        )

    @staticmethod
    def log_suspicious_activity(user, activity, ip_address):
        """Log suspicious user activity."""
        logger.warning(
            f'Suspicious activity - User: {user}, '
            f'Activity: {activity}, IP: {ip_address}'
        )

    @staticmethod
    def log_permission_denied(user, resource, ip_address):
        """Log unauthorized access attempt."""
        logger.warning(
            f'Permission denied - User: {user}, '
            f'Resource: {resource}, IP: {ip_address}'
        )

    @staticmethod
    def log_rate_limit_exceeded(identifier, endpoint):
        """Log rate limit violation."""
        logger.warning(
            f'Rate limit exceeded - Identifier: {identifier}, '
            f'Endpoint: {endpoint}'
        )

    @staticmethod
    def log_malicious_input(user, input_type, ip_address):
        """Log malicious input attempt."""
        logger.error(
            f'Malicious input detected - User: {user}, '
            f'Type: {input_type}, IP: {ip_address}'
        )


def get_client_ip(request):
    """
    Get the real client IP address from request.
    Handles proxies and load balancers correctly.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        # X-Forwarded-For can contain multiple IPs, first one is the original client
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')

    return ip


def is_safe_redirect_url(url, allowed_hosts=None):
    """
    Check if URL is safe for redirects.
    Prevents open redirect vulnerabilities.
    """
    if not url:
        return False

    # Disallow absolute URLs
    if url.startswith('http://') or url.startswith('https://'):
        if allowed_hosts:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc in allowed_hosts
        return False

    # Disallow JavaScript URLs
    if url.startswith('javascript:'):
        return False

    # Disallow data URLs
    if url.startswith('data:'):
        return False

    # URL should start with /
    if not url.startswith('/'):
        return False

    # Disallow //example.com type redirects
    if url.startswith('//'):
        return False

    return True


def sanitize_redirect_url(url, fallback='/'):
    """
    Sanitize redirect URL or return fallback.
    """
    if is_safe_redirect_url(url, allowed_hosts=settings.ALLOWED_HOSTS):
        return url
    return fallback
