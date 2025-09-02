#!/usr/bin/env python
"""
Development startup script for Trade India
"""

import os
import sys
import django
import subprocess
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tradeindia.settings')
django.setup()

def create_directories():
    """Create necessary directories"""
    dirs = ['static', 'media', 'logs', 'staticfiles']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    print("✅ Created necessary directories")

def setup_database():
    """Setup database and run migrations"""
    print("🗄️ Setting up database...")
    
    # Run migrations
    subprocess.run([sys.executable, 'manage.py', 'makemigrations'], check=True)
    subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
    
    print("✅ Database setup complete")

def create_superuser():
    """Create superuser if doesn't exist"""
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@tradeindia.com', 'admin123')
        print("✅ Created superuser: admin / admin123")
    else:
        print("ℹ️ Superuser already exists")

def populate_data():
    """Populate initial data"""
    print("📊 Populating initial data...")
    
    try:
        subprocess.run([sys.executable, 'manage.py', 'populate_locations'], check=True)
        print("✅ Populated location data")
    except subprocess.CalledProcessError:
        print("⚠️ Location data population failed (may already exist)")
    
    # Create basic categories manually
    from django.utils.text import slugify
    from listings.models import Category, Condition
    
    categories_data = [
        {'name': 'Electronics', 'icon': 'laptop'},
        {'name': 'Vehicles', 'icon': 'car'},
        {'name': 'Real Estate', 'icon': 'home'},
        {'name': 'Fashion', 'icon': 'tshirt'},
        {'name': 'Home & Garden', 'icon': 'couch'},
        {'name': 'Sports', 'icon': 'dumbbell'},
        {'name': 'Books', 'icon': 'book'},
        {'name': 'Jobs', 'icon': 'briefcase'},
    ]
    
    for cat_data in categories_data:
        cat, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'slug': slugify(cat_data['name']),
                'icon': cat_data['icon'],
                'is_active': True
            }
        )
        if created:
            print(f"✅ Created category: {cat.name}")
    
    # Create conditions
    conditions = ['Brand New', 'Like New', 'Good', 'Fair', 'Poor']
    for i, name in enumerate(conditions):
        cond, created = Condition.objects.get_or_create(
            name=name,
            defaults={'sort_order': i}
        )
        if created:
            print(f"✅ Created condition: {cond.name}")

def print_info():
    """Print application information"""
    print("\n" + "="*60)
    print("🎉 TRADE INDIA SETUP COMPLETE!")
    print("="*60)
    print("\n📱 Application Features:")
    print("   • Multi-category trading platform")
    print("   • Advanced search with location filters")
    print("   • AI-powered listing verification")
    print("   • Beautiful glassmorphism UI")
    print("   • Mobile-responsive design")
    print("   • REST API for integrations")
    print("   • Real-time notifications")
    print("   • User verification system")
    
    print("\n🌐 URLs:")
    print("   • Main Site: http://localhost:8000/")
    print("   • Admin Panel: http://localhost:8000/admin/")
    print("   • API Docs: http://localhost:8000/api/")
    
    print("\n🔑 Admin Credentials:")
    print("   • Username: admin")
    print("   • Password: admin123")
    
    print("\n🚀 To start the server:")
    print("   python manage.py runserver 0.0.0.0:8000")
    
    print("\n📊 Database Stats:")
    from locations.models import State, District, City
    from listings.models import Category, Condition
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    print(f"   • States: {State.objects.count()}")
    print(f"   • Districts: {District.objects.count()}")
    print(f"   • Cities: {City.objects.count()}")
    print(f"   • Categories: {Category.objects.count()}")
    print(f"   • Conditions: {Condition.objects.count()}")
    print(f"   • Users: {User.objects.count()}")
    
    print("\n🔧 Optional Setup:")
    print("   • Set OPENAI_API_KEY for AI verification")
    print("   • Configure Redis for caching")
    print("   • Set up PostgreSQL for production")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    print("🚀 Starting Trade India development setup...")
    
    try:
        create_directories()
        setup_database()
        create_superuser()
        populate_data()
        print_info()
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        sys.exit(1)