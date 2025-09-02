"""
URL configuration for AI verification app
"""
from django.urls import path
from . import views

app_name = 'ai_verification'

urlpatterns = [
    # AI verification endpoints
    path('verify/<uuid:listing_id>/', views.verify_listing, name='verify_listing'),
    path('status/<int:verification_id>/', views.verification_status, name='verification_status'),
    path('report/<int:verification_id>/', views.verification_report, name='verification_report'),
    
    # Admin views
    path('dashboard/', views.AIVerificationDashboard.as_view(), name='dashboard'),
    path('patterns/', views.FraudPatternListView.as_view(), name='fraud_patterns'),
    path('patterns/create/', views.FraudPatternCreateView.as_view(), name='create_pattern'),
]