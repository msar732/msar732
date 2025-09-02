from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView
from django.contrib import messages
from django.db.models import Count, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User, UserRating, UserFollowing
from .serializers import UserSerializer, UserRatingSerializer
from listings.models import Listing, Favorite


class UserViewSet(viewsets.ModelViewSet):
    """API ViewSet for User model"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.action == 'list':
            return User.objects.filter(is_active=True).select_related('state', 'district', 'city')
        return super().get_queryset()
    
    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        """Follow/unfollow a user"""
        user_to_follow = self.get_object()
        if user_to_follow == request.user:
            return Response({'error': 'Cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        following, created = UserFollowing.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )
        
        if not created:
            following.delete()
            return Response({'status': 'unfollowed'})
        
        return Response({'status': 'followed'})
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Rate a user"""
        user_to_rate = self.get_object()
        if user_to_rate == request.user:
            return Response({'error': 'Cannot rate yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserRatingSerializer(data=request.data)
        if serializer.is_valid():
            rating_obj, created = UserRating.objects.update_or_create(
                rater=request.user,
                rated_user=user_to_rate,
                defaults=serializer.validated_data
            )
            
            # Update user's average rating
            user_to_rate.update_rating(rating_obj.rating)
            
            return Response({'status': 'rating saved'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view"""
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context.update({
            'user': user,
            'total_listings': user.listings.count(),
            'active_listings': user.listings.filter(status='active').count(),
            'favorites_count': user.favorites.count(),
            'followers_count': user.followers.count(),
            'following_count': user.following.count(),
            'recent_listings': user.listings.filter(status='active').order_by('-created_at')[:5],
            'recent_ratings': user.received_ratings.order_by('-created_at')[:5],
        })
        
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Edit user profile"""
    model = User
    template_name = 'accounts/profile_edit.html'
    fields = [
        'first_name', 'last_name', 'phone_number', 'profile_picture', 'bio',
        'date_of_birth', 'state', 'district', 'city', 'address', 'pincode',
        'email_notifications', 'sms_notifications'
    ]
    
    def get_object(self):
        return self.request.user
    
    def get_success_url(self):
        messages.success(self.request, 'Profile updated successfully!')
        return '/accounts/profile/'


class DashboardView(LoginRequiredMixin, TemplateView):
    """User dashboard"""
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user statistics
        listings_stats = user.listings.aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(status='active')),
            sold=Count('id', filter=Q(status='sold')),
            draft=Count('id', filter=Q(status='draft')),
        )
        
        context.update({
            'listings_stats': listings_stats,
            'recent_listings': user.listings.order_by('-created_at')[:10],
            'recent_inquiries': user.listings.filter(
                inquiries__isnull=False
            ).prefetch_related('inquiries').order_by('-inquiries__created_at')[:10],
            'favorites_count': user.favorites.count(),
            'unread_inquiries': sum(
                listing.inquiries.filter(is_read=False).count() 
                for listing in user.listings.all()
            ),
        })
        
        return context


class FavoritesView(LoginRequiredMixin, TemplateView):
    """User favorites view"""
    template_name = 'accounts/favorites.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        favorites = Favorite.objects.filter(
            user=self.request.user
        ).select_related(
            'listing__seller', 'listing__category', 'listing__state', 'listing__district'
        ).prefetch_related('listing__images').order_by('-created_at')
        
        context['favorites'] = favorites
        return context


class MyListingsView(LoginRequiredMixin, TemplateView):
    """User's listings view"""
    template_name = 'accounts/my_listings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        listings = self.request.user.listings.select_related(
            'category', 'state', 'district'
        ).prefetch_related('images').order_by('-created_at')
        
        context['listings'] = listings
        return context


class VerificationView(LoginRequiredMixin, TemplateView):
    """User verification view"""
    template_name = 'accounts/verification.html'
    
    def post(self, request, *args, **kwargs):
        if 'verification_document' in request.FILES:
            user = request.user
            user.verification_document = request.FILES['verification_document']
            user.save()
            messages.success(request, 'Verification document uploaded successfully!')
        
        return redirect('accounts:verify')