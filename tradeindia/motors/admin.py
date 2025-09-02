from django.contrib import admin
from .models import MotorCategory, MotorMake, MotorModel, MotorListing, MotorImage, MotorInquiry

@admin.register(MotorCategory)
class MotorCategoryAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['display_name', 'name']

@admin.register(MotorMake)
class MotorMakeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name']

@admin.register(MotorModel)
class MotorModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'make']
    list_filter = ['make__category', 'make']
    search_fields = ['name', 'make__name']

@admin.register(MotorListing)
class MotorListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'make', 'model', 'year', 'price', 'status', 'is_featured', 'created_at']
    list_filter = ['status', 'is_featured', 'is_verified', 'category', 'make', 'fuel_type']
    search_fields = ['title', 'make__name', 'model__name']
    readonly_fields = ['ai_score', 'view_count', 'inquiry_count']

@admin.register(MotorImage)
class MotorImageAdmin(admin.ModelAdmin):
    list_display = ['listing', 'order', 'is_primary']
    list_filter = ['is_primary']

@admin.register(MotorInquiry)
class MotorInquiryAdmin(admin.ModelAdmin):
    list_display = ['listing', 'inquirer', 'created_at', 'is_responded']
    list_filter = ['is_responded', 'created_at']