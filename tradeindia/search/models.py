from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class SearchLog(models.Model):
    """Model to track search queries for analytics"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    query = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    filters_applied = models.JSONField(default=dict, blank=True)
    results_count = models.PositiveIntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['query']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['created_at']),
            models.Index(fields=['ip_address']),
        ]

    def __str__(self):
        return f"Search: {self.query} ({self.results_count} results)"


class PopularSearch(models.Model):
    """Model for popular/trending searches"""
    query = models.CharField(max_length=200, unique=True)
    search_count = models.PositiveIntegerField(default=1)
    last_searched = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-search_count', '-last_searched']
        indexes = [
            models.Index(fields=['search_count']),
            models.Index(fields=['last_searched']),
        ]

    def __str__(self):
        return f"{self.query} ({self.search_count} searches)"


class SearchSuggestion(models.Model):
    """Model for search suggestions and autocomplete"""
    text = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=100, blank=True)
    popularity_score = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-popularity_score', 'text']
        indexes = [
            models.Index(fields=['text']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['popularity_score']),
        ]

    def __str__(self):
        return self.text