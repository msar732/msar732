from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import CustomUser
from .forms import UserRegistrationForm

class RegisterView(CreateView):
    model = CustomUser
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = '/'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Account created successfully!')
        return response

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_listings'] = self.request.user.listings.all()[:10]
        return context