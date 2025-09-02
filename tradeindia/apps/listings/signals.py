"""
Signal handlers for listings app
"""
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.utils import timezone
from .models import Listing, ListingImage, ListingReport
from apps.ai_verification.tasks import verify_listing_async
from apps.notifications.utils import send_notification


@receiver(pre_save, sender=Listing)
def set_listing_expiry(sender, instance, **kwargs):
    """Set listing expiry date"""
    if instance.status == 'active' and not instance.expires_at:
        # Set expiry to 60 days from now
        instance.expires_at = timezone.now() + timezone.timedelta(days=60)


@receiver(post_save, sender=Listing)
def handle_listing_save(sender, instance, created, **kwargs):
    """Handle actions after listing is saved"""
    if created:
        # Send notification to user
        send_notification(
            recipient=instance.user,
            notification_type='listing_approved' if instance.status == 'active' else 'system_announcement',
            title='Listing Created Successfully',
            message=f'Your listing "{instance.title}" has been created.',
            related_listing=instance
        )
        
        # Trigger AI verification
        if instance.status == 'active':
            verify_listing_async.delay(instance.id)
    
    # Clear caches
    cache.delete(f'listing_{instance.slug}')
    cache.delete_pattern(f'user_listings_{instance.user.id}_*')
    cache.delete_pattern('recent_listings_*')
    
    # Update user statistics
    if created:
        instance.user.total_listings = instance.user.listings.count()
        instance.user.save(update_fields=['total_listings'])


@receiver(post_save, sender=ListingImage)
def process_listing_image(sender, instance, created, **kwargs):
    """Process listing image after upload"""
    if created:
        # Trigger AI image analysis
        from apps.ai_verification.tasks import analyze_image_async
        analyze_image_async.delay(instance.id)


@receiver(post_delete, sender=ListingImage)
def delete_listing_image_files(sender, instance, **kwargs):
    """Delete image files when ListingImage is deleted"""
    # Delete the actual file
    if instance.image:
        instance.image.delete(save=False)


@receiver(post_save, sender=ListingReport)
def handle_listing_report(sender, instance, created, **kwargs):
    """Handle actions after listing is reported"""
    if created:
        # Check if listing has too many reports
        report_count = ListingReport.objects.filter(
            listing=instance.listing,
            status__in=['pending', 'reviewed']
        ).count()
        
        if report_count >= 5:
            # Auto-hide listing for review
            instance.listing.status = 'pending'
            instance.listing.save()
            
            # Notify admin
            from django.contrib.auth import get_user_model
            User = get_user_model()
            admins = User.objects.filter(is_staff=True, is_active=True)
            
            for admin in admins:
                send_notification(
                    recipient=admin,
                    notification_type='system_announcement',
                    title='Listing Auto-Hidden Due to Reports',
                    message=f'Listing "{instance.listing.title}" has been auto-hidden due to multiple reports.',
                    related_listing=instance.listing
                )