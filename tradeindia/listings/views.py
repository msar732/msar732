from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Condition, Listing, ListingImage, Favorite, Inquiry, Report
from .serializers import (
    CategorySerializer, ListingSerializer, ListingCreateSerializer,
    InquirySerializer, FavoriteSerializer, ReportSerializer
)
from .filters import ListingFilter
from .tasks import verify_listing_with_ai


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for Category model"""
    queryset = Category.objects.filter(is_active=True).prefetch_related('subcategories')
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['sort_order', 'name']
    ordering = ['sort_order', 'name']


class ListingViewSet(viewsets.ModelViewSet):
    """API ViewSet for Listing model"""
    queryset = Listing.objects.filter(status='active', is_verified=True).select_related(
        'seller', 'category', 'condition', 'state', 'district', 'city'
    ).prefetch_related('images', 'attributes')
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ListingFilter
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['created_at', 'price', 'views', 'favorites']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ListingCreateSerializer
        return ListingSerializer
    
    def perform_create(self, serializer):
        listing = serializer.save(seller=self.request.user)
        # Trigger AI verification
        verify_listing_with_ai.delay(listing.id)
    
    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        """Add/remove listing from favorites"""
        listing = self.get_object()
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            listing=listing
        )
        
        if not created:
            favorite.delete()
            listing.favorites_count -= 1
            listing.save(update_fields=['favorites_count'])
            return Response({'status': 'removed'})
        
        listing.favorites_count += 1
        listing.save(update_fields=['favorites_count'])
        return Response({'status': 'added'})
    
    @action(detail=True, methods=['post'])
    def inquire(self, request, pk=None):
        """Create an inquiry for a listing"""
        listing = self.get_object()
        serializer = InquirySerializer(data=request.data)
        
        if serializer.is_valid():
            inquiry = serializer.save(inquirer=request.user, listing=listing)
            listing.inquiries_count += 1
            listing.save(update_fields=['inquiries_count'])
            return Response(InquirySerializer(inquiry).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        """Report a listing"""
        listing = self.get_object()
        serializer = ReportSerializer(data=request.data)
        
        if serializer.is_valid():
            report = serializer.save(reporter=request.user, listing=listing)
            return Response(ReportSerializer(report).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """Get similar listings"""
        listing = self.get_object()
        similar_listings = Listing.objects.filter(
            category=listing.category,
            status='active',
            is_verified=True
        ).exclude(id=listing.id).select_related(
            'seller', 'category', 'state', 'district'
        ).prefetch_related('images')[:10]
        
        serializer = ListingSerializer(similar_listings, many=True, context={'request': request})
        return Response(serializer.data)


class InquiryViewSet(viewsets.ModelViewSet):
    """API ViewSet for Inquiry model"""
    serializer_class = InquirySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see inquiries for their own listings or inquiries they made
        return Inquiry.objects.filter(
            Q(listing__seller=self.request.user) | Q(inquirer=self.request.user)
        ).select_related('listing', 'inquirer')


class ListingListView(ListView):
    """List view for listings"""
    model = Listing
    template_name = 'listings/list.html'
    context_object_name = 'listings'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Listing.objects.filter(
            status='active', is_verified=True
        ).select_related(
            'seller', 'category', 'condition', 'state', 'district', 'city'
        ).prefetch_related('images')
        
        # Apply filters
        category = self.request.GET.get('category')
        state = self.request.GET.get('state')
        district = self.request.GET.get('district')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        listing_type = self.request.GET.get('listing_type')
        query = self.request.GET.get('q')
        
        if category:
            queryset = queryset.filter(category_id=category)
        if state:
            queryset = queryset.filter(state_id=state)
        if district:
            queryset = queryset.filter(district_id=district)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if listing_type:
            queryset = queryset.filter(listing_type=listing_type)
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__icontains=query)
            )
        
        # Ordering
        order_by = self.request.GET.get('order_by', '-created_at')
        if order_by in ['created_at', '-created_at', 'price', '-price', 'views', '-views']:
            queryset = queryset.order_by(order_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': Category.objects.filter(is_active=True, parent__isnull=True),
            'conditions': Condition.objects.all(),
            'listing_types': Listing.LISTING_TYPE_CHOICES,
            'current_filters': self.request.GET,
        })
        return context


class ListingDetailView(DetailView):
    """Detail view for a single listing"""
    model = Listing
    template_name = 'listings/detail.html'
    context_object_name = 'listing'
    
    def get_queryset(self):
        return Listing.objects.select_related(
            'seller', 'category', 'condition', 'state', 'district', 'city'
        ).prefetch_related('images', 'attributes')
    
    def get_object(self):
        obj = super().get_object()
        # Increment view count
        obj.increment_views()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        listing = context['listing']
        
        # Get similar listings
        similar_listings = Listing.objects.filter(
            category=listing.category,
            status='active',
            is_verified=True
        ).exclude(id=listing.id).select_related(
            'seller', 'category', 'state', 'district'
        ).prefetch_related('images')[:6]
        
        context.update({
            'similar_listings': similar_listings,
            'is_favorited': False,
        })
        
        if self.request.user.is_authenticated:
            context['is_favorited'] = Favorite.objects.filter(
                user=self.request.user, listing=listing
            ).exists()
        
        return context


class ListingCreateView(LoginRequiredMixin, CreateView):
    """Create view for new listings"""
    model = Listing
    template_name = 'listings/create.html'
    fields = [
        'title', 'description', 'category', 'condition', 'listing_type',
        'price', 'is_negotiable', 'state', 'district', 'city',
        'address', 'pincode', 'tags'
    ]
    
    def form_valid(self, form):
        form.instance.seller = self.request.user
        response = super().form_valid(form)
        
        # Handle image uploads
        images = self.request.FILES.getlist('images')
        for i, image in enumerate(images):
            ListingImage.objects.create(
                listing=self.object,
                image=image,
                is_main=(i == 0),
                sort_order=i
            )
        
        # Trigger AI verification
        verify_listing_with_ai.delay(self.object.id)
        
        messages.success(self.request, 'Listing created successfully! It will be reviewed before going live.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': Category.objects.filter(is_active=True),
            'conditions': Condition.objects.all(),
        })
        return context


class ListingEditView(LoginRequiredMixin, UpdateView):
    """Edit view for listings"""
    model = Listing
    template_name = 'listings/edit.html'
    fields = [
        'title', 'description', 'category', 'condition', 'listing_type',
        'price', 'is_negotiable', 'state', 'district', 'city',
        'address', 'pincode', 'tags'
    ]
    
    def get_queryset(self):
        return Listing.objects.filter(seller=self.request.user)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Listing updated successfully!')
        return response


class ListingDeleteView(LoginRequiredMixin, DeleteView):
    """Delete view for listings"""
    model = Listing
    template_name = 'listings/delete.html'
    success_url = '/accounts/my-listings/'
    
    def get_queryset(self):
        return Listing.objects.filter(seller=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Listing deleted successfully!')
        return super().delete(request, *args, **kwargs)


class CategoryListingView(ListView):
    """List view for listings in a specific category"""
    model = Listing
    template_name = 'listings/category.html'
    context_object_name = 'listings'
    paginate_by = 20
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Listing.objects.filter(
            category=self.category,
            status='active',
            is_verified=True
        ).select_related(
            'seller', 'category', 'state', 'district'
        ).prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class FeaturedListingsView(ListView):
    """List view for featured listings"""
    model = Listing
    template_name = 'listings/featured.html'
    context_object_name = 'listings'
    paginate_by = 20
    
    def get_queryset(self):
        return Listing.objects.filter(
            status='active',
            is_verified=True,
            is_featured=True
        ).select_related(
            'seller', 'category', 'state', 'district'
        ).prefetch_related('images').order_by('-created_at')


class FavoriteToggleView(LoginRequiredMixin, View):
    """Toggle favorite status for a listing"""
    
    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            listing=listing
        )
        
        if not created:
            favorite.delete()
            listing.favorites -= 1
            listing.save(update_fields=['favorites'])
            return JsonResponse({'status': 'removed', 'favorited': False})
        
        listing.favorites += 1
        listing.save(update_fields=['favorites'])
        return JsonResponse({'status': 'added', 'favorited': True})


class InquiryCreateView(LoginRequiredMixin, View):
    """Create an inquiry for a listing"""
    
    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        message = request.POST.get('message', '')
        phone_number = request.POST.get('phone_number', '')
        email = request.POST.get('email', request.user.email)
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        inquiry = Inquiry.objects.create(
            listing=listing,
            inquirer=request.user,
            message=message,
            phone_number=phone_number,
            email=email
        )
        
        listing.inquiries += 1
        listing.save(update_fields=['inquiries'])
        
        messages.success(request, 'Your inquiry has been sent successfully!')
        return JsonResponse({'status': 'success'})


class ReportCreateView(LoginRequiredMixin, View):
    """Report a listing"""
    
    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        reason = request.POST.get('reason')
        description = request.POST.get('description', '')
        
        if not reason:
            return JsonResponse({'error': 'Reason is required'}, status=400)
        
        report, created = Report.objects.get_or_create(
            listing=listing,
            reporter=request.user,
            defaults={'reason': reason, 'description': description}
        )
        
        if created:
            messages.success(request, 'Report submitted successfully!')
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'error': 'You have already reported this listing'}, status=400)