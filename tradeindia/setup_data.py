#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tradeindia.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils.text import slugify
from listings.models import Category, Condition
from locations.models import State

User = get_user_model()

def create_superuser():
    """Create superuser if it doesn't exist"""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@tradeindia.com', 'admin123')
        print("Created superuser: admin / admin123")
    else:
        print("Superuser already exists")

def create_basic_categories():
    """Create basic categories"""
    categories = [
        {'name': 'Electronics', 'icon': 'laptop'},
        {'name': 'Vehicles', 'icon': 'car'},
        {'name': 'Real Estate', 'icon': 'home'},
        {'name': 'Fashion', 'icon': 'tshirt'},
        {'name': 'Home & Garden', 'icon': 'couch'},
        {'name': 'Sports', 'icon': 'dumbbell'},
        {'name': 'Books', 'icon': 'book'},
        {'name': 'Jobs', 'icon': 'briefcase'},
    ]
    
    for cat_data in categories:
        cat, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'slug': slugify(cat_data['name']),
                'icon': cat_data['icon'],
                'is_active': True
            }
        )
        if created:
            print(f"Created category: {cat.name}")

def create_conditions():
    """Create item conditions"""
    conditions = [
        'Brand New',
        'Like New', 
        'Good',
        'Fair',
        'Poor'
    ]
    
    for i, name in enumerate(conditions):
        cond, created = Condition.objects.get_or_create(
            name=name,
            defaults={'sort_order': i}
        )
        if created:
            print(f"Created condition: {cond.name}")

if __name__ == '__main__':
    print("Setting up basic data...")
    create_superuser()
    create_basic_categories()
    create_conditions()
    print("Setup complete!")
    print(f"States: {State.objects.count()}")
    print(f"Categories: {Category.objects.count()}")
    print(f"Conditions: {Condition.objects.count()}")