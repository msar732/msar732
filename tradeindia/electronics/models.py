from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth import get_user_model

User = get_user_model()

class ElectronicsCategory(models.Model):
    CATEGORY_CHOICES = [
        ('mobile_phones', 'Mobile Phones'),
        ('laptops_computers', 'Laptops & Computers'),
        ('tablets', 'Tablets'),
        ('cameras', 'Cameras & Photography'),
        ('audio_video', 'Audio & Video'),
        ('gaming', 'Gaming'),
        ('home_appliances', 'Home Appliances'),
        ('kitchen_appliances', 'Kitchen Appliances'),
        ('accessories', 'Accessories'),
        ('other', 'Other Electronics')
    ]
    
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.display_name

class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='brands/', blank=True)
    is_popular = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class ElectronicsListing(models.Model):
    WARRANTY_CHOICES = [
        ('no_warranty', 'No Warranty'),
        ('manufacturer', 'Manufacturer Warranty'),
        ('seller', 'Seller Warranty'),
        ('extended', 'Extended Warranty')
    ]
    
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(ElectronicsCategory, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    
    # Electronics specific fields
    model_name = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    warranty_status = models.CharField(max_length=20, choices=WARRANTY_CHOICES, default='no_warranty')
    warranty_till = models.DateField(null=True, blank=True)
    
    # Technical specifications (JSON for flexibility)
    specifications = models.JSONField(default=dict, blank=True)
    included_accessories = models.JSONField(default=list, blank=True)
    
    # Standard fields
    location = gis_models.PointField()
    address = models.CharField(max_length=255)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    ai_score = models.FloatField(default=0.0)
    
    view_count = models.PositiveIntegerField(default=0)
    inquiry_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']