from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserRating, UserFollowing


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_verified', 'rating', 'total_listings', 'last_active']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'is_verified', 'state', 'date_joined']
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone_number']
    readonly_fields = ['date_joined', 'last_login', 'last_active', 'rating', 'total_ratings', 'total_listings', 'successful_trades']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('phone_number', 'profile_picture', 'bio', 'date_of_birth')
        }),
        ('Location', {
            'fields': ('state', 'district', 'city', 'address', 'pincode')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_document', 'rating', 'total_ratings')
        }),
        ('Activity', {
            'fields': ('last_active', 'total_listings', 'successful_trades')
        }),
        ('Preferences', {
            'fields': ('preferred_categories', 'email_notifications', 'sms_notifications')
        }),
    )
    
    filter_horizontal = ['preferred_categories']


@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    list_display = ['rated_user', 'rater', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['rated_user__username', 'rater__username', 'review']
    readonly_fields = ['created_at']


@admin.register(UserFollowing)
class UserFollowingAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    list_filter = ['created_at']
    search_fields = ['follower__username', 'following__username']
    readonly_fields = ['created_at']