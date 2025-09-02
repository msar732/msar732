from django.urls import path
from django.views.generic import TemplateView

app_name = 'fashion'

urlpatterns = [
    path('', TemplateView.as_view(template_name='fashion/home.html'), name='home'),
]