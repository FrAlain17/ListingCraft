from django.urls import path
from . import views, admin_views

app_name = 'dashboard'

urlpatterns = [
    # Client Dashboard
    path('', views.dashboard_overview, name='overview'),

    # Admin Dashboard
    path('admin/', admin_views.admin_dashboard, name='admin'),
    path('admin/users/', admin_views.user_management, name='user_management'),
    path('admin/users/<int:user_id>/', admin_views.user_detail, name='user_detail'),
    path('admin/analytics/', admin_views.analytics, name='analytics'),
    path('admin/subscriptions/', admin_views.subscription_management, name='subscription_management'),
]
