"""
Signal handlers for core app
"""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Category, State, District, City


@receiver(post_save, sender=Category)
def clear_category_cache(sender, instance, **kwargs):
    """Clear category-related caches when category is saved"""
    cache.delete('main_categories')
    cache.delete(f'category_{instance.slug}')
    cache.delete_pattern('category_listings_*')


@receiver(post_save, sender=State)
@receiver(post_save, sender=District)
@receiver(post_save, sender=City)
def clear_location_cache(sender, instance, **kwargs):
    """Clear location-related caches when location is saved"""
    cache.delete_pattern('locations_*')
    cache.delete_pattern('districts_*')
    cache.delete_pattern('cities_*')