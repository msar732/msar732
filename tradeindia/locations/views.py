from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import ListView
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import State, District, City
from .serializers import StateSerializer, DistrictSerializer, CitySerializer


class StateViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for State model"""
    queryset = State.objects.all()
    serializer_class = StateSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name']
    ordering = ['name']


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for District model"""
    queryset = District.objects.select_related('state').all()
    serializer_class = DistrictSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['state']
    search_fields = ['name', 'code']
    ordering_fields = ['name']
    ordering = ['name']


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for City model"""
    queryset = City.objects.select_related('state', 'district').all()
    serializer_class = CitySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['state', 'district']
    search_fields = ['name', 'pincode']
    ordering_fields = ['name']
    ordering = ['name']


class StateListView(ListView):
    """List view for states"""
    model = State
    template_name = 'locations/states.html'
    context_object_name = 'states'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Indian States and Union Territories'
        return context


class DistrictListView(ListView):
    """List view for districts by state"""
    model = District
    template_name = 'locations/districts.html'
    context_object_name = 'districts'
    
    def get_queryset(self):
        state_id = self.kwargs.get('state_id')
        return District.objects.filter(state_id=state_id).select_related('state')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        state_id = self.kwargs.get('state_id')
        try:
            state = State.objects.get(id=state_id)
            context['state'] = state
            context['title'] = f'Districts in {state.name}'
        except State.DoesNotExist:
            context['title'] = 'Districts'
        return context


class CityListView(ListView):
    """List view for cities by district"""
    model = City
    template_name = 'locations/cities.html'
    context_object_name = 'cities'
    
    def get_queryset(self):
        district_id = self.kwargs.get('district_id')
        return City.objects.filter(district_id=district_id).select_related('state', 'district')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        district_id = self.kwargs.get('district_id')
        try:
            district = District.objects.select_related('state').get(id=district_id)
            context['district'] = district
            context['title'] = f'Cities in {district.name}, {district.state.name}'
        except District.DoesNotExist:
            context['title'] = 'Cities'
        return context


def get_districts_ajax(request):
    """AJAX view to get districts by state"""
    state_id = request.GET.get('state_id')
    if state_id:
        districts = District.objects.filter(state_id=state_id).values('id', 'name')
        return JsonResponse({'districts': list(districts)})
    return JsonResponse({'districts': []})


def get_cities_ajax(request):
    """AJAX view to get cities by district"""
    district_id = request.GET.get('district_id')
    if district_id:
        cities = City.objects.filter(district_id=district_id).values('id', 'name')
        return JsonResponse({'cities': list(cities)})
    return JsonResponse({'cities': []})