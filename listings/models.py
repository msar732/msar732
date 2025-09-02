from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse

User = get_user_model()


class State(models.Model):
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=128)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='districts')

    class Meta:
        unique_together = ('name', 'state')
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.state.name}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ListingQuerySet(models.QuerySet):
    def search(self, query: str):
        return self.filter(models.Q(title__icontains=query) | models.Q(description__icontains=query))


class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='listings')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name='listings')
    district = models.ForeignKey(District, on_delete=models.PROTECT, related_name='listings')
    address = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    ai_genuine_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ListingQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['category', 'state', 'district']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('listing_detail', args=[str(self.id)])

    @property
    def primary_image_url(self):
        img = self.images.first()
        return img.image.url if img else '/static/img/placeholder.jpg'


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='listings/%Y/%m/')
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.listing_id}"


# Create your models here.
