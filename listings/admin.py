from django.contrib import admin
from django.utils.html import format_html
from .models import Listing, Category, State, District, ListingImage, Favorite

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'price', 'status', 'is_verified', 'ai_score_display', 'created_at']
    list_filter = ['status', 'is_verified', 'category', 'state', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['view_count', 'ai_genuineness_score', 'created_at', 'updated_at']
    actions = ['mark_as_verified', 'mark_as_featured']
    
    def ai_score_display(self, obj):
        if obj.ai_genuineness_score > 0.8:
            color = 'green'
        elif obj.ai_genuineness_score > 0.6:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {};">{:.2f}</span>',
            color,
            obj.ai_genuineness_score
        )
    ai_score_display.short_description = 'AI Score'
    
    def mark_as_verified(self, request, queryset):
        queryset.update(is_verified=True)
    mark_as_verified.short_description = "Mark selected listings as verified"
    
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
    mark_as_featured.short_description = "Mark selected listings as featured"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'state']
    list_filter = ['state']
    search_fields = ['name', 'state__name']

@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ['listing', 'order', 'is_primary']
    list_filter = ['is_primary']
    search_fields = ['listing__title']

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'listing', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'listing__title']