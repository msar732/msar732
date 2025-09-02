"""
Core models for TradeIndia platform
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class TimestampedModel(models.Model):
    """
    Abstract base model with created and modified timestamps
    """
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True, db_index=True)
    modified_at = models.DateTimeField(_('Modified at'), auto_now=True, db_index=True)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']


class UUIDModel(models.Model):
    """
    Abstract base model with UUID primary key
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class Meta:
        abstract = True


class Category(MPTTModel, TimestampedModel):
    """
    Hierarchical category model for listings
    """
    name = models.CharField(_('Name'), max_length=100, db_index=True)
    slug = models.SlugField(_('Slug'), max_length=120, unique=True)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Parent category')
    )
    description = models.TextField(_('Description'), blank=True)
    icon = models.CharField(_('Icon class'), max_length=50, blank=True, help_text=_('Font Awesome icon class'))
    image = models.ImageField(_('Image'), upload_to='categories/', blank=True)
    is_active = models.BooleanField(_('Active'), default=True, db_index=True)
    featured = models.BooleanField(_('Featured'), default=False, db_index=True)
    order = models.PositiveIntegerField(_('Display order'), default=0)
    meta_title = models.CharField(_('Meta title'), max_length=155, blank=True)
    meta_description = models.TextField(_('Meta description'), max_length=255, blank=True)
    
    class MPTTMeta:
        order_insertion_by = ['order', 'name']
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('listings:category_detail', kwargs={'slug': self.slug})
    
    @property
    def full_path(self):
        """Get the full category path"""
        ancestors = self.get_ancestors(include_self=True)
        return ' > '.join([ancestor.name for ancestor in ancestors])


class State(TimestampedModel):
    """
    Indian states and union territories
    """
    code = models.CharField(_('State code'), max_length=2, primary_key=True)
    name = models.CharField(_('State name'), max_length=100, unique=True, db_index=True)
    slug = models.SlugField(_('Slug'), max_length=120, unique=True)
    capital = models.CharField(_('Capital'), max_length=100, blank=True)
    largest_city = models.CharField(_('Largest city'), max_length=100, blank=True)
    population = models.BigIntegerField(_('Population'), default=0)
    area = models.FloatField(_('Area (km²)'), default=0)
    official_languages = models.CharField(_('Official languages'), max_length=200, blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    
    class Meta:
        verbose_name = _('State')
        verbose_name_plural = _('States')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class District(TimestampedModel):
    """
    Districts within Indian states
    """
    name = models.CharField(_('District name'), max_length=100, db_index=True)
    slug = models.SlugField(_('Slug'), max_length=120)
    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name='districts',
        verbose_name=_('State')
    )
    headquarters = models.CharField(_('Headquarters'), max_length=100, blank=True)
    population = models.BigIntegerField(_('Population'), default=0)
    area = models.FloatField(_('Area (km²)'), default=0)
    pin_codes = models.TextField(_('PIN codes'), blank=True, help_text=_('Comma-separated PIN codes'))
    is_active = models.BooleanField(_('Active'), default=True)
    latitude = models.FloatField(_('Latitude'), null=True, blank=True)
    longitude = models.FloatField(_('Longitude'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('District')
        verbose_name_plural = _('Districts')
        ordering = ['state', 'name']
        unique_together = ['state', 'slug']
    
    def __str__(self):
        return f'{self.name}, {self.state.name}'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class City(TimestampedModel):
    """
    Cities and towns within districts
    """
    name = models.CharField(_('City name'), max_length=100, db_index=True)
    slug = models.SlugField(_('Slug'), max_length=120)
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name='cities',
        verbose_name=_('District')
    )
    population = models.BigIntegerField(_('Population'), default=0)
    pin_code = models.CharField(_('PIN code'), max_length=6, blank=True)
    std_code = models.CharField(_('STD code'), max_length=10, blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    latitude = models.FloatField(_('Latitude'), null=True, blank=True)
    longitude = models.FloatField(_('Longitude'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')
        ordering = ['district', 'name']
        unique_together = ['district', 'slug']
    
    def __str__(self):
        return f'{self.name}, {self.district.name}'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(TimestampedModel):
    """
    Tags for listings
    """
    name = models.CharField(_('Name'), max_length=50, unique=True)
    slug = models.SlugField(_('Slug'), max_length=60, unique=True)
    description = models.TextField(_('Description'), blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    
    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Currency(models.Model):
    """
    Currency model for multi-currency support
    """
    code = models.CharField(_('Currency code'), max_length=3, primary_key=True)
    name = models.CharField(_('Currency name'), max_length=50)
    symbol = models.CharField(_('Symbol'), max_length=10)
    exchange_rate = models.DecimalField(
        _('Exchange rate to INR'),
        max_digits=10,
        decimal_places=4,
        default=1.0000
    )
    is_active = models.BooleanField(_('Active'), default=True)
    
    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')
        ordering = ['code']
    
    def __str__(self):
        return f'{self.name} ({self.code})'


class Advertisement(TimestampedModel):
    """
    Advertisement banners and sponsored content
    """
    POSITION_CHOICES = [
        ('header', _('Header')),
        ('sidebar', _('Sidebar')),
        ('footer', _('Footer')),
        ('listing_top', _('Listing Top')),
        ('listing_bottom', _('Listing Bottom')),
        ('search_results', _('Search Results')),
        ('home_banner', _('Home Banner')),
    ]
    
    title = models.CharField(_('Title'), max_length=200)
    advertiser = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='advertisements',
        verbose_name=_('Advertiser')
    )
    position = models.CharField(_('Position'), max_length=20, choices=POSITION_CHOICES, db_index=True)
    image = models.ImageField(_('Image'), upload_to='advertisements/')
    link = models.URLField(_('Link'), max_length=500)
    alt_text = models.CharField(_('Alt text'), max_length=200)
    start_date = models.DateTimeField(_('Start date'), db_index=True)
    end_date = models.DateTimeField(_('End date'), db_index=True)
    impressions = models.BigIntegerField(_('Impressions'), default=0)
    clicks = models.BigIntegerField(_('Clicks'), default=0)
    is_active = models.BooleanField(_('Active'), default=True, db_index=True)
    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name='advertisements',
        verbose_name=_('Categories')
    )
    states = models.ManyToManyField(
        State,
        blank=True,
        related_name='advertisements',
        verbose_name=_('States')
    )
    priority = models.IntegerField(_('Priority'), default=0, help_text=_('Higher priority ads show first'))
    
    class Meta:
        verbose_name = _('Advertisement')
        verbose_name_plural = _('Advertisements')
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['position', 'is_active', 'start_date', 'end_date']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def ctr(self):
        """Click-through rate"""
        if self.impressions > 0:
            return (self.clicks / self.impressions) * 100
        return 0


class FAQ(TimestampedModel):
    """
    Frequently Asked Questions
    """
    question = models.CharField(_('Question'), max_length=500)
    answer = models.TextField(_('Answer'))
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='faqs',
        verbose_name=_('Category')
    )
    order = models.PositiveIntegerField(_('Display order'), default=0)
    is_active = models.BooleanField(_('Active'), default=True)
    views = models.BigIntegerField(_('Views'), default=0)
    helpful_votes = models.BigIntegerField(_('Helpful votes'), default=0)
    
    class Meta:
        verbose_name = _('FAQ')
        verbose_name_plural = _('FAQs')
        ordering = ['order', '-helpful_votes']
    
    def __str__(self):
        return self.question


class Page(TimestampedModel):
    """
    Static pages like About Us, Terms, etc.
    """
    title = models.CharField(_('Title'), max_length=200)
    slug = models.SlugField(_('Slug'), max_length=220, unique=True)
    content = models.TextField(_('Content'))
    meta_title = models.CharField(_('Meta title'), max_length=155, blank=True)
    meta_description = models.TextField(_('Meta description'), max_length=255, blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    show_in_footer = models.BooleanField(_('Show in footer'), default=False)
    show_in_header = models.BooleanField(_('Show in header'), default=False)
    order = models.PositiveIntegerField(_('Display order'), default=0)
    
    class Meta:
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('core:page_detail', kwargs={'slug': self.slug})


class SiteConfiguration(models.Model):
    """
    Singleton model for site-wide configuration
    """
    site_name = models.CharField(_('Site name'), max_length=100, default='TradeIndia')
    tagline = models.CharField(_('Tagline'), max_length=200, default='Buy and Sell Anything in India')
    logo = models.ImageField(_('Logo'), upload_to='site/', blank=True)
    favicon = models.ImageField(_('Favicon'), upload_to='site/', blank=True)
    contact_email = models.EmailField(_('Contact email'), default='support@tradeindia.com')
    contact_phone = models.CharField(_('Contact phone'), max_length=20, blank=True)
    contact_address = models.TextField(_('Contact address'), blank=True)
    facebook_url = models.URLField(_('Facebook URL'), blank=True)
    twitter_url = models.URLField(_('Twitter URL'), blank=True)
    instagram_url = models.URLField(_('Instagram URL'), blank=True)
    youtube_url = models.URLField(_('YouTube URL'), blank=True)
    linkedin_url = models.URLField(_('LinkedIn URL'), blank=True)
    whatsapp_number = models.CharField(_('WhatsApp number'), max_length=20, blank=True)
    google_analytics_id = models.CharField(_('Google Analytics ID'), max_length=20, blank=True)
    facebook_pixel_id = models.CharField(_('Facebook Pixel ID'), max_length=20, blank=True)
    maintenance_mode = models.BooleanField(_('Maintenance mode'), default=False)
    maintenance_message = models.TextField(_('Maintenance message'), blank=True)
    terms_of_service = models.TextField(_('Terms of Service'), blank=True)
    privacy_policy = models.TextField(_('Privacy Policy'), blank=True)
    listing_approval_required = models.BooleanField(_('Listing approval required'), default=False)
    max_images_per_listing = models.PositiveIntegerField(_('Max images per listing'), default=10)
    max_free_listings_per_user = models.PositiveIntegerField(_('Max free listings per user'), default=50)
    featured_listing_price = models.DecimalField(
        _('Featured listing price'),
        max_digits=10,
        decimal_places=2,
        default=100.00
    )
    commission_percentage = models.DecimalField(
        _('Commission percentage'),
        max_digits=5,
        decimal_places=2,
        default=2.50,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    minimum_listing_price = models.DecimalField(
        _('Minimum listing price'),
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    maximum_listing_price = models.DecimalField(
        _('Maximum listing price'),
        max_digits=15,
        decimal_places=2,
        default=999999999.99
    )
    
    class Meta:
        verbose_name = _('Site Configuration')
        verbose_name_plural = _('Site Configuration')
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        pass
    
    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj