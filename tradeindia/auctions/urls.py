from django.urls import path
from django.views.generic import TemplateView

app_name = 'auctions'

urlpatterns = [
    path('', TemplateView.as_view(template_name='auctions/home.html'), name='home'),
]