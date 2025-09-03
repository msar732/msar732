from django.db import models
from listings.models import Listing

class AIVerificationResult(models.Model):
    listing = models.OneToOneField(Listing, on_delete=models.CASCADE)
    genuineness_score = models.FloatField()
    image_analysis_score = models.FloatField()
    text_analysis_score = models.FloatField()
    location_verification_score = models.FloatField()
    verification_details = models.JSONField()
    is_genuine = models.BooleanField()
    processed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"AI Verification for {self.listing.title}"