from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.JobHomeView.as_view(), name='home'),
    path('it-software/', views.ITJobsView.as_view(), name='it_software'),
    path('marketing/', views.MarketingJobsView.as_view(), name='marketing'),
    path('finance/', views.FinanceJobsView.as_view(), name='finance'),
    path('healthcare/', views.HealthcareJobsView.as_view(), name='healthcare'),
    path('engineering/', views.EngineeringJobsView.as_view(), name='engineering'),
    path('post/', views.PostJobView.as_view(), name='post'),
    path('detail/<int:job_id>/', views.JobDetailView.as_view(), name='detail'),
]