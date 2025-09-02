from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'phone_number', 'state', 'is_verified', 'trust_score', 'date_joined']
    list_filter = ['is_verified', 'state', 'date_joined']
    search_fields = ['username', 'email', 'phone_number']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'profile_image', 'state', 'district', 'address', 'trust_score', 'is_verified')
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth']
    search_fields = ['user__username', 'user__email']