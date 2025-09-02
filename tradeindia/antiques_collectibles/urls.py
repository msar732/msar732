from django.urls import path
from django.views.generic import TemplateView

app_name = 'antiques_collectibles'

urlpatterns = [
    path('', TemplateView.as_view(template_name='antiques_collectibles/home.html'), name='home'),
]
