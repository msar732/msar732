from rest_framework import serializers
from listings.models import Listing, Category, State, District, ListingImage
from accounts.models import CustomUser

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'description']

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name', 'code']

class DistrictSerializer(serializers.ModelSerializer):
    state = StateSerializer(read_only=True)
    
    class Meta:
        model = District
        fields = ['id', 'name', 'state']

class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ['id', 'image', 'thumbnail', 'alt_text', 'is_primary']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'profile_image', 'trust_score']

class ListingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    images = ListingImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Listing
        fields = [
            'id', 'user', 'category', 'title', 'description', 'price',
            'condition', 'status', 'state', 'district', 'address',
            'contact_phone', 'is_negotiable', 'is_featured', 'is_verified',
            'ai_genuineness_score', 'view_count', 'created_at', 'images'
        ]