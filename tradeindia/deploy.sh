#!/bin/bash

# Trade India Deployment Script

echo "🚀 Starting Trade India deployment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📋 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p static media logs

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser (only if it doesn't exist)
echo "👤 Setting up admin user..."
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tradeindia.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@tradeindia.com', 'admin123')
    print('Created admin user: admin / admin123')
else:
    print('Admin user already exists')
"

# Populate location data
echo "🌍 Populating location data..."
python manage.py populate_locations

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Deployment complete!"
echo ""
echo "🌐 To start the server:"
echo "   python manage.py runserver 0.0.0.0:8000"
echo ""
echo "🔑 Admin credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo "   URL: http://localhost:8000/admin/"
echo ""
echo "📱 Application URL: http://localhost:8000/"