# API Views
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from listings.models import Listing, Category, State, District
from .serializers import ListingSerializer, CategorySerializer, StateSerializer, DistrictSerializer

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.filter(status='active').select_related(
        'user', 'category', 'state', 'district'
    ).prefetch_related('images')
    serializer_class = ListingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'state', 'district', 'condition']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'ai_genuineness_score']
    ordering = ['-ai_genuineness_score', '-created_at']
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_listings = self.queryset.filter(is_featured=True)[:10]
        serializer = self.get_serializer(featured_listings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def verified(self, request):
        verified_listings = self.queryset.filter(is_verified=True)
        page = self.paginate_queryset(verified_listings)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer

class StateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer

class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = District.objects.select_related('state')
    serializer_class = DistrictSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['state']