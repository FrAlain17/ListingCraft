"""
Role-based access control decorators for ListingCraft.
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from .models import UserProfile


def client_required(function=None, redirect_url='/'):
    """
    Decorator for views that checks that the user is logged in and has CLIENT role.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not hasattr(request.user, 'profile'):
                messages.error(request, 'User profile not found. Please contact support.')
                return redirect(redirect_url)

            if not request.user.profile.is_client:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect(redirect_url)

            return view_func(request, *args, **kwargs)
        return _wrapped_view

    if function:
        return decorator(function)
    return decorator


def admin_required(function=None, redirect_url='/'):
    """
    Decorator for views that checks that the user is logged in and has ADMIN role.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not hasattr(request.user, 'profile'):
                messages.error(request, 'User profile not found. Please contact support.')
                return redirect(redirect_url)

            if not request.user.profile.is_admin_user:
                messages.error(request, 'You must be an admin to access this page.')
                return redirect(redirect_url)

            return view_func(request, *args, **kwargs)
        return _wrapped_view

    if function:
        return decorator(function)
    return decorator


def role_required(*allowed_roles, redirect_url='/'):
    """
    Decorator for views that checks that the user has one of the specified roles.

    Usage:
        @role_required(UserProfile.Role.CLIENT, UserProfile.Role.ADMIN)
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not hasattr(request.user, 'profile'):
                messages.error(request, 'User profile not found. Please contact support.')
                return redirect(redirect_url)

            if request.user.profile.role not in allowed_roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect(redirect_url)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
