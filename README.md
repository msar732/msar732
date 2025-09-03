# Trade India - Django Trading Platform

A comprehensive Django-based marketplace application for buying and selling items across India with AI-powered verification.

## Features

- **AI-Powered Verification**: Advanced machine learning models to verify listing authenticity
- **Multi-Image Upload**: Support for multiple images with automatic thumbnails
- **Location-Based Search**: Search by state and district across India
- **User Authentication**: Complete user registration and login system
- **Favorites System**: Save and manage favorite listings
- **Real-time Search**: Live search suggestions and filtering
- **Responsive Design**: Beautiful glassmorphism UI with Tailwind CSS
- **REST API**: Complete API for mobile apps and integrations
- **Admin Panel**: Comprehensive admin interface for management

## Technology Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL with PostGIS for location data
- **AI/ML**: TensorFlow, scikit-learn for verification
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Image Processing**: Pillow, django-imagekit
- **Background Tasks**: Celery with Redis
- **Deployment**: Docker, Gunicorn, Nginx

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd trade-india
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup PostgreSQL with PostGIS**
   ```bash
   # Install PostgreSQL and PostGIS
   sudo apt-get install postgresql postgresql-contrib postgis
   
   # Create database
   sudo -u postgres createdb tradeindia
   sudo -u postgres psql -c "CREATE EXTENSION postgis;" tradeindia
   ```

5. **Environment Configuration**
   Create a `.env` file:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DB_NAME=tradeindia
   DB_USER=postgres
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=5432
   ```

6. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Populate initial data**
   ```bash
   python manage.py populate_data
   ```

9. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
trade-india/
├── manage.py
├── requirements.txt
├── tradeindia/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
├── listings/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
├── search/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── ai_verification/
│   ├── models.py
│   ├── tasks.py
│   └── admin.py
├── notifications/
│   ├── models.py
│   └── admin.py
├── api/
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
└── templates/
    ├── base.html
    ├── index.html
    ├── accounts/
    ├── listings/
    └── search/
```

## API Endpoints

- `GET /api/listings/` - List all listings
- `GET /api/listings/featured/` - Get featured listings
- `GET /api/listings/verified/` - Get verified listings
- `GET /api/categories/` - List all categories
- `GET /api/states/` - List all states
- `GET /api/districts/` - List districts by state

## AI Verification System

The application includes an AI-powered verification system that analyzes:

- **Text Analysis**: Detects spam indicators and content quality
- **Image Analysis**: Verifies image authenticity and quality
- **Location Verification**: Ensures location consistency
- **Overall Score**: Combines all factors for a genuineness score

## Deployment

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Collect static files**
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

### Production Deployment

1. **Set environment variables**
   ```env
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

2. **Use production database**
   ```env
   DB_HOST=your-production-db-host
   DB_PASSWORD=your-production-db-password
   ```

3. **Configure static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.

---

**Trade India** - India's most trusted marketplace with AI-powered verification! 🚀