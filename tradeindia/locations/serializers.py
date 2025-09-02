from rest_framework import serializers
from .models import State, District, City


class StateSerializer(serializers.ModelSerializer):
    """Serializer for State model"""
    districts_count = serializers.IntegerField(source='districts.count', read_only=True)
    
    class Meta:
        model = State
        fields = ['id', 'name', 'code', 'districts_count']


class DistrictSerializer(serializers.ModelSerializer):
    """Serializer for District model"""
    state_name = serializers.CharField(source='state.name', read_only=True)
    cities_count = serializers.IntegerField(source='cities.count', read_only=True)
    
    class Meta:
        model = District
        fields = ['id', 'name', 'code', 'state', 'state_name', 'cities_count']


class CitySerializer(serializers.ModelSerializer):
    """Serializer for City model"""
    state_name = serializers.CharField(source='state.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    
    class Meta:
        model = City
        fields = ['id', 'name', 'district', 'district_name', 'state', 'state_name', 'pincode', 'latitude', 'longitude']