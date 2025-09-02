from rest_framework import serializers
from .models import SearchLog, PopularSearch, SearchSuggestion


class SearchLogSerializer(serializers.ModelSerializer):
    """Serializer for SearchLog model"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SearchLog
        fields = ['id', 'query', 'category', 'location', 'results_count', 'user_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class PopularSearchSerializer(serializers.ModelSerializer):
    """Serializer for PopularSearch model"""
    
    class Meta:
        model = PopularSearch
        fields = ['id', 'query', 'search_count', 'last_searched']


class SearchSuggestionSerializer(serializers.ModelSerializer):
    """Serializer for SearchSuggestion model"""
    
    class Meta:
        model = SearchSuggestion
        fields = ['id', 'text', 'category', 'popularity_score']