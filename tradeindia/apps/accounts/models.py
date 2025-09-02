"""
User and authentication models for TradeIndia
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils import timezone
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from apps.core.models import TimestampedModel, State, District, City
import uuid


class User(AbstractUser):
    """
    Custom user model with additional fields for the marketplace
    """
    USER_TYPE_CHOICES = [
        ('individual', _('Individual')),
        ('business', _('Business')),
        ('dealer', _('Dealer')),
        ('agent', _('Agent')),
    ]
    
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other')),
        ('P', _('Prefer not to say')),
    ]
    
    # Basic Information
    email = models.EmailField(_('Email address'), unique=True, db_index=True)
    phone_number = PhoneNumberField(
        _('Phone number'),
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text=_('Phone number with country code')
    )
    alternate_phone = PhoneNumberField(
        _('Alternate phone'),
        null=True,
        blank=True
    )
    user_type = models.CharField(
        _('User type'),
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='individual'
    )
    
    # Profile Information
    avatar = models.ImageField(
        _('Avatar'),
        upload_to='avatars/',
        blank=True,
        help_text=_('Profile picture')
    )
    bio = models.TextField(_('Bio'), max_length=500, blank=True)
    date_of_birth = models.DateField(_('Date of birth'), null=True, blank=True)
    gender = models.CharField(
        _('Gender'),
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True
    )
    
    # Location Information
    address_line_1 = models.CharField(_('Address line 1'), max_length=255, blank=True)
    address_line_2 = models.CharField(_('Address line 2'), max_length=255, blank=True)
    state = models.ForeignKey(
        State,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name=_('State')
    )
    district = models.ForeignKey(
        District,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name=_('District')
    )
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name=_('City')
    )
    pin_code = models.CharField(
        _('PIN code'),
        max_length=6,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\d{6}$',
                message=_('PIN code must be 6 digits')
            )
        ]
    )
    latitude = models.FloatField(_('Latitude'), null=True, blank=True)
    longitude = models.FloatField(_('Longitude'), null=True, blank=True)
    
    # Business Information (for business users)
    business_name = models.CharField(_('Business name'), max_length=255, blank=True)
    gst_number = models.CharField(
        _('GST number'),
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$',
                message=_('Invalid GST number format')
            )
        ]
    )
    pan_number = models.CharField(
        _('PAN number'),
        max_length=10,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$',
                message=_('Invalid PAN number format')
            )
        ]
    )
    
    # Verification Status
    email_verified = models.BooleanField(_('Email verified'), default=False)
    phone_verified = models.BooleanField(_('Phone verified'), default=False)
    identity_verified = models.BooleanField(_('Identity verified'), default=False)
    business_verified = models.BooleanField(_('Business verified'), default=False)
    
    # Account Status
    is_premium = models.BooleanField(_('Premium user'), default=False)
    premium_expires = models.DateTimeField(_('Premium expires'), null=True, blank=True)
    is_banned = models.BooleanField(_('Banned'), default=False)
    ban_reason = models.TextField(_('Ban reason'), blank=True)
    
    # Preferences
    newsletter_subscribed = models.BooleanField(_('Newsletter subscribed'), default=True)
    sms_notifications = models.BooleanField(_('SMS notifications'), default=True)
    email_notifications = models.BooleanField(_('Email notifications'), default=True)
    push_notifications = models.BooleanField(_('Push notifications'), default=True)
    language_preference = models.CharField(
        _('Language preference'),
        max_length=5,
        choices=settings.LANGUAGES,
        default='en'
    )
    currency_preference = models.CharField(
        _('Currency preference'),
        max_length=3,
        default='INR'
    )
    
    # Statistics
    rating = models.DecimalField(
        _('Rating'),
        max_digits=3,
        decimal_places=2,
        default=0.00,
        db_index=True
    )
    total_reviews = models.PositiveIntegerField(_('Total reviews'), default=0)
    total_listings = models.PositiveIntegerField(_('Total listings'), default=0)
    total_sales = models.PositiveIntegerField(_('Total sales'), default=0)
    total_purchases = models.PositiveIntegerField(_('Total purchases'), default=0)
    
    # Activity Tracking
    last_login_ip = models.GenericIPAddressField(_('Last login IP'), null=True, blank=True)
    last_activity = models.DateTimeField(_('Last activity'), null=True, blank=True)
    login_count = models.PositiveIntegerField(_('Login count'), default=0)
    
    # Social Links
    website = models.URLField(_('Website'), blank=True)
    facebook_url = models.URLField(_('Facebook URL'), blank=True)
    twitter_url = models.URLField(_('Twitter URL'), blank=True)
    instagram_url = models.URLField(_('Instagram URL'), blank=True)
    linkedin_url = models.URLField(_('LinkedIn URL'), blank=True)
    
    # System Fields
    referral_code = models.CharField(
        _('Referral code'),
        max_length=10,
        unique=True,
        null=True,
        blank=True
    )
    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals'
    )
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        indexes = [
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['phone_number', 'is_active']),
            models.Index(fields=['state', 'district', 'city']),
            models.Index(fields=['user_type', 'is_active']),
        ]
    
    def __str__(self):
        return self.get_full_name() or self.username
    
    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self.generate_referral_code()
        super().save(*args, **kwargs)
    
    def generate_referral_code(self):
        """Generate unique referral code"""
        import random
        import string
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not User.objects.filter(referral_code=code).exists():
                return code
    
    @property
    def is_business_user(self):
        return self.user_type in ['business', 'dealer', 'agent']
    
    @property
    def is_verified(self):
        """Check if user is fully verified"""
        if self.is_business_user:
            return all([
                self.email_verified,
                self.phone_verified,
                self.identity_verified,
                self.business_verified
            ])
        return all([
            self.email_verified,
            self.phone_verified,
            self.identity_verified
        ])
    
    @property
    def display_name(self):
        """Get display name for the user"""
        if self.business_name and self.is_business_user:
            return self.business_name
        return self.get_full_name() or self.username
    
    @property
    def location_display(self):
        """Get formatted location display"""
        parts = []
        if self.city:
            parts.append(self.city.name)
        if self.district:
            parts.append(self.district.name)
        if self.state:
            parts.append(self.state.name)
        return ', '.join(parts) if parts else 'India'
    
    def update_last_activity(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])


class UserProfile(TimestampedModel):
    """
    Extended user profile information
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True
    )
    
    # Additional Profile Fields
    cover_image = models.ImageField(
        _('Cover image'),
        upload_to='covers/',
        blank=True
    )
    about_me = models.TextField(_('About me'), blank=True)
    interests = models.TextField(
        _('Interests'),
        blank=True,
        help_text=_('Comma-separated interests')
    )
    skills = models.TextField(
        _('Skills'),
        blank=True,
        help_text=_('Comma-separated skills')
    )
    
    # Professional Information
    occupation = models.CharField(_('Occupation'), max_length=100, blank=True)
    company = models.CharField(_('Company'), max_length=100, blank=True)
    designation = models.CharField(_('Designation'), max_length=100, blank=True)
    years_of_experience = models.PositiveIntegerField(
        _('Years of experience'),
        null=True,
        blank=True
    )
    
    # Preferences
    show_email = models.BooleanField(_('Show email publicly'), default=False)
    show_phone = models.BooleanField(_('Show phone publicly'), default=False)
    show_location = models.BooleanField(_('Show location publicly'), default=True)
    allow_messages = models.BooleanField(_('Allow messages'), default=True)
    
    # Statistics
    profile_views = models.BigIntegerField(_('Profile views'), default=0)
    response_rate = models.DecimalField(
        _('Response rate'),
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    response_time = models.DurationField(
        _('Average response time'),
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
    
    def __str__(self):
        return f'Profile of {self.user.display_name}'


class UserDocument(TimestampedModel):
    """
    User verification documents
    """
    DOCUMENT_TYPE_CHOICES = [
        ('aadhaar', _('Aadhaar Card')),
        ('pan', _('PAN Card')),
        ('passport', _('Passport')),
        ('driving_license', _('Driving License')),
        ('voter_id', _('Voter ID')),
        ('gst_certificate', _('GST Certificate')),
        ('business_registration', _('Business Registration')),
        ('other', _('Other')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(
        _('Document type'),
        max_length=30,
        choices=DOCUMENT_TYPE_CHOICES
    )
    document_number = models.CharField(
        _('Document number'),
        max_length=50,
        blank=True
    )
    document_file = models.FileField(
        _('Document file'),
        upload_to='documents/'
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents'
    )
    verified_at = models.DateTimeField(
        _('Verified at'),
        null=True,
        blank=True
    )
    rejection_reason = models.TextField(
        _('Rejection reason'),
        blank=True
    )
    
    class Meta:
        verbose_name = _('User Document')
        verbose_name_plural = _('User Documents')
        unique_together = ['user', 'document_type']
    
    def __str__(self):
        return f'{self.user.username} - {self.get_document_type_display()}'


class UserFollowing(TimestampedModel):
    """
    User following/follower relationships
    """
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers'
    )
    
    class Meta:
        verbose_name = _('User Following')
        verbose_name_plural = _('User Followings')
        unique_together = ['follower', 'following']
        indexes = [
            models.Index(fields=['follower', 'following']),
        ]
    
    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'


class UserBlock(TimestampedModel):
    """
    User blocking relationships
    """
    blocker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blocked_users'
    )
    blocked = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blocked_by_users'
    )
    reason = models.TextField(_('Reason'), blank=True)
    
    class Meta:
        verbose_name = _('User Block')
        verbose_name_plural = _('User Blocks')
        unique_together = ['blocker', 'blocked']
    
    def __str__(self):
        return f'{self.blocker.username} blocked {self.blocked.username}'


class LoginHistory(models.Model):
    """
    Track user login history
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_history'
    )
    ip_address = models.GenericIPAddressField(_('IP Address'))
    user_agent = models.TextField(_('User Agent'))
    login_time = models.DateTimeField(_('Login time'), auto_now_add=True)
    logout_time = models.DateTimeField(_('Logout time'), null=True, blank=True)
    location = models.CharField(_('Location'), max_length=255, blank=True)
    device_type = models.CharField(_('Device type'), max_length=50, blank=True)
    browser = models.CharField(_('Browser'), max_length=50, blank=True)
    os = models.CharField(_('Operating System'), max_length=50, blank=True)
    is_mobile = models.BooleanField(_('Is mobile'), default=False)
    is_suspicious = models.BooleanField(_('Is suspicious'), default=False)
    
    class Meta:
        verbose_name = _('Login History')
        verbose_name_plural = _('Login Histories')
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['user', '-login_time']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.login_time}'