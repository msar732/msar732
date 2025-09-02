from rest_framework import serializers
from .models import User, UserRating, UserFollowing
from locations.serializers import StateSerializer, DistrictSerializer, CitySerializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    state = StateSerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    full_location = serializers.CharField(source='get_full_location', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'profile_picture', 'bio', 'date_of_birth',
            'state', 'district', 'city', 'full_location', 'address', 'pincode',
            'is_verified', 'rating', 'total_ratings', 'total_listings',
            'successful_trades', 'last_active', 'date_joined'
        ]
        read_only_fields = [
            'id', 'is_verified', 'rating', 'total_ratings', 'total_listings',
            'successful_trades', 'last_active', 'date_joined'
        ]


class UserRatingSerializer(serializers.ModelSerializer):
    """Serializer for UserRating model"""
    rater_name = serializers.CharField(source='rater.username', read_only=True)
    
    class Meta:
        model = UserRating
        fields = ['id', 'rating', 'review', 'rater_name', 'created_at']
        read_only_fields = ['id', 'rater_name', 'created_at']


class UserFollowingSerializer(serializers.ModelSerializer):
    """Serializer for UserFollowing model"""
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)
    
    class Meta:
        model = UserFollowing
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['id', 'created_at']