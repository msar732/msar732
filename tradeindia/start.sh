#!/bin/bash

echo "🚀 Starting Trade India Django Project Setup..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating environment file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your database credentials"
fi

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser if needed
echo "👤 Creating superuser..."
python manage.py createsuperuser --noinput --username admin --email admin@tradeindia.com || echo "Superuser already exists or skipped"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Setup complete! Run 'python manage.py runserver' to start the development server."
echo "🌐 Access the application at http://localhost:8000"
echo "🔧 Admin panel at http://localhost:8000/admin (username: admin)"