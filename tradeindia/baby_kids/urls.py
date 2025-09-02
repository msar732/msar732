from django.urls import path
from django.views.generic import TemplateView

app_name = 'baby_kids'

urlpatterns = [
    path('', TemplateView.as_view(template_name='baby_kids/home.html'), name='home'),
]
