# Accounts Admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'state', 'district', 'is_verified', 'trust_score', 'created_at']
    list_filter = ['is_verified', 'state', 'created_at']
    search_fields = ['username', 'email', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio', 'website']
    search_fields = ['user__username', 'bio']