"""
Listing models for TradeIndia marketplace
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from taggit.managers import TaggableManager
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill, ResizeToFit
from apps.core.models import TimestampedModel, UUIDModel, Category, State, District, City, Currency
import uuid
import os


def listing_image_upload_path(instance, filename):
    """Generate upload path for listing images"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('listings', str(instance.listing.id), filename)


class Listing(UUIDModel, TimestampedModel):
    """
    Main listing model for items/services
    """
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('pending', _('Pending Approval')),
        ('active', _('Active')),
        ('sold', _('Sold')),
        ('expired', _('Expired')),
        ('rejected', _('Rejected')),
        ('archived', _('Archived')),
    ]
    
    CONDITION_CHOICES = [
        ('new', _('Brand New')),
        ('like_new', _('Like New')),
        ('excellent', _('Excellent')),
        ('good', _('Good')),
        ('fair', _('Fair')),
        ('poor', _('Poor')),
        ('parts', _('For Parts/Not Working')),
    ]
    
    LISTING_TYPE_CHOICES = [
        ('sale', _('For Sale')),
        ('rent', _('For Rent')),
        ('wanted', _('Wanted')),
        ('service', _('Service')),
        ('job', _('Job')),
        ('event', _('Event')),
    ]
    
    # Basic Information
    title = models.CharField(_('Title'), max_length=200, db_index=True)
    slug = models.SlugField(_('Slug'), max_length=220, unique=True)
    description = models.TextField(_('Description'))
    short_description = models.CharField(_('Short description'), max_length=500, blank=True)
    
    # User and Category
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listings',
        verbose_name=_('User')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='listings',
        verbose_name=_('Category')
    )
    subcategory = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategory_listings',
        verbose_name=_('Subcategory')
    )
    
    # Listing Type and Status
    listing_type = models.CharField(
        _('Listing type'),
        max_length=20,
        choices=LISTING_TYPE_CHOICES,
        default='sale',
        db_index=True
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True
    )
    condition = models.CharField(
        _('Condition'),
        max_length=20,
        choices=CONDITION_CHOICES,
        blank=True
    )
    
    # Pricing
    price = models.DecimalField(
        _('Price'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        db_index=True
    )
    original_price = models.DecimalField(
        _('Original price'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.SET_NULL,
        null=True,
        default='INR',
        verbose_name=_('Currency')
    )
    is_negotiable = models.BooleanField(_('Price negotiable'), default=True)
    
    # Location
    state = models.ForeignKey(
        State,
        on_delete=models.PROTECT,
        related_name='listings',
        verbose_name=_('State')
    )
    district = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        related_name='listings',
        verbose_name=_('District')
    )
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='listings',
        verbose_name=_('City')
    )
    locality = models.CharField(_('Locality'), max_length=100, blank=True)
    pin_code = models.CharField(_('PIN code'), max_length=6, blank=True)
    latitude = models.FloatField(_('Latitude'), null=True, blank=True)
    longitude = models.FloatField(_('Longitude'), null=True, blank=True)
    
    # Features
    is_featured = models.BooleanField(_('Featured'), default=False, db_index=True)
    is_premium = models.BooleanField(_('Premium'), default=False, db_index=True)
    is_urgent = models.BooleanField(_('Urgent'), default=False)
    featured_until = models.DateTimeField(_('Featured until'), null=True, blank=True)
    
    # Contact Options
    show_phone = models.BooleanField(_('Show phone number'), default=True)
    show_email = models.BooleanField(_('Show email'), default=True)
    allow_messages = models.BooleanField(_('Allow messages'), default=True)
    whatsapp_enabled = models.BooleanField(_('WhatsApp enabled'), default=True)
    contact_name = models.CharField(_('Contact name'), max_length=100, blank=True)
    contact_phone = models.CharField(_('Contact phone'), max_length=20, blank=True)
    contact_email = models.EmailField(_('Contact email'), blank=True)
    
    # Statistics
    views = models.BigIntegerField(_('Views'), default=0, db_index=True)
    unique_views = models.BigIntegerField(_('Unique views'), default=0)
    favorites = models.BigIntegerField(_('Favorites'), default=0)
    shares = models.BigIntegerField(_('Shares'), default=0)
    inquiries = models.BigIntegerField(_('Inquiries'), default=0)
    
    # SEO
    meta_title = models.CharField(_('Meta title'), max_length=155, blank=True)
    meta_description = models.TextField(_('Meta description'), max_length=255, blank=True)
    meta_keywords = models.CharField(_('Meta keywords'), max_length=255, blank=True)
    
    # AI Verification
    ai_verified = models.BooleanField(_('AI verified'), default=False)
    ai_confidence_score = models.FloatField(
        _('AI confidence score'),
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    ai_verification_date = models.DateTimeField(
        _('AI verification date'),
        null=True,
        blank=True
    )
    
    # Admin Fields
    admin_notes = models.TextField(_('Admin notes'), blank=True)
    rejection_reason = models.TextField(_('Rejection reason'), blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_listings'
    )
    approved_at = models.DateTimeField(_('Approved at'), null=True, blank=True)
    
    # Timestamps
    published_at = models.DateTimeField(_('Published at'), null=True, blank=True, db_index=True)
    expires_at = models.DateTimeField(_('Expires at'), null=True, blank=True, db_index=True)
    sold_at = models.DateTimeField(_('Sold at'), null=True, blank=True)
    
    # Tags
    tags = TaggableManager(blank=True)
    
    class Meta:
        verbose_name = _('Listing')
        verbose_name_plural = _('Listings')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'listing_type', '-created_at']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['state', 'district', 'status']),
            models.Index(fields=['is_featured', 'status', '-created_at']),
            models.Index(fields=['price', 'status']),
            models.Index(fields=['-views', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)
    
    def generate_unique_slug(self):
        """Generate unique slug for the listing"""
        slug = slugify(self.title)
        unique_slug = slug
        num = 1
        while Listing.objects.filter(slug=unique_slug).exists():
            unique_slug = f'{slug}-{num}'
            num += 1
        return unique_slug
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('listings:detail', kwargs={'slug': self.slug})
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0
    
    @property
    def location_display(self):
        """Get formatted location display"""
        parts = []
        if self.locality:
            parts.append(self.locality)
        if self.city:
            parts.append(self.city.name)
        parts.append(self.district.name)
        parts.append(self.state.name)
        return ', '.join(parts)
    
    def increment_views(self, unique=False):
        """Increment view count"""
        self.views += 1
        if unique:
            self.unique_views += 1
        self.save(update_fields=['views', 'unique_views'])


class ListingImage(TimestampedModel):
    """
    Images for listings
    """
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = ProcessedImageField(
        upload_to=listing_image_upload_path,
        processors=[ResizeToFit(1200, 1200)],
        format='JPEG',
        options={'quality': 90}
    )
    thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 85}
    )
    medium = ImageSpecField(
        source='image',
        processors=[ResizeToFit(600, 600)],
        format='JPEG',
        options={'quality': 85}
    )
    caption = models.CharField(_('Caption'), max_length=200, blank=True)
    alt_text = models.CharField(_('Alt text'), max_length=200, blank=True)
    is_primary = models.BooleanField(_('Primary image'), default=False)
    order = models.PositiveIntegerField(_('Display order'), default=0)
    
    # AI Analysis
    ai_tags = models.JSONField(_('AI generated tags'), default=list, blank=True)
    ai_description = models.TextField(_('AI description'), blank=True)
    contains_text = models.BooleanField(_('Contains text'), default=False)
    is_inappropriate = models.BooleanField(_('Inappropriate content'), default=False)
    
    class Meta:
        verbose_name = _('Listing Image')
        verbose_name_plural = _('Listing Images')
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['listing', 'is_primary']),
        ]
    
    def __str__(self):
        return f'Image for {self.listing.title}'
    
    def save(self, *args, **kwargs):
        # Ensure only one primary image per listing
        if self.is_primary:
            ListingImage.objects.filter(
                listing=self.listing,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class ListingVideo(TimestampedModel):
    """
    Videos for listings
    """
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='videos'
    )
    video_file = models.FileField(
        _('Video file'),
        upload_to='listings/videos/',
        blank=True
    )
    video_url = models.URLField(
        _('Video URL'),
        blank=True,
        help_text=_('YouTube, Vimeo, or other video URL')
    )
    thumbnail = models.ImageField(
        _('Thumbnail'),
        upload_to='listings/video_thumbnails/',
        blank=True
    )
    title = models.CharField(_('Title'), max_length=200, blank=True)
    duration = models.DurationField(_('Duration'), null=True, blank=True)
    order = models.PositiveIntegerField(_('Display order'), default=0)
    
    class Meta:
        verbose_name = _('Listing Video')
        verbose_name_plural = _('Listing Videos')
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f'Video for {self.listing.title}'


class ListingAttribute(models.Model):
    """
    Dynamic attributes for listings based on category
    """
    FIELD_TYPE_CHOICES = [
        ('text', _('Text')),
        ('number', _('Number')),
        ('decimal', _('Decimal')),
        ('boolean', _('Yes/No')),
        ('date', _('Date')),
        ('choice', _('Choice')),
        ('multiple_choice', _('Multiple Choice')),
    ]
    
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='attributes'
    )
    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField(_('Slug'), max_length=120)
    field_type = models.CharField(
        _('Field type'),
        max_length=20,
        choices=FIELD_TYPE_CHOICES
    )
    choices = models.JSONField(
        _('Choices'),
        default=list,
        blank=True,
        help_text=_('For choice fields only')
    )
    unit = models.CharField(_('Unit'), max_length=20, blank=True)
    help_text = models.CharField(_('Help text'), max_length=200, blank=True)
    is_required = models.BooleanField(_('Required'), default=False)
    is_searchable = models.BooleanField(_('Searchable'), default=True)
    show_in_list = models.BooleanField(_('Show in list'), default=True)
    order = models.PositiveIntegerField(_('Display order'), default=0)
    
    class Meta:
        verbose_name = _('Listing Attribute')
        verbose_name_plural = _('Listing Attributes')
        ordering = ['category', 'order', 'name']
        unique_together = ['category', 'slug']
    
    def __str__(self):
        return f'{self.category.name} - {self.name}'


class ListingAttributeValue(models.Model):
    """
    Values for dynamic listing attributes
    """
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='attribute_values'
    )
    attribute = models.ForeignKey(
        ListingAttribute,
        on_delete=models.CASCADE,
        related_name='values'
    )
    value_text = models.TextField(_('Text value'), blank=True)
    value_number = models.BigIntegerField(_('Number value'), null=True, blank=True)
    value_decimal = models.DecimalField(
        _('Decimal value'),
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True
    )
    value_boolean = models.BooleanField(_('Boolean value'), null=True, blank=True)
    value_date = models.DateField(_('Date value'), null=True, blank=True)
    value_json = models.JSONField(_('JSON value'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('Listing Attribute Value')
        verbose_name_plural = _('Listing Attribute Values')
        unique_together = ['listing', 'attribute']
    
    def __str__(self):
        return f'{self.listing.title} - {self.attribute.name}'
    
    @property
    def display_value(self):
        """Get the appropriate value based on attribute type"""
        if self.attribute.field_type == 'text':
            return self.value_text
        elif self.attribute.field_type == 'number':
            return self.value_number
        elif self.attribute.field_type == 'decimal':
            return self.value_decimal
        elif self.attribute.field_type == 'boolean':
            return 'Yes' if self.value_boolean else 'No'
        elif self.attribute.field_type == 'date':
            return self.value_date
        elif self.attribute.field_type in ['choice', 'multiple_choice']:
            return self.value_json
        return self.value_text


class ListingFavorite(TimestampedModel):
    """
    User favorites/bookmarks for listings
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_listings'
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    notes = models.TextField(_('Notes'), blank=True)
    
    class Meta:
        verbose_name = _('Listing Favorite')
        verbose_name_plural = _('Listing Favorites')
        unique_together = ['user', 'listing']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.listing.title}'


class ListingView(models.Model):
    """
    Track listing views
    """
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='view_records'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='viewed_listings'
    )
    ip_address = models.GenericIPAddressField(_('IP Address'))
    user_agent = models.TextField(_('User Agent'), blank=True)
    referrer = models.URLField(_('Referrer'), blank=True)
    viewed_at = models.DateTimeField(_('Viewed at'), auto_now_add=True)
    session_id = models.CharField(_('Session ID'), max_length=40, blank=True)
    
    class Meta:
        verbose_name = _('Listing View')
        verbose_name_plural = _('Listing Views')
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['listing', '-viewed_at']),
            models.Index(fields=['user', '-viewed_at']),
        ]
    
    def __str__(self):
        return f'{self.listing.title} viewed at {self.viewed_at}'


class ListingReport(TimestampedModel):
    """
    Reports for inappropriate listings
    """
    REASON_CHOICES = [
        ('spam', _('Spam')),
        ('fake', _('Fake/Scam')),
        ('inappropriate', _('Inappropriate Content')),
        ('wrong_category', _('Wrong Category')),
        ('duplicate', _('Duplicate')),
        ('sold', _('Already Sold')),
        ('offensive', _('Offensive')),
        ('other', _('Other')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('reviewed', _('Reviewed')),
        ('action_taken', _('Action Taken')),
        ('dismissed', _('Dismissed')),
    ]
    
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listing_reports'
    )
    reason = models.CharField(
        _('Reason'),
        max_length=20,
        choices=REASON_CHOICES
    )
    description = models.TextField(_('Description'))
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_reports'
    )
    reviewed_at = models.DateTimeField(
        _('Reviewed at'),
        null=True,
        blank=True
    )
    admin_notes = models.TextField(_('Admin notes'), blank=True)
    
    class Meta:
        verbose_name = _('Listing Report')
        verbose_name_plural = _('Listing Reports')
        ordering = ['-created_at']
        unique_together = ['listing', 'reporter', 'reason']
    
    def __str__(self):
        return f'Report for {self.listing.title} - {self.get_reason_display()}'


class ListingPromotion(TimestampedModel):
    """
    Paid promotions for listings
    """
    PROMOTION_TYPE_CHOICES = [
        ('featured', _('Featured Listing')),
        ('premium', _('Premium Listing')),
        ('top', _('Top of Category')),
        ('homepage', _('Homepage Feature')),
        ('urgent', _('Urgent Badge')),
    ]
    
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='promotions'
    )
    promotion_type = models.CharField(
        _('Promotion type'),
        max_length=20,
        choices=PROMOTION_TYPE_CHOICES
    )
    start_date = models.DateTimeField(_('Start date'))
    end_date = models.DateTimeField(_('End date'))
    amount_paid = models.DecimalField(
        _('Amount paid'),
        max_digits=10,
        decimal_places=2
    )
    payment_reference = models.CharField(
        _('Payment reference'),
        max_length=100,
        blank=True
    )
    is_active = models.BooleanField(_('Active'), default=True)
    impressions = models.BigIntegerField(_('Impressions'), default=0)
    clicks = models.BigIntegerField(_('Clicks'), default=0)
    
    class Meta:
        verbose_name = _('Listing Promotion')
        verbose_name_plural = _('Listing Promotions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['listing', 'is_active', 'end_date']),
        ]
    
    def __str__(self):
        return f'{self.listing.title} - {self.get_promotion_type_display()}'