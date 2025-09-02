from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import MotorListing, MotorCategory, MotorMake

class MotorHomeView(TemplateView):
    template_name = 'motors/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = MotorCategory.objects.filter(is_active=True)
        context['popular_makes'] = MotorMake.objects.all()[:10]
        context['featured_motors'] = MotorListing.objects.filter(
            is_featured=True, status='active'
        )[:8]
        return context

class CarsView(ListView):
    model = MotorListing
    template_name = 'motors/cars.html'
    context_object_name = 'cars'
    paginate_by = 20
    
    def get_queryset(self):
        return MotorListing.objects.filter(
            category__name='cars',
            status='active'
        ).order_by('-created_at')

class MotorcyclesView(ListView):
    model = MotorListing
    template_name = 'motors/motorcycles.html'
    context_object_name = 'motorcycles'
    paginate_by = 20
    
    def get_queryset(self):
        return MotorListing.objects.filter(
            category__name='motorcycles',
            status='active'
        ).order_by('-created_at')

class TrucksView(ListView):
    model = MotorListing
    template_name = 'motors/trucks.html'
    context_object_name = 'trucks'
    paginate_by = 20
    
    def get_queryset(self):
        return MotorListing.objects.filter(
            category__name='trucks',
            status='active'
        ).order_by('-created_at')

class BoatsView(ListView):
    model = MotorListing
    template_name = 'motors/boats.html'
    context_object_name = 'boats'
    paginate_by = 20
    
    def get_queryset(self):
        return MotorListing.objects.filter(
            category__name='boats',
            status='active'
        ).order_by('-created_at')

class CaravansView(ListView):
    model = MotorListing
    template_name = 'motors/caravans.html'
    context_object_name = 'caravans'
    paginate_by = 20
    
    def get_queryset(self):
        return MotorListing.objects.filter(
            category__name='caravans',
            status='active'
        ).order_by('-created_at')

class PartsView(ListView):
    model = MotorListing
    template_name = 'motors/parts.html'
    context_object_name = 'parts'
    paginate_by = 20
    
    def get_queryset(self):
        return MotorListing.objects.filter(
            category__name='parts',
            status='active'
        ).order_by('-created_at')

class CreateMotorView(LoginRequiredMixin, CreateView):
    model = MotorListing
    template_name = 'motors/create.html'
    fields = ['category', 'make', 'model', 'title', 'description', 'price', 'condition', 
              'year', 'mileage', 'fuel_type', 'transmission', 'contact_phone']
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class MotorDetailView(DetailView):
    model = MotorListing
    template_name = 'motors/detail.html'
    context_object_name = 'motor'
    pk_url_kwarg = 'listing_id'