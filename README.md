# Trade India - Django Marketplace

A comprehensive Django-based marketplace platform for buying and selling anything in India, featuring AI-powered verification and modern UI.

## Project Structure

```
tradeindia/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── tradeindia/              # Main project directory
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI configuration
│   ├── asgi.py              # ASGI configuration
│   ├── celery.py            # Celery configuration
│   ├── db_router.py         # Database routing
│   ├── accounts/            # User management app
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   └── urls.py
│   ├── listings/            # Core listings app
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   └── urls.py
│   ├── search/              # Search functionality
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── ai_verification/     # AI verification system
│   │   └── models.py
│   ├── api/                 # REST API
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── templates/           # HTML templates
│   │   ├── base.html
│   │   └── index.html
│   └── static/              # Static files
│       ├── css/
│       ├── js/
│       └── images/
└── other_apps/              # Additional category-specific apps
    ├── community/
    ├── electronics/
    ├── fashion/
    ├── jobs/
    ├── services/
    ├── auctions/
    ├── motors/
    ├── property/
    └── notifications/
```

## Features

- **User Management**: Custom user model with verification and trust scoring
- **Listings**: Comprehensive listing system with categories, images, and location
- **AI Verification**: Automated verification of listings using AI
- **Search**: Advanced search with suggestions and filters
- **REST API**: Full API support with Django REST Framework
- **Modern UI**: Glassmorphism design with Tailwind CSS
- **Real-time Features**: WebSocket support for live updates
- **Performance**: Redis caching and database optimization

## Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

## Environment Variables

Create a `.env` file with the following variables:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=tradeindia
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
EMAIL_HOST=smtp.gmail.com
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

## Key Components

### Models
- **CustomUser**: Extended user model with location and verification
- **Listing**: Core listing model with AI verification scores
- **Category**: Hierarchical category system
- **State/District**: Location management

### Views
- **Account Management**: Registration, login, profile management
- **Listing Management**: Create, view, search listings
- **API Views**: RESTful API endpoints

### Templates
- **Base Template**: Common layout with navigation and footer
- **Index Template**: Homepage with featured listings and categories

## API Endpoints

- `/api/listings/` - List and create listings
- `/api/categories/` - Get categories
- `/api/states/` - Get states
- `/api/districts/` - Get districts
- `/search/suggestions/` - Search suggestions

## Development

The project is structured for scalability and maintainability:

- **Modular Design**: Separate apps for different functionalities
- **Database Optimization**: Proper indexing and query optimization
- **Caching**: Redis-based caching for performance
- **Background Tasks**: Celery for async processing
- **Security**: CSRF protection, secure headers, and input validation

## Deployment

The project includes Docker configuration for easy deployment:

```bash
docker-compose up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.