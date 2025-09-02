from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from locations.models import State, District, City


class User(AbstractUser):
    """Extended user model with additional fields"""
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    email = models.EmailField(unique=True)
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Location fields
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField(max_length=300, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    
    # Verification and ratings
    is_verified = models.BooleanField(default=False)
    verification_document = models.ImageField(upload_to='verification/', blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_ratings = models.PositiveIntegerField(default=0)
    
    # Activity tracking
    last_active = models.DateTimeField(auto_now=True)
    total_listings = models.PositiveIntegerField(default=0)
    successful_trades = models.PositiveIntegerField(default=0)
    
    # Preferences
    preferred_categories = models.ManyToManyField('listings.Category', blank=True)
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['state', 'district']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['rating']),
            models.Index(fields=['last_active']),
        ]

    def __str__(self):
        return self.email

    def get_full_location(self):
        """Return full location string"""
        location_parts = []
        if self.city:
            location_parts.append(self.city.name)
        if self.district:
            location_parts.append(self.district.name)
        if self.state:
            location_parts.append(self.state.name)
        return ", ".join(location_parts)

    def update_rating(self, new_rating):
        """Update user rating with new rating"""
        total_score = self.rating * self.total_ratings + new_rating
        self.total_ratings += 1
        self.rating = total_score / self.total_ratings
        self.save()


class UserRating(models.Model):
    """Model for user ratings and reviews"""
    rater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    rated_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_ratings')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    review = models.TextField(max_length=500, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)  # Reference to trade
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['rater', 'rated_user', 'transaction_id']
        indexes = [
            models.Index(fields=['rated_user', 'rating']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.rater.username} rated {self.rated_user.username}: {self.rating}/5"


class UserFollowing(models.Model):
    """Model for user following system"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['follower', 'following']
        indexes = [
            models.Index(fields=['follower']),
            models.Index(fields=['following']),
        ]

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"