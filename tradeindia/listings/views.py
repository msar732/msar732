from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Listing, Category

class ListingHomeView(ListView):
    model = Listing
    template_name = 'listings/home.html'
    context_object_name = 'listings'
    paginate_by = 20
    
    def get_queryset(self):
        return Listing.objects.filter(status='active').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['featured_listings'] = Listing.objects.filter(
            is_featured=True, status='active'
        )[:8]
        return context

class CreateListingView(LoginRequiredMixin, CreateView):
    model = Listing
    template_name = 'listings/create.html'
    fields = ['category', 'title', 'description', 'price', 'condition', 
              'state', 'district', 'address', 'contact_phone', 'contact_email']
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class ListingDetailView(DetailView):
    model = Listing
    template_name = 'listings/detail.html'
    context_object_name = 'listing'
    pk_url_kwarg = 'listing_id'