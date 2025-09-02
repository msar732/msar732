# Accounts Views
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import CustomUser, UserProfile
import json

@csrf_protect
@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        phone_number = request.POST.get('phone_number')
        state = request.POST.get('state')
        district = request.POST.get('district')
        
        if password1 == password2:
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            elif CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
            else:
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    phone_number=phone_number,
                    state=state,
                    district=district
                )
                UserProfile.objects.create(user=user)
                login(request, user)
                return redirect('home')
        else:
            messages.error(request, 'Passwords do not match')
    
    return render(request, 'accounts/register.html')

@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'accounts/login.html')

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile})