from django.urls import path
from . import views

app_name = 'electronics'

urlpatterns = [
    path('', views.ElectronicsHomeView.as_view(), name='home'),
    path('mobiles/', views.MobilePhonesView.as_view(), name='mobiles'),
    path('laptops/', views.LaptopsView.as_view(), name='laptops'),
    path('tablets/', views.TabletsView.as_view(), name='tablets'),
    path('cameras/', views.CamerasView.as_view(), name='cameras'),
    path('gaming/', views.GamingView.as_view(), name='gaming'),
    path('create/', views.CreateElectronicsView.as_view(), name='create'),
    path('detail/<int:listing_id>/', views.ElectronicsDetailView.as_view(), name='detail'),
]