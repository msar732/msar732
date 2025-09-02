"""
Views for listings app
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q, Count, Avg, F
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import (
    Listing, ListingImage, ListingVideo, ListingAttribute, 
    ListingAttributeValue, ListingFavorite, ListingView, ListingReport
)
from .forms import ListingForm, ListingImageFormSet, ListingReportForm
from apps.core.models import Category, State, District, City
import json


class ListingListView(ListView):
    """List all active listings with filters"""
    model = Listing
    template_name = 'listings/list.html'
    context_object_name = 'listings'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Listing.objects.filter(status='active').select_related(
            'user', 'category', 'state', 'district', 'city'
        ).prefetch_related('images', 'tags')
        
        # Search query
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | 
                Q(description__icontains=q) |
                Q(tags__name__icontains=q)
            ).distinct()
        
        # Category filter
        category_slug = self.request.GET.get('category') or self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            # Include subcategories
            categories = category.get_descendants(include_self=True)
            queryset = queryset.filter(category__in=categories)
        
        # Location filters
        state = self.request.GET.get('state')
        if state:
            queryset = queryset.filter(state__code=state)
        
        district = self.request.GET.get('district')
        if district:
            queryset = queryset.filter(district__slug=district)
        
        city = self.request.GET.get('city')
        if city:
            queryset = queryset.filter(city__slug=city)
        
        # Price range
        price_min = self.request.GET.get('price_min')
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        
        price_max = self.request.GET.get('price_max')
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
        
        # Listing type
        listing_type = self.request.GET.get('type')
        if listing_type:
            queryset = queryset.filter(listing_type=listing_type)
        
        # Condition
        condition = self.request.GET.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)
        
        # Featured filter
        featured = self.request.GET.get('featured')
        if featured:
            queryset = queryset.filter(is_featured=True)
        
        # Sorting
        sort = self.request.GET.get('sort', '-created_at')
        if sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort == 'popular':
            queryset = queryset.order_by('-views')
        elif sort == 'oldest':
            queryset = queryset.order_by('created_at')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter options
        context['states'] = State.objects.filter(is_active=True)
        context['listing_types'] = Listing.LISTING_TYPE_CHOICES
        context['conditions'] = Listing.CONDITION_CHOICES
        
        # Current filters
        context['current_filters'] = {
            'q': self.request.GET.get('q', ''),
            'category': self.request.GET.get('category', ''),
            'state': self.request.GET.get('state', ''),
            'district': self.request.GET.get('district', ''),
            'city': self.request.GET.get('city', ''),
            'price_min': self.request.GET.get('price_min', ''),
            'price_max': self.request.GET.get('price_max', ''),
            'type': self.request.GET.get('type', ''),
            'condition': self.request.GET.get('condition', ''),
            'featured': self.request.GET.get('featured', ''),
            'sort': self.request.GET.get('sort', '-created_at'),
        }
        
        # Category info if filtered
        category_slug = self.request.GET.get('category') or self.kwargs.get('category_slug')
        if category_slug:
            context['current_category'] = get_object_or_404(Category, slug=category_slug)
        
        return context


class ListingDetailView(DetailView):
    """Display single listing details"""
    model = Listing
    template_name = 'listings/detail.html'
    context_object_name = 'listing'
    
    def get_queryset(self):
        return Listing.objects.select_related(
            'user', 'user__profile', 'category', 'state', 'district', 'city'
        ).prefetch_related(
            'images', 'videos', 'tags', 'attribute_values__attribute'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        listing = self.object
        
        # Increment views
        if not self.request.user == listing.user:
            # Track view
            ip_address = self.request.META.get('REMOTE_ADDR')
            user_agent = self.request.META.get('HTTP_USER_AGENT', '')
            session_id = self.request.session.session_key
            
            # Check if unique view
            recent_view = ListingView.objects.filter(
                listing=listing,
                ip_address=ip_address,
                viewed_at__gte=timezone.now() - timezone.timedelta(hours=24)
            ).exists()
            
            if not recent_view:
                listing.increment_views(unique=True)
            else:
                listing.increment_views(unique=False)
            
            # Record view
            ListingView.objects.create(
                listing=listing,
                user=self.request.user if self.request.user.is_authenticated else None,
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id or '',
                referrer=self.request.META.get('HTTP_REFERER', '')
            )
        
        # Check if favorited
        if self.request.user.is_authenticated:
            context['is_favorited'] = ListingFavorite.objects.filter(
                user=self.request.user,
                listing=listing
            ).exists()
        
        # Related listings
        context['related_listings'] = Listing.objects.filter(
            status='active',
            category=listing.category
        ).exclude(id=listing.id).select_related(
            'user', 'state', 'district'
        ).prefetch_related('images')[:8]
        
        # More from seller
        context['seller_listings'] = Listing.objects.filter(
            status='active',
            user=listing.user
        ).exclude(id=listing.id).select_related(
            'category', 'state', 'district'
        ).prefetch_related('images')[:4]
        
        # Listing attributes
        context['attributes'] = listing.attribute_values.select_related('attribute')
        
        return context


class ListingCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Create new listing"""
    model = Listing
    form_class = ListingForm
    template_name = 'listings/create.html'
    success_message = "Your listing has been created successfully!"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = ListingImageFormSet(
                self.request.POST,
                self.request.FILES,
                prefix='images'
            )
        else:
            context['image_formset'] = ListingImageFormSet(prefix='images')
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        
        if image_formset.is_valid():
            # Save listing
            form.instance.user = self.request.user
            
            # Set contact details from user if not provided
            if not form.instance.contact_name:
                form.instance.contact_name = self.request.user.get_full_name() or self.request.user.username
            if not form.instance.contact_phone:
                form.instance.contact_phone = str(self.request.user.phone_number) if self.request.user.phone_number else ''
            if not form.instance.contact_email:
                form.instance.contact_email = self.request.user.email
            
            # Set status based on settings
            from apps.core.models import SiteConfiguration
            config = SiteConfiguration.get_solo()
            if config.listing_approval_required:
                form.instance.status = 'pending'
            else:
                form.instance.status = 'active'
                form.instance.published_at = timezone.now()
            
            self.object = form.save()
            
            # Save images
            image_formset.instance = self.object
            images = image_formset.save()
            
            # Set first image as primary if none selected
            if images and not any(img.is_primary for img in images):
                images[0].is_primary = True
                images[0].save()
            
            # Handle dynamic attributes
            self._save_attributes(form)
            
            return super().form_valid(form)
        else:
            return self.form_invalid(form)
    
    def _save_attributes(self, form):
        """Save dynamic attributes based on category"""
        category = self.object.category
        attributes = ListingAttribute.objects.filter(category=category)
        
        for attribute in attributes:
            value = form.cleaned_data.get(f'attribute_{attribute.id}')
            if value is not None:
                attr_value = ListingAttributeValue(
                    listing=self.object,
                    attribute=attribute
                )
                
                # Set appropriate value field based on type
                if attribute.field_type == 'text':
                    attr_value.value_text = value
                elif attribute.field_type == 'number':
                    attr_value.value_number = value
                elif attribute.field_type == 'decimal':
                    attr_value.value_decimal = value
                elif attribute.field_type == 'boolean':
                    attr_value.value_boolean = value
                elif attribute.field_type == 'date':
                    attr_value.value_date = value
                elif attribute.field_type in ['choice', 'multiple_choice']:
                    attr_value.value_json = value
                
                attr_value.save()
    
    def get_success_url(self):
        if self.object.status == 'pending':
            messages.info(
                self.request,
                "Your listing is pending approval. You'll be notified once it's approved."
            )
            return reverse_lazy('listings:my_listings')
        return self.object.get_absolute_url()


class ListingUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """Update existing listing"""
    model = Listing
    form_class = ListingForm
    template_name = 'listings/update.html'
    success_message = "Your listing has been updated successfully!"
    
    def test_func(self):
        return self.get_object().user == self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = ListingImageFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object,
                prefix='images'
            )
        else:
            context['image_formset'] = ListingImageFormSet(
                instance=self.object,
                prefix='images'
            )
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        
        if image_formset.is_valid():
            self.object = form.save()
            image_formset.save()
            
            # Update attributes
            self._update_attributes(form)
            
            return super().form_valid(form)
        else:
            return self.form_invalid(form)
    
    def _update_attributes(self, form):
        """Update dynamic attributes"""
        # Similar to _save_attributes in CreateView
        pass


class ListingDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """Delete listing"""
    model = Listing
    template_name = 'listings/delete.html'
    success_url = reverse_lazy('listings:my_listings')
    success_message = "Your listing has been deleted successfully!"
    
    def test_func(self):
        return self.get_object().user == self.request.user
    
    def delete(self, request, *args, **kwargs):
        # Soft delete - just change status
        self.object = self.get_object()
        self.object.status = 'archived'
        self.object.save()
        messages.success(self.request, self.success_message)
        return redirect(self.success_url)


class MyListingsView(LoginRequiredMixin, ListView):
    """User's own listings"""
    model = Listing
    template_name = 'listings/my_listings.html'
    context_object_name = 'listings'
    paginate_by = 20
    
    def get_queryset(self):
        return Listing.objects.filter(
            user=self.request.user
        ).exclude(
            status='archived'
        ).select_related(
            'category', 'state', 'district'
        ).prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics
        context['stats'] = {
            'active': self.request.user.listings.filter(status='active').count(),
            'pending': self.request.user.listings.filter(status='pending').count(),
            'sold': self.request.user.listings.filter(status='sold').count(),
            'expired': self.request.user.listings.filter(status='expired').count(),
            'total_views': self.request.user.listings.aggregate(
                total=models.Sum('views')
            )['total'] or 0,
        }
        
        return context


class FavoriteListingsView(LoginRequiredMixin, ListView):
    """User's favorite listings"""
    model = ListingFavorite
    template_name = 'listings/favorites.html'
    context_object_name = 'favorites'
    paginate_by = 20
    
    def get_queryset(self):
        return ListingFavorite.objects.filter(
            user=self.request.user
        ).select_related(
            'listing__user',
            'listing__category',
            'listing__state',
            'listing__district'
        ).prefetch_related('listing__images')


# AJAX Views
@login_required
@require_POST
def toggle_favorite(request, pk):
    """Toggle favorite status for a listing"""
    listing = get_object_or_404(Listing, pk=pk, status='active')
    
    favorite, created = ListingFavorite.objects.get_or_create(
        user=request.user,
        listing=listing
    )
    
    if not created:
        favorite.delete()
        is_favorited = False
        listing.favorites = F('favorites') - 1
    else:
        is_favorited = True
        listing.favorites = F('favorites') + 1
    
    listing.save(update_fields=['favorites'])
    
    return JsonResponse({
        'is_favorited': is_favorited,
        'favorites_count': listing.favorites
    })


@login_required
@require_POST
def report_listing(request, pk):
    """Report a listing"""
    listing = get_object_or_404(Listing, pk=pk, status='active')
    
    if listing.user == request.user:
        return HttpResponseForbidden("You cannot report your own listing")
    
    form = ListingReportForm(request.POST)
    if form.is_valid():
        report = form.save(commit=False)
        report.listing = listing
        report.reporter = request.user
        
        # Check if already reported for same reason
        existing = ListingReport.objects.filter(
            listing=listing,
            reporter=request.user,
            reason=report.reason
        ).exists()
        
        if not existing:
            report.save()
            messages.success(request, "Thank you for reporting. We'll review it soon.")
        else:
            messages.info(request, "You have already reported this listing for the same reason.")
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'errors': form.errors})


@login_required
@require_POST
def mark_as_sold(request, pk):
    """Mark listing as sold"""
    listing = get_object_or_404(Listing, pk=pk, user=request.user)
    
    if listing.status == 'active':
        listing.status = 'sold'
        listing.sold_at = timezone.now()
        listing.save()
        messages.success(request, "Listing marked as sold!")
    
    return redirect('listings:my_listings')


def get_attributes(request):
    """Get dynamic attributes for a category (AJAX)"""
    category_id = request.GET.get('category')
    if not category_id:
        return JsonResponse({'attributes': []})
    
    attributes = ListingAttribute.objects.filter(
        category_id=category_id
    ).values('id', 'name', 'field_type', 'choices', 'unit', 
             'help_text', 'is_required').order_by('order')
    
    return JsonResponse({'attributes': list(attributes)})