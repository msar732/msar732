"""
URL configuration for accounts app
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Profile views
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/<str:username>/', views.PublicProfileView.as_view(), name='public_profile'),
    
    # Settings
    path('settings/', views.AccountSettingsView.as_view(), name='settings'),
    path('settings/password/', views.PasswordChangeView.as_view(), name='password_change'),
    path('settings/notifications/', views.NotificationSettingsView.as_view(), name='notification_settings'),
    path('settings/privacy/', views.PrivacySettingsView.as_view(), name='privacy_settings'),
    
    # Verification
    path('verify/phone/', views.PhoneVerificationView.as_view(), name='phone_verification'),
    path('verify/identity/', views.IdentityVerificationView.as_view(), name='identity_verification'),
    path('verify/business/', views.BusinessVerificationView.as_view(), name='business_verification'),
    
    # Following
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('followers/', views.FollowersListView.as_view(), name='followers'),
    path('following/', views.FollowingListView.as_view(), name='following'),
    
    # Blocking
    path('block/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock/<int:user_id>/', views.unblock_user, name='unblock_user'),
    path('blocked/', views.BlockedUsersView.as_view(), name='blocked_users'),
]