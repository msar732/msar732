from django.contrib import admin
from .models import SearchQuery, SavedSearch

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['query', 'user', 'results_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['query', 'user__username']
    readonly_fields = ['created_at']

@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'email_alerts', 'created_at']
    list_filter = ['email_alerts', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at']