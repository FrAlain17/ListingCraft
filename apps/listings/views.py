from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import models as django_models

from apps.accounts.decorators import client_required
from .models import Listing
from .forms import ListingForm, EditDescriptionForm
from .services import ListingService, DeepSeekService


@login_required
@client_required
def create_listing(request):
    """
    Create a new listing and generate description.
    """
    if request.method == 'POST':
        form = ListingForm(request.POST)

        if form.is_valid():
            # Prepare listing data
            listing_data = form.cleaned_data
            listing_data.pop('key_features_text', None)  # Remove the text field

            # Create listing with description
            listing, success, message = ListingService.create_listing_with_description(
                request.user,
                listing_data
            )

            if success:
                messages.success(request, message)
                return redirect('listings:detail', slug=listing.slug)
            else:
                if listing:
                    # Listing was created but generation failed
                    messages.warning(request, message)
                    return redirect('listings:detail', slug=listing.slug)
                else:
                    messages.error(request, message)
    else:
        form = ListingForm()

    return render(request, 'listings/create.html', {'form': form})


@login_required
@client_required
def listing_detail(request, slug):
    """
    View listing details and generated description.
    """
    listing = get_object_or_404(Listing, slug=slug, user=request.user)

    # Handle description editing
    if request.method == 'POST':
        edit_form = EditDescriptionForm(request.POST, instance=listing)
        if edit_form.is_valid():
            edit_form.save()
            messages.success(request, 'Description updated successfully!')
            return redirect('listings:detail', slug=listing.slug)
    else:
        edit_form = EditDescriptionForm(instance=listing)

    context = {
        'listing': listing,
        'edit_form': edit_form,
    }
    return render(request, 'listings/detail.html', context)


@login_required
@client_required
def listing_list(request):
    """
    View all listings for the current user.
    """
    listings = Listing.objects.filter(user=request.user)

    # Filter by favorites if requested
    if request.GET.get('favorites') == 'true':
        listings = listings.filter(is_favorite=True)

    # Search
    search_query = request.GET.get('search')
    if search_query:
        listings = listings.filter(
            django_models.Q(title__icontains=search_query) |
            django_models.Q(city__icontains=search_query) |
            django_models.Q(generated_description__icontains=search_query)
        )

    context = {
        'listings': listings,
        'search_query': search_query,
    }
    return render(request, 'listings/list.html', context)


@login_required
@client_required
@require_POST
def regenerate_description(request, slug):
    """
    Regenerate description for an existing listing.
    """
    listing = get_object_or_404(Listing, slug=slug, user=request.user)

    success, message = ListingService.regenerate_description(listing)

    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)

    return redirect('listings:detail', slug=listing.slug)


@login_required
@client_required
@require_POST
def toggle_favorite(request, slug):
    """
    Toggle favorite status of a listing.
    """
    listing = get_object_or_404(Listing, slug=slug, user=request.user)

    listing.is_favorite = not listing.is_favorite
    listing.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_favorite': listing.is_favorite
        })

    return redirect('listings:detail', slug=listing.slug)


@login_required
@client_required
@require_POST
def delete_listing(request, slug):
    """
    Delete a listing.
    """
    listing = get_object_or_404(Listing, slug=slug, user=request.user)

    listing.delete()
    messages.success(request, 'Listing deleted successfully.')

    return redirect('listings:list')


@login_required
@client_required
def edit_listing(request, slug):
    """
    Edit listing details (not description).
    """
    listing = get_object_or_404(Listing, slug=slug, user=request.user)

    if request.method == 'POST':
        form = ListingForm(request.POST, instance=listing)

        if form.is_valid():
            form.save()
            messages.success(request, 'Listing updated successfully!')
            return redirect('listings:detail', slug=listing.slug)
    else:
        form = ListingForm(instance=listing)

    context = {
        'form': form,
        'listing': listing,
    }
    return render(request, 'listings/edit.html', context)
