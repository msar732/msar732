"""
AI Verification models for listing authenticity checks
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.models import TimestampedModel
from apps.listings.models import Listing, ListingImage


class AIVerificationLog(TimestampedModel):
    """
    Log of AI verification attempts
    """
    VERIFICATION_TYPE_CHOICES = [
        ('listing', _('Listing Verification')),
        ('image', _('Image Verification')),
        ('text', _('Text Analysis')),
        ('price', _('Price Analysis')),
        ('user', _('User Verification')),
        ('fraud', _('Fraud Detection')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    ]
    
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='ai_verifications'
    )
    verification_type = models.CharField(
        _('Verification type'),
        max_length=20,
        choices=VERIFICATION_TYPE_CHOICES
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Results
    is_genuine = models.BooleanField(_('Is genuine'), null=True, blank=True)
    confidence_score = models.FloatField(_('Confidence score'), null=True, blank=True)
    risk_score = models.FloatField(_('Risk score'), null=True, blank=True)
    
    # Analysis details
    analysis_results = models.JSONField(_('Analysis results'), default=dict)
    detected_issues = models.JSONField(_('Detected issues'), default=list)
    recommendations = models.JSONField(_('Recommendations'), default=list)
    
    # Processing details
    processing_time = models.FloatField(_('Processing time (seconds)'), null=True, blank=True)
    model_version = models.CharField(_('Model version'), max_length=50, blank=True)
    error_message = models.TextField(_('Error message'), blank=True)
    
    class Meta:
        verbose_name = _('AI Verification Log')
        verbose_name_plural = _('AI Verification Logs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['listing', 'verification_type', 'status']),
        ]
    
    def __str__(self):
        return f'{self.listing.title} - {self.get_verification_type_display()}'


class FraudPattern(TimestampedModel):
    """
    Known fraud patterns for detection
    """
    PATTERN_TYPE_CHOICES = [
        ('title', _('Title Pattern')),
        ('description', _('Description Pattern')),
        ('price', _('Price Pattern')),
        ('image', _('Image Pattern')),
        ('behavior', _('User Behavior Pattern')),
        ('contact', _('Contact Pattern')),
    ]
    
    name = models.CharField(_('Pattern name'), max_length=100)
    pattern_type = models.CharField(
        _('Pattern type'),
        max_length=20,
        choices=PATTERN_TYPE_CHOICES
    )
    pattern_data = models.JSONField(_('Pattern data'))
    severity = models.IntegerField(
        _('Severity'),
        default=5,
        help_text=_('1-10, higher is more severe')
    )
    description = models.TextField(_('Description'))
    examples = models.JSONField(_('Examples'), default=list, blank=True)
    
    # Statistics
    detection_count = models.BigIntegerField(_('Detection count'), default=0)
    false_positive_count = models.BigIntegerField(_('False positive count'), default=0)
    
    is_active = models.BooleanField(_('Active'), default=True)
    
    class Meta:
        verbose_name = _('Fraud Pattern')
        verbose_name_plural = _('Fraud Patterns')
        ordering = ['-severity', 'name']
    
    def __str__(self):
        return self.name
    
    @property
    def accuracy(self):
        total = self.detection_count
        if total > 0:
            return ((total - self.false_positive_count) / total) * 100
        return 0


class ImageAnalysis(TimestampedModel):
    """
    AI analysis results for listing images
    """
    image = models.OneToOneField(
        ListingImage,
        on_delete=models.CASCADE,
        related_name='ai_analysis'
    )
    
    # Content detection
    detected_objects = models.JSONField(_('Detected objects'), default=list)
    detected_text = models.TextField(_('Detected text'), blank=True)
    detected_logos = models.JSONField(_('Detected logos'), default=list)
    dominant_colors = models.JSONField(_('Dominant colors'), default=list)
    
    # Quality metrics
    quality_score = models.FloatField(_('Quality score'), null=True, blank=True)
    blur_score = models.FloatField(_('Blur score'), null=True, blank=True)
    brightness_score = models.FloatField(_('Brightness score'), null=True, blank=True)
    
    # Authenticity checks
    is_stock_photo = models.BooleanField(_('Is stock photo'), default=False)
    is_watermarked = models.BooleanField(_('Is watermarked'), default=False)
    is_edited = models.BooleanField(_('Is edited'), default=False)
    edit_probability = models.FloatField(_('Edit probability'), null=True, blank=True)
    
    # Content moderation
    is_inappropriate = models.BooleanField(_('Is inappropriate'), default=False)
    inappropriate_score = models.FloatField(_('Inappropriate score'), null=True, blank=True)
    moderation_labels = models.JSONField(_('Moderation labels'), default=list)
    
    # Duplicate detection
    is_duplicate = models.BooleanField(_('Is duplicate'), default=False)
    duplicate_of = models.ForeignKey(
        ListingImage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='duplicates'
    )
    similarity_score = models.FloatField(_('Similarity score'), null=True, blank=True)
    
    # Processing details
    processed_at = models.DateTimeField(_('Processed at'), auto_now_add=True)
    processing_time = models.FloatField(_('Processing time (seconds)'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Image Analysis')
        verbose_name_plural = _('Image Analyses')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Analysis for {self.image}'


class TextAnalysis(TimestampedModel):
    """
    AI analysis for listing text content
    """
    listing = models.OneToOneField(
        Listing,
        on_delete=models.CASCADE,
        related_name='text_analysis'
    )
    
    # Language and quality
    detected_language = models.CharField(_('Detected language'), max_length=10, blank=True)
    language_confidence = models.FloatField(_('Language confidence'), null=True, blank=True)
    grammar_score = models.FloatField(_('Grammar score'), null=True, blank=True)
    readability_score = models.FloatField(_('Readability score'), null=True, blank=True)
    
    # Content analysis
    sentiment_score = models.FloatField(_('Sentiment score'), null=True, blank=True)
    sentiment_label = models.CharField(_('Sentiment label'), max_length=20, blank=True)
    keywords = models.JSONField(_('Keywords'), default=list)
    entities = models.JSONField(_('Named entities'), default=list)
    
    # Spam and fraud detection
    spam_score = models.FloatField(_('Spam score'), null=True, blank=True)
    is_spam = models.BooleanField(_('Is spam'), default=False)
    suspicious_phrases = models.JSONField(_('Suspicious phrases'), default=list)
    
    # Contact information detection
    contains_phone = models.BooleanField(_('Contains phone'), default=False)
    contains_email = models.BooleanField(_('Contains email'), default=False)
    contains_url = models.BooleanField(_('Contains URL'), default=False)
    extracted_contacts = models.JSONField(_('Extracted contacts'), default=dict)
    
    # Category relevance
    category_relevance_score = models.FloatField(
        _('Category relevance score'),
        null=True,
        blank=True
    )
    suggested_categories = models.JSONField(_('Suggested categories'), default=list)
    
    class Meta:
        verbose_name = _('Text Analysis')
        verbose_name_plural = _('Text Analyses')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Text analysis for {self.listing.title}'


class PriceAnalysis(TimestampedModel):
    """
    AI-based price analysis and recommendations
    """
    listing = models.OneToOneField(
        Listing,
        on_delete=models.CASCADE,
        related_name='price_analysis'
    )
    
    # Market analysis
    market_average = models.DecimalField(
        _('Market average'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    market_min = models.DecimalField(
        _('Market minimum'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    market_max = models.DecimalField(
        _('Market maximum'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Price evaluation
    price_percentile = models.FloatField(_('Price percentile'), null=True, blank=True)
    is_overpriced = models.BooleanField(_('Is overpriced'), default=False)
    is_underpriced = models.BooleanField(_('Is underpriced'), default=False)
    price_score = models.FloatField(_('Price score'), null=True, blank=True)
    
    # Recommendations
    recommended_price = models.DecimalField(
        _('Recommended price'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    price_range_min = models.DecimalField(
        _('Price range minimum'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    price_range_max = models.DecimalField(
        _('Price range maximum'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Analysis details
    comparable_listings = models.JSONField(_('Comparable listings'), default=list)
    price_factors = models.JSONField(_('Price factors'), default=dict)
    confidence_level = models.FloatField(_('Confidence level'), null=True, blank=True)
    
    # Market trends
    price_trend = models.CharField(
        _('Price trend'),
        max_length=20,
        choices=[
            ('increasing', _('Increasing')),
            ('stable', _('Stable')),
            ('decreasing', _('Decreasing')),
        ],
        blank=True
    )
    demand_level = models.CharField(
        _('Demand level'),
        max_length=20,
        choices=[
            ('high', _('High')),
            ('medium', _('Medium')),
            ('low', _('Low')),
        ],
        blank=True
    )
    
    class Meta:
        verbose_name = _('Price Analysis')
        verbose_name_plural = _('Price Analyses')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Price analysis for {self.listing.title}'


class UserTrustScore(TimestampedModel):
    """
    AI-calculated trust score for users
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trust_score'
    )
    
    # Overall score
    trust_score = models.FloatField(
        _('Trust score'),
        default=50.0,
        help_text=_('0-100, higher is more trustworthy')
    )
    score_components = models.JSONField(_('Score components'), default=dict)
    
    # Verification factors
    identity_verified_score = models.FloatField(_('Identity verification score'), default=0)
    behavior_score = models.FloatField(_('Behavior score'), default=50)
    transaction_score = models.FloatField(_('Transaction score'), default=50)
    communication_score = models.FloatField(_('Communication score'), default=50)
    listing_quality_score = models.FloatField(_('Listing quality score'), default=50)
    
    # Risk indicators
    risk_level = models.CharField(
        _('Risk level'),
        max_length=20,
        choices=[
            ('low', _('Low Risk')),
            ('medium', _('Medium Risk')),
            ('high', _('High Risk')),
        ],
        default='medium'
    )
    risk_factors = models.JSONField(_('Risk factors'), default=list)
    
    # Activity metrics
    suspicious_activities = models.IntegerField(_('Suspicious activities'), default=0)
    reported_count = models.IntegerField(_('Reported count'), default=0)
    successful_transactions = models.IntegerField(_('Successful transactions'), default=0)
    failed_transactions = models.IntegerField(_('Failed transactions'), default=0)
    
    # Update tracking
    last_calculated = models.DateTimeField(_('Last calculated'), auto_now=True)
    calculation_version = models.CharField(_('Calculation version'), max_length=20, blank=True)
    
    class Meta:
        verbose_name = _('User Trust Score')
        verbose_name_plural = _('User Trust Scores')
        ordering = ['-trust_score']
    
    def __str__(self):
        return f'{self.user.username} - Trust Score: {self.trust_score}'
    
    @property
    def trust_level(self):
        """Get trust level based on score"""
        if self.trust_score >= 80:
            return 'Very High'
        elif self.trust_score >= 60:
            return 'High'
        elif self.trust_score >= 40:
            return 'Medium'
        elif self.trust_score >= 20:
            return 'Low'
        return 'Very Low'