"""
Custom middleware for security and rate limiting.
"""
import time
from django.core.cache import cache
from django.http import HttpResponseForbidden, JsonResponse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """
    Simple rate limiting middleware using cache.
    Limits requests per IP address.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = getattr(settings, 'RATE_LIMIT_REQUESTS', 100)  # requests
        self.rate_limit_period = getattr(settings, 'RATE_LIMIT_PERIOD', 60)  # seconds

    def __call__(self, request):
        # Skip rate limiting for authenticated staff users
        if request.user.is_authenticated and request.user.is_staff:
            return self.get_response(request)

        # Get client IP
        ip_address = self.get_client_ip(request)

        # Check rate limit
        cache_key = f'rate_limit:{ip_address}'
        requests = cache.get(cache_key, 0)

        if requests >= self.rate_limit:
            logger.warning(f'Rate limit exceeded for IP: {ip_address}')
            return JsonResponse({
                'error': 'Rate limit exceeded. Please try again later.'
            }, status=429)

        # Increment request count
        if requests == 0:
            cache.set(cache_key, 1, self.rate_limit_period)
        else:
            cache.incr(cache_key)

        response = self.get_response(request)
        return response

    @staticmethod
    def get_client_ip(request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware:
    """
    Add additional security headers to responses.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'same-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

        # Content Security Policy (basic)
        if not settings.DEBUG:
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://api.stripe.com https://api.deepseek.com; "
                "frame-src https://js.stripe.com;"
            )
            response['Content-Security-Policy'] = csp

        return response


class RequestLoggingMiddleware:
    """
    Log all requests for security monitoring.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request details
        start_time = time.time()

        # Get response
        response = self.get_response(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log suspicious activity
        if response.status_code >= 400:
            logger.warning(
                f'{request.method} {request.path} '
                f'- Status: {response.status_code} '
                f'- IP: {self.get_client_ip(request)} '
                f'- User: {request.user if request.user.is_authenticated else "Anonymous"} '
                f'- Duration: {duration:.2f}s'
            )

        # Log slow requests
        if duration > 5:
            logger.warning(
                f'Slow request: {request.method} {request.path} '
                f'took {duration:.2f}s'
            )

        return response

    @staticmethod
    def get_client_ip(request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class APIRateLimitMiddleware:
    """
    Stricter rate limiting for AI description generation endpoints.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Stricter limits for AI endpoints
        self.api_rate_limit = getattr(settings, 'API_RATE_LIMIT_REQUESTS', 10)  # requests
        self.api_rate_limit_period = getattr(settings, 'API_RATE_LIMIT_PERIOD', 60)  # seconds

    def __call__(self, request):
        # Only apply to listing creation/regeneration endpoints
        if not self.is_ai_endpoint(request.path):
            return self.get_response(request)

        # Skip for staff
        if request.user.is_authenticated and request.user.is_staff:
            return self.get_response(request)

        # Get user or IP identifier
        if request.user.is_authenticated:
            identifier = f'user:{request.user.id}'
        else:
            identifier = f'ip:{self.get_client_ip(request)}'

        # Check rate limit
        cache_key = f'api_rate_limit:{identifier}'
        requests = cache.get(cache_key, 0)

        if requests >= self.api_rate_limit:
            logger.warning(f'API rate limit exceeded for {identifier}')
            return JsonResponse({
                'error': 'Too many requests. Please wait before generating more descriptions.'
            }, status=429)

        # Increment request count
        if requests == 0:
            cache.set(cache_key, 1, self.api_rate_limit_period)
        else:
            cache.incr(cache_key)

        response = self.get_response(request)
        return response

    @staticmethod
    def is_ai_endpoint(path):
        """Check if path is an AI generation endpoint."""
        ai_paths = ['/listings/create/', '/listings/', '/regenerate/']
        return any(ai_path in path for ai_path in ai_paths)

    @staticmethod
    def get_client_ip(request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
