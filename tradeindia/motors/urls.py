from django.urls import path
from . import views

app_name = 'motors'

urlpatterns = [
    path('', views.MotorHomeView.as_view(), name='home'),
    path('cars/', views.CarsView.as_view(), name='cars'),
    path('motorcycles/', views.MotorcyclesView.as_view(), name='motorcycles'),
    path('trucks/', views.TrucksView.as_view(), name='trucks'),
    path('boats/', views.BoatsView.as_view(), name='boats'),
    path('caravans/', views.CaravansView.as_view(), name='caravans'),
    path('parts/', views.PartsView.as_view(), name='parts'),
    path('create/', views.CreateMotorView.as_view(), name='create'),
    path('detail/<int:listing_id>/', views.MotorDetailView.as_view(), name='detail'),
]