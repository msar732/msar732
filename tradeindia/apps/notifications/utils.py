"""
Notification utilities
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from .models import NotificationTemplate, UserNotification, NotificationLog
import logging

logger = logging.getLogger(__name__)


def send_notification(recipient, notification_type, title, message, 
                     sender=None, related_listing=None, related_user=None, 
                     action_url=None, data=None):
    """
    Send notification to user through multiple channels
    """
    # Create in-app notification
    notification = UserNotification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        title=title,
        message=message,
        related_listing=related_listing,
        related_user=related_user,
        action_url=action_url or '',
        data=data or {}
    )
    
    # Get notification template
    try:
        template = NotificationTemplate.objects.get(
            notification_type=notification_type,
            is_active=True
        )
    except NotificationTemplate.DoesNotExist:
        logger.warning(f"No template found for notification type: {notification_type}")
        return notification
    
    # Check user preferences
    preferences = getattr(recipient, 'notification_preferences', None)
    if not preferences:
        from .models import NotificationPreference
        preferences = NotificationPreference.objects.create(user=recipient)
    
    # Send through different channels
    if template.send_email and preferences.can_send_notification(notification_type, 'email'):
        send_email_notification(notification, template)
    
    if template.send_sms and preferences.can_send_notification(notification_type, 'sms'):
        send_sms_notification(notification, template)
    
    if template.send_push and preferences.can_send_notification(notification_type, 'push'):
        send_push_notification(notification, template)
    
    return notification


def send_email_notification(notification, template):
    """Send email notification"""
    try:
        # Prepare context
        context = {
            'user': notification.recipient,
            'notification': notification,
            'site_name': settings.SITE_NAME,
            'action_url': notification.action_url,
        }
        
        # Render email content
        subject = template.email_subject.format(**context)
        html_content = render_to_string('notifications/email_base.html', {
            **context,
            'content': template.email_body.format(**context)
        })
        
        # Send email
        send_mail(
            subject=subject,
            message='',  # Plain text version
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.recipient.email],
            html_message=html_content,
            fail_silently=False
        )
        
        # Update notification
        notification.email_sent = True
        notification.email_sent_at = timezone.now()
        notification.save(update_fields=['email_sent', 'email_sent_at'])
        
        # Log success
        NotificationLog.objects.create(
            notification=notification,
            channel='email',
            status='sent',
            sent_at=timezone.now()
        )
        
    except Exception as e:
        logger.error(f"Error sending email notification: {e}")
        NotificationLog.objects.create(
            notification=notification,
            channel='email',
            status='failed',
            error_message=str(e)
        )


def send_sms_notification(notification, template):
    """Send SMS notification"""
    try:
        # Check if user has phone number
        if not notification.recipient.phone_number:
            return
        
        # Prepare message
        context = {
            'user': notification.recipient.get_short_name() or notification.recipient.username,
            'title': notification.title,
        }
        message = template.sms_template.format(**context)
        
        # Send SMS using provider (e.g., Twilio)
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=str(notification.recipient.phone_number)
        )
        
        # Update notification
        notification.sms_sent = True
        notification.sms_sent_at = timezone.now()
        notification.save(update_fields=['sms_sent', 'sms_sent_at'])
        
        # Log success
        NotificationLog.objects.create(
            notification=notification,
            channel='sms',
            status='sent',
            sent_at=timezone.now(),
            provider_message_id=message.sid
        )
        
    except Exception as e:
        logger.error(f"Error sending SMS notification: {e}")
        NotificationLog.objects.create(
            notification=notification,
            channel='sms',
            status='failed',
            error_message=str(e)
        )


def send_push_notification(notification, template):
    """Send push notification"""
    try:
        # Get user's devices
        devices = notification.recipient.push_devices.filter(is_active=True)
        
        if not devices.exists():
            return
        
        # Prepare notification data
        data = {
            'title': template.push_title or notification.title,
            'body': template.push_body or notification.message,
            'notification_id': str(notification.id),
            'action_url': notification.action_url,
        }
        
        # Send to each device
        for device in devices:
            if device.device_type == 'web':
                # Send web push notification
                send_web_push(device, data)
            elif device.device_type in ['ios', 'android']:
                # Send mobile push notification
                send_mobile_push(device, data)
        
        # Update notification
        notification.push_sent = True
        notification.push_sent_at = timezone.now()
        notification.save(update_fields=['push_sent', 'push_sent_at'])
        
        # Log success
        NotificationLog.objects.create(
            notification=notification,
            channel='push',
            status='sent',
            sent_at=timezone.now()
        )
        
    except Exception as e:
        logger.error(f"Error sending push notification: {e}")
        NotificationLog.objects.create(
            notification=notification,
            channel='push',
            status='failed',
            error_message=str(e)
        )


def send_web_push(device, data):
    """Send web push notification"""
    # Implementation depends on web push service
    pass


def send_mobile_push(device, data):
    """Send mobile push notification"""
    # Implementation depends on FCM/APNS
    pass


def mark_notifications_as_read(user, notification_ids=None):
    """Mark notifications as read"""
    queryset = UserNotification.objects.filter(
        recipient=user,
        is_read=False
    )
    
    if notification_ids:
        queryset = queryset.filter(id__in=notification_ids)
    
    count = queryset.update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return count


def get_unread_count(user):
    """Get unread notification count for user"""
    return UserNotification.objects.filter(
        recipient=user,
        is_read=False,
        is_archived=False
    ).count()


def send_bulk_notification(users, notification_type, title, message, **kwargs):
    """Send notification to multiple users"""
    notifications = []
    
    for user in users:
        notification = send_notification(
            recipient=user,
            notification_type=notification_type,
            title=title,
            message=message,
            **kwargs
        )
        notifications.append(notification)
    
    return notifications