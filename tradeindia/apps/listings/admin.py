"""
Admin configuration for listings app
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models import Count, Sum, Avg
from import_export.admin import ImportExportModelAdmin
from .models import (
    Listing, ListingImage, ListingVideo, ListingAttribute,
    ListingAttributeValue, ListingFavorite, ListingView,
    ListingReport, ListingPromotion
)


class ListingImageInline(admin.TabularInline):
    """Inline for listing images"""
    model = ListingImage
    extra = 0
    fields = ['image', 'caption', 'is_primary', 'order', 'is_inappropriate']
    readonly_fields = ['is_inappropriate']


class ListingAttributeValueInline(admin.TabularInline):
    """Inline for listing attribute values"""
    model = ListingAttributeValue
    extra = 0
    fields = ['attribute', 'value_text', 'value_number', 'value_boolean']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('attribute')


@admin.register(Listing)
class ListingAdmin(ImportExportModelAdmin):
    """Admin for listings"""
    list_display = [
        'title', 'user_link', 'category', 'price_display', 'location_display',
        'status_badge', 'featured_badge', 'views', 'created_at'
    ]
    list_filter = [
        'status', 'listing_type', 'is_featured', 'is_premium',
        'ai_verified', 'category', 'state', 'created_at'
    ]
    search_fields = [
        'title', 'description', 'user__username', 'user__email',
        'user__phone_number', 'id'
    ]
    readonly_fields = [
        'id', 'slug', 'views', 'unique_views', 'favorites', 'shares',
        'inquiries', 'ai_verified', 'ai_confidence_score', 'ai_verification_date',
        'created_at', 'modified_at', 'published_at', 'approved_at', 'sold_at'
    ]
    date_hierarchy = 'created_at'
    inlines = [ListingImageInline, ListingAttributeValueInline]
    actions = ['approve_listings', 'reject_listings', 'feature_listings']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('id', 'title', 'slug', 'description', 'short_description')
        }),
        (_('Classification'), {
            'fields': ('user', 'category', 'subcategory', 'listing_type', 'condition', 'tags')
        }),
        (_('Pricing'), {
            'fields': ('price', 'original_price', 'currency', 'is_negotiable')
        }),
        (_('Location'), {
            'fields': ('state', 'district', 'city', 'locality', 'pin_code', 'latitude', 'longitude')
        }),
        (_('Status & Features'), {
            'fields': ('status', 'is_featured', 'is_premium', 'is_urgent', 'featured_until')
        }),
        (_('Contact Options'), {
            'fields': ('show_phone', 'show_email', 'allow_messages', 'whatsapp_enabled',
                      'contact_name', 'contact_phone', 'contact_email')
        }),
        (_('AI Verification'), {
            'fields': ('ai_verified', 'ai_confidence_score', 'ai_verification_date'),
            'classes': ('collapse',)
        }),
        (_('Statistics'), {
            'fields': ('views', 'unique_views', 'favorites', 'shares', 'inquiries'),
            'classes': ('collapse',)
        }),
        (_('Admin'), {
            'fields': ('admin_notes', 'rejection_reason', 'approved_by', 'approved_at'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'modified_at', 'published_at', 'expires_at', 'sold_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = _('User')
    
    def price_display(self, obj):
        return format_html('₹{:,.0f}', obj.price)
    price_display.short_description = _('Price')
    price_display.admin_order_field = 'price'
    
    def location_display(self, obj):
        return f"{obj.city.name if obj.city else obj.district.name}, {obj.state.name}"
    location_display.short_description = _('Location')
    
    def status_badge(self, obj):
        colors = {
            'draft': 'gray',
            'pending': 'orange',
            'active': 'green',
            'sold': 'blue',
            'expired': 'red',
            'rejected': 'red',
            'archived': 'gray',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = _('Status')
    
    def featured_badge(self, obj):
        if obj.is_featured:
            return format_html('<span style="color: gold;">★ Featured</span>')
        return '-'
    featured_badge.short_description = _('Featured')
    
    def approve_listings(self, request, queryset):
        count = queryset.filter(status='pending').update(
            status='active',
            approved_by=request.user,
            approved_at=timezone.now(),
            published_at=timezone.now()
        )
        self.message_user(request, f'{count} listings approved.')
    approve_listings.short_description = _('Approve selected listings')
    
    def reject_listings(self, request, queryset):
        count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{count} listings rejected.')
    reject_listings.short_description = _('Reject selected listings')
    
    def feature_listings(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f'{count} listings featured.')
    feature_listings.short_description = _('Feature selected listings')


@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    """Admin for listing images"""
    list_display = ['listing', 'image_preview', 'caption', 'is_primary', 'order', 
                    'contains_text', 'is_inappropriate', 'created_at']
    list_filter = ['is_primary', 'contains_text', 'is_inappropriate', 'created_at']
    search_fields = ['listing__title', 'caption', 'ai_description']
    list_editable = ['is_primary', 'order']
    readonly_fields = ['image_preview', 'ai_tags', 'ai_description', 
                      'contains_text', 'is_inappropriate']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.thumbnail.url
            )
        return '-'
    image_preview.short_description = _('Preview')


@admin.register(ListingAttribute)
class ListingAttributeAdmin(admin.ModelAdmin):
    """Admin for listing attributes"""
    list_display = ['name', 'category', 'field_type', 'is_required', 
                    'is_searchable', 'show_in_list', 'order']
    list_filter = ['category', 'field_type', 'is_required', 'is_searchable']
    search_fields = ['name', 'category__name']
    list_editable = ['is_required', 'is_searchable', 'show_in_list', 'order']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ListingReport)
class ListingReportAdmin(admin.ModelAdmin):
    """Admin for listing reports"""
    list_display = ['listing', 'reporter', 'reason', 'status', 'created_at']
    list_filter = ['reason', 'status', 'created_at']
    search_fields = ['listing__title', 'reporter__username', 'description']
    readonly_fields = ['listing', 'reporter', 'reason', 'description', 'created_at']
    actions = ['mark_reviewed', 'take_action', 'dismiss_reports']
    
    fieldsets = (
        (_('Report Details'), {
            'fields': ('listing', 'reporter', 'reason', 'description', 'created_at')
        }),
        (_('Review'), {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'admin_notes')
        }),
    )
    
    def mark_reviewed(self, request, queryset):
        count = queryset.filter(status='pending').update(
            status='reviewed',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{count} reports marked as reviewed.')
    mark_reviewed.short_description = _('Mark as reviewed')
    
    def take_action(self, request, queryset):
        for report in queryset.filter(status__in=['pending', 'reviewed']):
            report.status = 'action_taken'
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.save()
            
            # Deactivate the listing
            report.listing.status = 'archived'
            report.listing.save()
        
        self.message_user(request, f'Action taken on {queryset.count()} reports.')
    take_action.short_description = _('Take action on reports')
    
    def dismiss_reports(self, request, queryset):
        count = queryset.update(
            status='dismissed',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{count} reports dismissed.')
    dismiss_reports.short_description = _('Dismiss reports')


@admin.register(ListingPromotion)
class ListingPromotionAdmin(admin.ModelAdmin):
    """Admin for listing promotions"""
    list_display = ['listing', 'promotion_type', 'date_range', 'amount_paid', 
                    'is_active', 'impressions', 'clicks', 'ctr']
    list_filter = ['promotion_type', 'is_active', 'start_date', 'end_date']
    search_fields = ['listing__title', 'payment_reference']
    date_hierarchy = 'start_date'
    readonly_fields = ['impressions', 'clicks', 'ctr']
    
    def date_range(self, obj):
        return f"{obj.start_date.date()} to {obj.end_date.date()}"
    date_range.short_description = _('Date Range')
    
    def ctr(self, obj):
        if obj.impressions > 0:
            return f"{(obj.clicks / obj.impressions * 100):.2f}%"
        return "0%"
    ctr.short_description = _('CTR')


# Register remaining models
admin.site.register(ListingVideo)
admin.site.register(ListingFavorite)

# Customize admin site
admin.site.site_header = 'TradeIndia Administration'
admin.site.site_title = 'TradeIndia Admin'
admin.site.index_title = 'Welcome to TradeIndia Administration'