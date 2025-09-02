"""
Search-related models for TradeIndia
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.models import TimestampedModel


class SearchQuery(TimestampedModel):
    """
    Track search queries for analytics and suggestions
    """
    query = models.CharField(_('Search query'), max_length=255, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='search_queries'
    )
    ip_address = models.GenericIPAddressField(_('IP Address'))
    results_count = models.PositiveIntegerField(_('Results count'), default=0)
    category_filter = models.CharField(_('Category filter'), max_length=100, blank=True)
    location_filter = models.CharField(_('Location filter'), max_length=100, blank=True)
    price_min = models.DecimalField(
        _('Minimum price'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    price_max = models.DecimalField(
        _('Maximum price'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    filters_applied = models.JSONField(_('Filters applied'), default=dict, blank=True)
    clicked_results = models.JSONField(_('Clicked results'), default=list, blank=True)
    session_id = models.CharField(_('Session ID'), max_length=40, blank=True)
    
    class Meta:
        verbose_name = _('Search Query')
        verbose_name_plural = _('Search Queries')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['query', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return self.query


class PopularSearch(TimestampedModel):
    """
    Popular search terms for autocomplete and suggestions
    """
    term = models.CharField(_('Search term'), max_length=100, unique=True, db_index=True)
    search_count = models.BigIntegerField(_('Search count'), default=0)
    click_count = models.BigIntegerField(_('Click count'), default=0)
    conversion_count = models.BigIntegerField(_('Conversion count'), default=0)
    is_active = models.BooleanField(_('Active'), default=True)
    is_promoted = models.BooleanField(_('Promoted'), default=False)
    category = models.ForeignKey(
        'core.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='popular_searches'
    )
    
    class Meta:
        verbose_name = _('Popular Search')
        verbose_name_plural = _('Popular Searches')
        ordering = ['-search_count']
    
    def __str__(self):
        return self.term
    
    @property
    def click_rate(self):
        if self.search_count > 0:
            return (self.click_count / self.search_count) * 100
        return 0
    
    @property
    def conversion_rate(self):
        if self.click_count > 0:
            return (self.conversion_count / self.click_count) * 100
        return 0


class SavedSearch(TimestampedModel):
    """
    User saved searches with alerts
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_searches'
    )
    name = models.CharField(_('Search name'), max_length=100)
    query = models.CharField(_('Search query'), max_length=255, blank=True)
    category = models.ForeignKey(
        'core.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    state = models.ForeignKey(
        'core.State',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    district = models.ForeignKey(
        'core.District',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    city = models.ForeignKey(
        'core.City',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    price_min = models.DecimalField(
        _('Minimum price'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    price_max = models.DecimalField(
        _('Maximum price'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    filters = models.JSONField(_('Additional filters'), default=dict, blank=True)
    
    # Alert settings
    alert_enabled = models.BooleanField(_('Alert enabled'), default=True)
    alert_frequency = models.CharField(
        _('Alert frequency'),
        max_length=20,
        choices=[
            ('instant', _('Instant')),
            ('daily', _('Daily')),
            ('weekly', _('Weekly')),
        ],
        default='daily'
    )
    last_alert_sent = models.DateTimeField(
        _('Last alert sent'),
        null=True,
        blank=True
    )
    alert_count = models.PositiveIntegerField(_('Alert count'), default=0)
    
    class Meta:
        verbose_name = _('Saved Search')
        verbose_name_plural = _('Saved Searches')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'alert_enabled']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.name}'
    
    def get_search_url(self):
        """Generate search URL from saved parameters"""
        from django.urls import reverse
        from urllib.parse import urlencode
        
        params = {}
        if self.query:
            params['q'] = self.query
        if self.category:
            params['category'] = self.category.slug
        if self.state:
            params['state'] = self.state.code
        if self.district:
            params['district'] = self.district.slug
        if self.city:
            params['city'] = self.city.slug
        if self.price_min:
            params['price_min'] = str(self.price_min)
        if self.price_max:
            params['price_max'] = str(self.price_max)
        
        # Add additional filters
        params.update(self.filters)
        
        url = reverse('search:listing_search')
        if params:
            url += '?' + urlencode(params)
        
        return url


class SearchSuggestion(TimestampedModel):
    """
    AI-generated search suggestions
    """
    original_query = models.CharField(_('Original query'), max_length=255)
    suggested_query = models.CharField(_('Suggested query'), max_length=255)
    suggestion_type = models.CharField(
        _('Suggestion type'),
        max_length=20,
        choices=[
            ('spelling', _('Spelling Correction')),
            ('synonym', _('Synonym')),
            ('related', _('Related Term')),
            ('category', _('Category Suggestion')),
            ('location', _('Location Suggestion')),
        ]
    )
    confidence_score = models.FloatField(_('Confidence score'), default=0.0)
    times_shown = models.BigIntegerField(_('Times shown'), default=0)
    times_clicked = models.BigIntegerField(_('Times clicked'), default=0)
    is_active = models.BooleanField(_('Active'), default=True)
    
    class Meta:
        verbose_name = _('Search Suggestion')
        verbose_name_plural = _('Search Suggestions')
        ordering = ['-confidence_score']
        unique_together = ['original_query', 'suggested_query', 'suggestion_type']
    
    def __str__(self):
        return f'{self.original_query} → {self.suggested_query}'
    
    @property
    def click_rate(self):
        if self.times_shown > 0:
            return (self.times_clicked / self.times_shown) * 100
        return 0