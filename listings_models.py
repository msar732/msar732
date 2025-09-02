# Listings App Models
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth import get_user_model
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
import uuid

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    icon = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        indexes = [models.Index(fields=['slug', 'is_active'])]
    
    def __str__(self):
        return self.name

class State(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return self.name

class District(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='districts')
    
    class Meta:
        unique_together = ['name', 'state']
    
    def __str__(self):
        return f"{self.name}, {self.state.name}"

class Listing(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('expired', 'Expired'),
        ('pending', 'Pending'),
        ('draft', 'Draft'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2, db_index=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    location = gis_models.PointField()
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField(blank=True)
    is_negotiable = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    ai_genuineness_score = models.FloatField(default=0.0)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'state', 'status']),
            models.Index(fields=['price', 'created_at']),
            models.Index(fields=['ai_genuineness_score']),
            models.Index(fields=['location']),
        ]
    
    def __str__(self):
        return self.title

class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = ProcessedImageField(
        upload_to='listings/',
        processors=[ResizeToFit(800, 600)],
        format='JPEG',
        options={'quality': 80}
    )
    thumbnail = ProcessedImageField(
        upload_to='listings/thumbnails/',
        processors=[ResizeToFit(200, 150)],
        format='JPEG',
        options={'quality': 60}
    )
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['listing', 'order']

class ListingView(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['listing', 'ip_address', 'user']

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'listing']