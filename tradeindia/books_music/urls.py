from django.urls import path
from django.views.generic import TemplateView

app_name = 'books_music'

urlpatterns = [
    path('', TemplateView.as_view(template_name='books_music/home.html'), name='home'),
]
