"""
URL configuration for notifications app
"""
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notification views
    path('', views.NotificationListView.as_view(), name='list'),
    path('unread/', views.UnreadNotificationsView.as_view(), name='unread'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='detail'),
    
    # Actions
    path('mark-read/', views.mark_as_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_read'),
    path('<int:pk>/archive/', views.archive_notification, name='archive'),
    path('clear-all/', views.clear_all_notifications, name='clear_all'),
    
    # Settings
    path('settings/', views.NotificationSettingsView.as_view(), name='settings'),
    path('settings/update/', views.update_notification_settings, name='update_settings'),
    
    # Push notifications
    path('push/subscribe/', views.subscribe_push_notifications, name='push_subscribe'),
    path('push/unsubscribe/', views.unsubscribe_push_notifications, name='push_unsubscribe'),
]