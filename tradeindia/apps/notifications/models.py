"""
Notification models for TradeIndia
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.models import TimestampedModel


class NotificationTemplate(TimestampedModel):
    """
    Templates for different types of notifications
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('listing_approved', _('Listing Approved')),
        ('listing_rejected', _('Listing Rejected')),
        ('listing_expired', _('Listing Expired')),
        ('listing_sold', _('Listing Sold')),
        ('new_message', _('New Message')),
        ('new_offer', _('New Offer')),
        ('offer_accepted', _('Offer Accepted')),
        ('offer_rejected', _('Offer Rejected')),
        ('new_review', _('New Review')),
        ('new_follower', _('New Follower')),
        ('saved_search_alert', _('Saved Search Alert')),
        ('price_drop', _('Price Drop')),
        ('payment_received', _('Payment Received')),
        ('payment_sent', _('Payment Sent')),
        ('verification_complete', _('Verification Complete')),
        ('account_warning', _('Account Warning')),
        ('promotion_ending', _('Promotion Ending')),
        ('system_announcement', _('System Announcement')),
    ]
    
    name = models.CharField(_('Template name'), max_length=100, unique=True)
    notification_type = models.CharField(
        _('Notification type'),
        max_length=30,
        choices=NOTIFICATION_TYPE_CHOICES,
        unique=True
    )
    
    # Templates for different channels
    email_subject = models.CharField(_('Email subject'), max_length=200, blank=True)
    email_body = models.TextField(_('Email body'), blank=True, help_text=_('HTML allowed'))
    sms_template = models.TextField(_('SMS template'), max_length=160, blank=True)
    push_title = models.CharField(_('Push notification title'), max_length=100, blank=True)
    push_body = models.CharField(_('Push notification body'), max_length=255, blank=True)
    in_app_message = models.TextField(_('In-app message'), blank=True)
    
    # Channel settings
    send_email = models.BooleanField(_('Send email'), default=True)
    send_sms = models.BooleanField(_('Send SMS'), default=False)
    send_push = models.BooleanField(_('Send push notification'), default=True)
    send_in_app = models.BooleanField(_('Send in-app notification'), default=True)
    
    # Additional settings
    is_active = models.BooleanField(_('Active'), default=True)
    priority = models.IntegerField(
        _('Priority'),
        choices=[(1, _('Low')), (2, _('Medium')), (3, _('High'))],
        default=2
    )
    
    class Meta:
        verbose_name = _('Notification Template')
        verbose_name_plural = _('Notification Templates')
        ordering = ['notification_type']
    
    def __str__(self):
        return self.name


class UserNotification(TimestampedModel):
    """
    Individual notifications sent to users
    """
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications'
    )
    
    notification_type = models.CharField(
        _('Notification type'),
        max_length=30,
        choices=NotificationTemplate.NOTIFICATION_TYPE_CHOICES
    )
    
    # Content
    title = models.CharField(_('Title'), max_length=200)
    message = models.TextField(_('Message'))
    data = models.JSONField(_('Additional data'), default=dict, blank=True)
    
    # Related objects
    related_listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    related_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='related_notifications'
    )
    
    # Status
    is_read = models.BooleanField(_('Read'), default=False, db_index=True)
    read_at = models.DateTimeField(_('Read at'), null=True, blank=True)
    is_archived = models.BooleanField(_('Archived'), default=False)
    
    # Delivery status
    email_sent = models.BooleanField(_('Email sent'), default=False)
    email_sent_at = models.DateTimeField(_('Email sent at'), null=True, blank=True)
    sms_sent = models.BooleanField(_('SMS sent'), default=False)
    sms_sent_at = models.DateTimeField(_('SMS sent at'), null=True, blank=True)
    push_sent = models.BooleanField(_('Push sent'), default=False)
    push_sent_at = models.DateTimeField(_('Push sent at'), null=True, blank=True)
    
    # Action URL
    action_url = models.CharField(_('Action URL'), max_length=500, blank=True)
    action_text = models.CharField(_('Action text'), max_length=50, blank=True)
    
    class Meta:
        verbose_name = _('User Notification')
        verbose_name_plural = _('User Notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
            models.Index(fields=['recipient', 'notification_type', '-created_at']),
        ]
    
    def __str__(self):
        return f'{self.recipient.username} - {self.title}'
    
    def mark_as_read(self):
        """Mark notification as read"""
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class NotificationPreference(models.Model):
    """
    User notification preferences
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Global settings
    all_email = models.BooleanField(_('All email notifications'), default=True)
    all_sms = models.BooleanField(_('All SMS notifications'), default=False)
    all_push = models.BooleanField(_('All push notifications'), default=True)
    all_in_app = models.BooleanField(_('All in-app notifications'), default=True)
    
    # Specific notification types
    preferences = models.JSONField(
        _('Notification preferences'),
        default=dict,
        help_text=_('Specific preferences for each notification type')
    )
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField(_('Quiet hours enabled'), default=False)
    quiet_hours_start = models.TimeField(_('Quiet hours start'), null=True, blank=True)
    quiet_hours_end = models.TimeField(_('Quiet hours end'), null=True, blank=True)
    
    # Frequency settings
    daily_digest = models.BooleanField(_('Daily digest'), default=False)
    weekly_digest = models.BooleanField(_('Weekly digest'), default=True)
    
    class Meta:
        verbose_name = _('Notification Preference')
        verbose_name_plural = _('Notification Preferences')
    
    def __str__(self):
        return f'Preferences for {self.user.username}'
    
    def can_send_notification(self, notification_type, channel):
        """Check if notification can be sent based on preferences"""
        # Check global settings
        if channel == 'email' and not self.all_email:
            return False
        elif channel == 'sms' and not self.all_sms:
            return False
        elif channel == 'push' and not self.all_push:
            return False
        elif channel == 'in_app' and not self.all_in_app:
            return False
        
        # Check specific preferences
        if notification_type in self.preferences:
            return self.preferences[notification_type].get(channel, True)
        
        return True


class NotificationLog(TimestampedModel):
    """
    Log of all notification attempts
    """
    notification = models.ForeignKey(
        UserNotification,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    channel = models.CharField(
        _('Channel'),
        max_length=20,
        choices=[
            ('email', _('Email')),
            ('sms', _('SMS')),
            ('push', _('Push')),
            ('in_app', _('In-App')),
        ]
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=[
            ('pending', _('Pending')),
            ('sent', _('Sent')),
            ('delivered', _('Delivered')),
            ('failed', _('Failed')),
            ('bounced', _('Bounced')),
        ],
        default='pending'
    )
    
    # Delivery details
    sent_at = models.DateTimeField(_('Sent at'), null=True, blank=True)
    delivered_at = models.DateTimeField(_('Delivered at'), null=True, blank=True)
    failed_at = models.DateTimeField(_('Failed at'), null=True, blank=True)
    
    # Error details
    error_message = models.TextField(_('Error message'), blank=True)
    retry_count = models.IntegerField(_('Retry count'), default=0)
    
    # Provider details
    provider = models.CharField(_('Provider'), max_length=50, blank=True)
    provider_message_id = models.CharField(_('Provider message ID'), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('Notification Log')
        verbose_name_plural = _('Notification Logs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['notification', 'channel', 'status']),
        ]
    
    def __str__(self):
        return f'{self.notification} - {self.channel} - {self.status}'


class PushDevice(TimestampedModel):
    """
    User devices for push notifications
    """
    DEVICE_TYPE_CHOICES = [
        ('ios', _('iOS')),
        ('android', _('Android')),
        ('web', _('Web')),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='push_devices'
    )
    device_type = models.CharField(
        _('Device type'),
        max_length=20,
        choices=DEVICE_TYPE_CHOICES
    )
    device_token = models.CharField(_('Device token'), max_length=255, unique=True)
    device_name = models.CharField(_('Device name'), max_length=100, blank=True)
    
    # Status
    is_active = models.BooleanField(_('Active'), default=True)
    last_used = models.DateTimeField(_('Last used'), null=True, blank=True)
    
    # Additional info
    app_version = models.CharField(_('App version'), max_length=20, blank=True)
    os_version = models.CharField(_('OS version'), max_length=20, blank=True)
    
    class Meta:
        verbose_name = _('Push Device')
        verbose_name_plural = _('Push Devices')
        ordering = ['-last_used']
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.device_type} - {self.device_name}'