from rest_framework import serializers
from .models import Category, Condition, Listing, ListingImage, ListingAttribute, Favorite, Inquiry, Report, SavedSearch
from accounts.serializers import UserSerializer
from locations.serializers import StateSerializer, DistrictSerializer, CitySerializer


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    subcategories = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'parent', 'parent_name', 'subcategories', 'is_active', 'sort_order']
    
    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            return CategorySerializer(obj.subcategories.filter(is_active=True), many=True).data
        return []


class ConditionSerializer(serializers.ModelSerializer):
    """Serializer for Condition model"""
    
    class Meta:
        model = Condition
        fields = ['id', 'name', 'description']


class ListingImageSerializer(serializers.ModelSerializer):
    """Serializer for ListingImage model"""
    
    class Meta:
        model = ListingImage
        fields = ['id', 'image', 'caption', 'is_main', 'sort_order']


class ListingAttributeSerializer(serializers.ModelSerializer):
    """Serializer for ListingAttribute model"""
    
    class Meta:
        model = ListingAttribute
        fields = ['id', 'name', 'value']


class ListingSerializer(serializers.ModelSerializer):
    """Serializer for Listing model"""
    seller = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    condition = ConditionSerializer(read_only=True)
    state = StateSerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    images = ListingImageSerializer(many=True, read_only=True)
    attributes = ListingAttributeSerializer(many=True, read_only=True)
    main_image = serializers.SerializerMethodField()
    location_string = serializers.CharField(source='get_location_string', read_only=True)
    is_favorited = serializers.SerializerMethodField()
    
    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'category', 'condition', 'listing_type',
            'price', 'is_negotiable', 'currency', 'seller', 'state', 'district', 'city',
            'address', 'pincode', 'latitude', 'longitude', 'status', 'is_featured',
            'is_urgent', 'is_verified', 'ai_verification_score', 'views', 'favorites_count',
            'inquiries_count', 'tags', 'created_at', 'updated_at', 'expires_at',
            'images', 'attributes', 'main_image', 'location_string', 'is_favorited'
        ]
        read_only_fields = [
            'id', 'seller', 'views', 'favorites_count', 'inquiries_count', 'ai_verification_score',
            'created_at', 'updated_at', 'sold_at'
        ]
    
    def get_main_image(self, obj):
        main_image = obj.get_main_image()
        if main_image:
            return ListingImageSerializer(main_image).data
        return None
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, listing=obj).exists()
        return False


class ListingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating listings"""
    images = ListingImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Listing
        fields = [
            'title', 'description', 'category', 'condition', 'listing_type',
            'price', 'is_negotiable', 'state', 'district', 'city',
            'address', 'pincode', 'latitude', 'longitude', 'tags',
            'images', 'uploaded_images'
        ]
    
    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        listing = Listing.objects.create(**validated_data)
        
        # Create images
        for i, image in enumerate(uploaded_images):
            ListingImage.objects.create(
                listing=listing,
                image=image,
                is_main=(i == 0),
                sort_order=i
            )
        
        return listing


class InquirySerializer(serializers.ModelSerializer):
    """Serializer for Inquiry model"""
    inquirer = UserSerializer(read_only=True)
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    
    class Meta:
        model = Inquiry
        fields = ['id', 'listing', 'listing_title', 'inquirer', 'message', 'phone_number', 'email', 'is_read', 'created_at']
        read_only_fields = ['id', 'inquirer', 'created_at']


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for Favorite model"""
    listing = ListingSerializer(read_only=True)
    
    class Meta:
        model = Favorite
        fields = ['id', 'listing', 'created_at']
        read_only_fields = ['id', 'created_at']


class ReportSerializer(serializers.ModelSerializer):
    """Serializer for Report model"""
    reporter = UserSerializer(read_only=True)
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    
    class Meta:
        model = Report
        fields = ['id', 'listing', 'listing_title', 'reporter', 'reason', 'description', 'is_resolved', 'created_at']
        read_only_fields = ['id', 'reporter', 'created_at']


class SavedSearchSerializer(serializers.ModelSerializer):
    """Serializer for SavedSearch model"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    state_name = serializers.CharField(source='state.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    
    class Meta:
        model = SavedSearch
        fields = [
            'id', 'name', 'query', 'category', 'category_name', 'state', 'state_name',
            'district', 'district_name', 'min_price', 'max_price', 'listing_type',
            'email_alerts', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']