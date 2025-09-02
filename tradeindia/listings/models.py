from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from locations.models import State, District, City
import uuid

User = get_user_model()


class Category(models.Model):
    """Model for listing categories"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Font awesome icon class
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name_plural = 'Categories'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['parent']),
            models.Index(fields=['is_active', 'sort_order']),
        ]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    def get_absolute_url(self):
        return reverse('listings:category', kwargs={'slug': self.slug})


class Condition(models.Model):
    """Model for item conditions"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.name


class Listing(models.Model):
    """Main model for listings/items"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
        ('pending_verification', 'Pending Verification'),
    ]

    LISTING_TYPE_CHOICES = [
        ('sell', 'For Sale'),
        ('buy', 'Looking to Buy'),
        ('exchange', 'Exchange'),
        ('rent', 'For Rent'),
        ('service', 'Service'),
    ]

    # Basic information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='listings')
    condition = models.ForeignKey(Condition, on_delete=models.SET_NULL, null=True, blank=True)
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPE_CHOICES, default='sell')
    
    # Pricing
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    is_negotiable = models.BooleanField(default=True)
    currency = models.CharField(max_length=3, default='INR')
    
    # Location
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    address = models.TextField(max_length=300, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    # Status and verification
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_verification')
    is_featured = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    ai_verification_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    
    # Engagement metrics
    views = models.PositiveIntegerField(default=0)
    favorites_count = models.PositiveIntegerField(default=0)
    inquiries_count = models.PositiveIntegerField(default=0)
    
    # SEO and search
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    search_vector = models.TextField(blank=True)  # For full-text search
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    sold_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_verified']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['state', 'district', 'status']),
            models.Index(fields=['price', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_featured', 'status']),
            models.Index(fields=['listing_type', 'status']),
            models.Index(fields=['seller', 'status']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('listings:detail', kwargs={'pk': self.pk})

    def get_main_image(self):
        """Get the main image for the listing"""
        main_image = self.images.filter(is_main=True).first()
        if main_image:
            return main_image
        return self.images.first()

    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.save(update_fields=['views'])

    def get_location_string(self):
        """Get formatted location string"""
        parts = []
        if self.city:
            parts.append(self.city.name)
        parts.append(self.district.name)
        parts.append(self.state.name)
        return ", ".join(parts)


class ListingImage(models.Model):
    """Model for listing images"""
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='listings/%Y/%m/%d/')
    caption = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'created_at']
        indexes = [
            models.Index(fields=['listing', 'is_main']),
            models.Index(fields=['listing', 'sort_order']),
        ]

    def __str__(self):
        return f"Image for {self.listing.title}"

    def save(self, *args, **kwargs):
        # Ensure only one main image per listing
        if self.is_main:
            ListingImage.objects.filter(listing=self.listing, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)


class ListingAttribute(models.Model):
    """Model for dynamic listing attributes"""
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='attributes')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['listing', 'name']
        indexes = [
            models.Index(fields=['listing', 'name']),
        ]

    def __str__(self):
        return f"{self.name}: {self.value}"


class Favorite(models.Model):
    """Model for user favorites"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'listing']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['listing']),
        ]

    def __str__(self):
        return f"{self.user.username} favorited {self.listing.title}"


class Inquiry(models.Model):
    """Model for listing inquiries"""
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='inquiries')
    inquirer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inquiries_made')
    message = models.TextField()
    phone_number = models.CharField(max_length=17, blank=True)
    email = models.EmailField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['listing', 'created_at']),
            models.Index(fields=['inquirer', 'created_at']),
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        return f"Inquiry for {self.listing.title} by {self.inquirer.username}"


class Report(models.Model):
    """Model for reporting inappropriate listings"""
    REASON_CHOICES = [
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
        ('fake', 'Fake Listing'),
        ('duplicate', 'Duplicate Listing'),
        ('wrong_category', 'Wrong Category'),
        ('other', 'Other'),
    ]

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['listing', 'reporter']
        indexes = [
            models.Index(fields=['listing', 'is_resolved']),
            models.Index(fields=['reason', 'is_resolved']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Report for {self.listing.title} by {self.reporter.username}"


class SavedSearch(models.Model):
    """Model for saved searches"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_searches')
    name = models.CharField(max_length=100)
    query = models.CharField(max_length=200, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=True, blank=True)
    min_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    listing_type = models.CharField(max_length=20, choices=Listing.LISTING_TYPE_CHOICES, blank=True)
    email_alerts = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.name}"