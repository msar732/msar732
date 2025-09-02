from django.urls import path
from . import views

app_name = 'property'

urlpatterns = [
    path('', views.PropertyHomeView.as_view(), name='home'),
    path('apartments/', views.ApartmentsView.as_view(), name='apartments'),
    path('houses/', views.HousesView.as_view(), name='houses'),
    path('plots/', views.PlotsView.as_view(), name='plots'),
    path('commercial/', views.CommercialView.as_view(), name='commercial'),
    path('create/', views.CreatePropertyView.as_view(), name='create'),
    path('detail/<int:listing_id>/', views.PropertyDetailView.as_view(), name='detail'),
]