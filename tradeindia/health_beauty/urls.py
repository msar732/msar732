from django.urls import path
from django.views.generic import TemplateView

app_name = 'health_beauty'

urlpatterns = [
    path('', TemplateView.as_view(template_name='health_beauty/home.html'), name='home'),
]
