from django.contrib import admin
from .models import SearchLog, PopularSearch, SearchSuggestion


@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    list_display = ['query', 'user', 'category', 'location', 'results_count', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['query', 'user__username', 'location']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(PopularSearch)
class PopularSearchAdmin(admin.ModelAdmin):
    list_display = ['query', 'search_count', 'last_searched', 'created_at']
    list_filter = ['last_searched', 'created_at']
    search_fields = ['query']
    readonly_fields = ['created_at', 'last_searched']
    ordering = ['-search_count']


@admin.register(SearchSuggestion)
class SearchSuggestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'category', 'popularity_score', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['text', 'category']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['popularity_score', 'is_active']