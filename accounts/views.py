from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import CustomUser, UserProfile
from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm
import json

@csrf_protect
@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            form = UserRegistrationForm(data)
        else:
            form = UserRegistrationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            
            if request.content_type == 'application/json':
                return JsonResponse({'success': True, 'redirect': '/'})
            return redirect('home')
        else:
            if request.content_type == 'application/json':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if request.content_type == 'application/json':
                return JsonResponse({'success': True, 'redirect': '/'})
            return redirect('home')
        else:
            error_msg = 'Invalid credentials'
            if request.content_type == 'application/json':
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
    
    return render(request, 'accounts/login.html')

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile})