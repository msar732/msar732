# Trade India - AI-Powered Marketplace

A comprehensive Django-based marketplace application with AI-powered features for buying and selling various items including motors, property, jobs, electronics, and more.

## Features

- **AI-Powered Verification**: Advanced AI system to verify listing authenticity
- **Multi-Category Support**: Motors, Property, Jobs, Electronics, Fashion, and more
- **Geospatial Features**: Location-based search and filtering
- **Real-time Notifications**: WebSocket-based real-time updates
- **Advanced Search**: AI-powered search suggestions and recommendations
- **User Management**: Custom user profiles with trust scores
- **Mobile Responsive**: Modern glassmorphism UI design

## Project Structure

```
tradeindia/
├── tradeindia/          # Main Django project
│   ├── settings.py      # Django settings
│   ├── urls.py          # Main URL configuration
│   ├── views.py         # Main views
│   ├── wsgi.py          # WSGI application
│   └── asgi.py          # ASGI application
├── accounts/            # User management
├── listings/            # Core listing functionality
├── motors/              # Motor vehicles marketplace
├── property/            # Real estate marketplace
├── jobs/                # Job listings
├── electronics/         # Electronics marketplace
├── fashion/             # Fashion & apparel
├── services/            # Service listings
├── auctions/            # Auction functionality
├── ai_verification/     # AI verification system
├── templates/           # HTML templates
├── static/              # Static files (CSS, JS, images)
└── media/               # User uploaded files
```

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database and other settings
```

4. Set up the database:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Environment Variables

Create a `.env` file in the project root with:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=tradeindia
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
EMAIL_HOST=smtp.gmail.com
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

## Key Apps

### Motors
- Car listings and sales
- Motorcycle marketplace
- Commercial vehicles
- Boats and marine vehicles
- Parts and accessories

### Property
- Residential properties
- Commercial real estate
- Rental properties
- Plots and land
- PG and hostel listings

### Jobs
- Job postings and applications
- Company profiles
- Job alerts and notifications
- Resume management

### Electronics
- Mobile phones and tablets
- Computers and laptops
- Home appliances
- Gaming equipment
- Accessories

## AI Features

- **Price Prediction**: ML models for fair price estimation
- **Listing Verification**: AI-powered authenticity checks
- **Recommendation Engine**: Personalized listing recommendations
- **Image Recognition**: Automatic product categorization
- **Fraud Detection**: Advanced fraud prevention algorithms

## Technology Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL with PostGIS
- **Cache**: Redis
- **Search**: Elasticsearch (optional)
- **AI/ML**: scikit-learn, TensorFlow
- **Frontend**: Tailwind CSS, Alpine.js
- **Real-time**: Django Channels, WebSockets
- **Image Processing**: Pillow, django-imagekit

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.