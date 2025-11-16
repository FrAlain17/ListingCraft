from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    # List and create
    path('', views.listing_list, name='list'),
    path('create/', views.create_listing, name='create'),

    # Detail and actions
    path('<slug:slug>/', views.listing_detail, name='detail'),
    path('<slug:slug>/edit/', views.edit_listing, name='edit'),
    path('<slug:slug>/delete/', views.delete_listing, name='delete'),
    path('<slug:slug>/regenerate/', views.regenerate_description, name='regenerate'),
    path('<slug:slug>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
]
