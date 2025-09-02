"""
Signal handlers for accounts app
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile, UserTrustScore
from apps.notifications.models import NotificationPreference

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when user is created"""
    if created:
        UserProfile.objects.create(user=instance)
        NotificationPreference.objects.create(user=instance)
        
        # Send welcome notification
        from apps.notifications.utils import send_notification
        send_notification(
            recipient=instance,
            notification_type='system_announcement',
            title='Welcome to TradeIndia!',
            message='Your account has been created successfully. Start buying and selling today!'
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()