"""
Admin configuration for core app
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from mptt.admin import MPTTModelAdmin
from import_export.admin import ImportExportModelAdmin
from .models import (
    Category, State, District, City, Tag, Currency,
    Advertisement, FAQ, Page, SiteConfiguration
)


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin, ImportExportModelAdmin):
    """Admin for categories with MPTT support"""
    list_display = ['name', 'parent', 'slug', 'is_active', 'featured', 'order', 'listing_count']
    list_filter = ['is_active', 'featured', 'level', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'featured', 'order']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'parent', 'description')
        }),
        (_('Display Options'), {
            'fields': ('icon', 'image', 'is_active', 'featured', 'order')
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    def listing_count(self, obj):
        return obj.listings.filter(status='active').count()
    listing_count.short_description = _('Active Listings')


@admin.register(State)
class StateAdmin(ImportExportModelAdmin):
    """Admin for Indian states"""
    list_display = ['code', 'name', 'capital', 'population', 'area', 'is_active', 'district_count']
    list_filter = ['is_active']
    search_fields = ['name', 'code', 'capital']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    
    def district_count(self, obj):
        return obj.districts.count()
    district_count.short_description = _('Districts')


@admin.register(District)
class DistrictAdmin(ImportExportModelAdmin):
    """Admin for districts"""
    list_display = ['name', 'state', 'headquarters', 'population', 'is_active', 'city_count']
    list_filter = ['state', 'is_active']
    search_fields = ['name', 'headquarters', 'state__name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    autocomplete_fields = ['state']
    
    def city_count(self, obj):
        return obj.cities.count()
    city_count.short_description = _('Cities')


@admin.register(City)
class CityAdmin(ImportExportModelAdmin):
    """Admin for cities"""
    list_display = ['name', 'district', 'population', 'pin_code', 'is_active']
    list_filter = ['district__state', 'district', 'is_active']
    search_fields = ['name', 'pin_code', 'district__name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    autocomplete_fields = ['district']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin for tags"""
    list_display = ['name', 'slug', 'is_active', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active', 'created_at']
    list_editable = ['is_active']


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    """Admin for currencies"""
    list_display = ['code', 'name', 'symbol', 'exchange_rate', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    list_editable = ['exchange_rate', 'is_active']


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    """Admin for advertisements"""
    list_display = ['title', 'advertiser', 'position', 'display_status', 'impressions', 
                    'clicks', 'ctr', 'priority', 'is_active']
    list_filter = ['position', 'is_active', 'start_date', 'end_date']
    search_fields = ['title', 'advertiser__username', 'advertiser__email']
    filter_horizontal = ['categories', 'states']
    date_hierarchy = 'created_at'
    readonly_fields = ['impressions', 'clicks', 'ctr']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'advertiser', 'position', 'priority')
        }),
        (_('Content'), {
            'fields': ('image', 'link', 'alt_text')
        }),
        (_('Schedule'), {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
        (_('Targeting'), {
            'fields': ('categories', 'states'),
            'classes': ('collapse',)
        }),
        (_('Statistics'), {
            'fields': ('impressions', 'clicks', 'ctr'),
            'classes': ('collapse',)
        }),
    )
    
    def display_status(self, obj):
        from django.utils import timezone
        now = timezone.now()
        if not obj.is_active:
            return format_html('<span style="color: red;">Inactive</span>')
        elif obj.start_date > now:
            return format_html('<span style="color: orange;">Scheduled</span>')
        elif obj.end_date < now:
            return format_html('<span style="color: gray;">Expired</span>')
        else:
            return format_html('<span style="color: green;">Active</span>')
    display_status.short_description = _('Status')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """Admin for FAQs"""
    list_display = ['question', 'category', 'order', 'views', 'helpful_votes', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['question', 'answer']
    list_editable = ['order', 'is_active']
    
    fieldsets = (
        (None, {
            'fields': ('question', 'answer', 'category')
        }),
        (_('Display'), {
            'fields': ('order', 'is_active')
        }),
        (_('Statistics'), {
            'fields': ('views', 'helpful_votes'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """Admin for static pages"""
    list_display = ['title', 'slug', 'display_locations', 'order', 'is_active']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['order', 'is_active']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content')
        }),
        (_('Display Options'), {
            'fields': ('is_active', 'show_in_header', 'show_in_footer', 'order')
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    def display_locations(self, obj):
        locations = []
        if obj.show_in_header:
            locations.append('Header')
        if obj.show_in_footer:
            locations.append('Footer')
        return ', '.join(locations) if locations else '-'
    display_locations.short_description = _('Display Locations')


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    """Admin for site configuration"""
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('site_name', 'tagline', 'logo', 'favicon')
        }),
        (_('Contact Information'), {
            'fields': ('contact_email', 'contact_phone', 'contact_address', 'whatsapp_number')
        }),
        (_('Social Media'), {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'youtube_url', 'linkedin_url')
        }),
        (_('Analytics & Tracking'), {
            'fields': ('google_analytics_id', 'facebook_pixel_id'),
            'classes': ('collapse',)
        }),
        (_('Business Settings'), {
            'fields': ('listing_approval_required', 'max_images_per_listing', 
                      'max_free_listings_per_user', 'featured_listing_price', 
                      'commission_percentage', 'minimum_listing_price', 'maximum_listing_price')
        }),
        (_('Maintenance'), {
            'fields': ('maintenance_mode', 'maintenance_message'),
            'classes': ('collapse',)
        }),
        (_('Legal'), {
            'fields': ('terms_of_service', 'privacy_policy'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteConfiguration.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False