"""
URL configuration for ListingCraft project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Authentication (django-allauth)
    path('accounts/', include('allauth.urls')),

    # App URLs
    path('', include('apps.landing.urls', namespace='landing')),
    path('subscriptions/', include('apps.subscriptions.urls', namespace='subscriptions')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('listings/', include('apps.listings.urls', namespace='listings')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
