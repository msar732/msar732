from django.contrib import admin
from .models import Category, Condition, Listing, ListingImage, ListingAttribute, Favorite, Inquiry, Report, SavedSearch


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1
    fields = ['image', 'caption', 'is_main', 'sort_order']


class ListingAttributeInline(admin.TabularInline):
    model = ListingAttribute
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'sort_order', 'created_at']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['sort_order', 'is_active']


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ['name', 'sort_order']
    list_editable = ['sort_order']


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'category', 'price', 'status', 'is_verified', 'state', 'district', 'created_at']
    list_filter = ['status', 'is_verified', 'is_featured', 'listing_type', 'category', 'state', 'created_at']
    search_fields = ['title', 'description', 'seller__username', 'seller__email']
    readonly_fields = ['id', 'views', 'favorites_count', 'inquiries_count', 'ai_verification_score', 'created_at', 'updated_at', 'sold_at']
    autocomplete_fields = ['seller', 'category', 'state', 'district', 'city']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['title', 'description', 'category', 'condition', 'listing_type']
        }),
        ('Pricing', {
            'fields': ['price', 'is_negotiable', 'currency']
        }),
        ('Location', {
            'fields': ['seller', 'state', 'district', 'city', 'address', 'pincode', 'latitude', 'longitude']
        }),
        ('Status & Verification', {
            'fields': ['status', 'is_featured', 'is_urgent', 'is_verified', 'ai_verification_score', 'verification_notes']
        }),
        ('Engagement', {
            'fields': ['views', 'favorites_count', 'inquiries_count', 'tags']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at', 'expires_at', 'sold_at']
        }),
    ]
    
    inlines = [ListingImageInline, ListingAttributeInline]
    actions = ['mark_as_verified', 'mark_as_suspended']
    
    def mark_as_verified(self, request, queryset):
        queryset.update(is_verified=True, status='active')
    mark_as_verified.short_description = "Mark selected listings as verified"
    
    def mark_as_suspended(self, request, queryset):
        queryset.update(status='suspended')
    mark_as_suspended.short_description = "Suspend selected listings"


@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ['listing', 'caption', 'is_main', 'sort_order', 'created_at']
    list_filter = ['is_main', 'created_at']
    search_fields = ['listing__title', 'caption']
    readonly_fields = ['created_at']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'listing', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'listing__title']
    readonly_fields = ['created_at']


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['listing', 'inquirer', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['listing__title', 'inquirer__username', 'message']
    readonly_fields = ['created_at']
    actions = ['mark_as_read']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected inquiries as read"


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['listing', 'reporter', 'reason', 'is_resolved', 'created_at']
    list_filter = ['reason', 'is_resolved', 'created_at']
    search_fields = ['listing__title', 'reporter__username', 'description']
    readonly_fields = ['created_at', 'resolved_at']
    actions = ['mark_as_resolved']
    
    def mark_as_resolved(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_resolved=True, resolved_at=timezone.now())
    mark_as_resolved.short_description = "Mark selected reports as resolved"


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'query', 'category', 'state', 'email_alerts', 'created_at']
    list_filter = ['email_alerts', 'category', 'state', 'created_at']
    search_fields = ['user__username', 'name', 'query']
    readonly_fields = ['created_at']