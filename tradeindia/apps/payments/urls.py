"""
URL configuration for payments app
"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment methods
    path('methods/', views.PaymentMethodListView.as_view(), name='payment_methods'),
    path('methods/add/', views.AddPaymentMethodView.as_view(), name='add_payment_method'),
    path('methods/<int:pk>/delete/', views.delete_payment_method, name='delete_payment_method'),
    path('methods/<int:pk>/set-default/', views.set_default_payment_method, name='set_default_payment_method'),
    
    # Transactions
    path('transactions/', views.TransactionListView.as_view(), name='transactions'),
    path('transactions/<uuid:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('transactions/<uuid:pk>/invoice/', views.download_invoice, name='download_invoice'),
    
    # Payments
    path('pay/listing/<uuid:listing_id>/', views.PayForListingView.as_view(), name='pay_for_listing'),
    path('pay/featured/<uuid:listing_id>/', views.PayForFeaturedView.as_view(), name='pay_for_featured'),
    path('pay/subscription/<int:plan_id>/', views.PayForSubscriptionView.as_view(), name='pay_for_subscription'),
    
    # Wallet
    path('wallet/', views.WalletView.as_view(), name='wallet'),
    path('wallet/add-funds/', views.AddFundsView.as_view(), name='add_funds'),
    path('wallet/withdraw/', views.WithdrawFundsView.as_view(), name='withdraw_funds'),
    path('wallet/history/', views.WalletHistoryView.as_view(), name='wallet_history'),
    
    # Subscriptions
    path('subscriptions/', views.SubscriptionListView.as_view(), name='subscriptions'),
    path('subscriptions/plans/', views.SubscriptionPlansView.as_view(), name='subscription_plans'),
    path('subscriptions/<int:pk>/cancel/', views.cancel_subscription, name='cancel_subscription'),
    
    # Webhooks
    path('webhooks/razorpay/', views.razorpay_webhook, name='razorpay_webhook'),
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
    
    # Payment status
    path('success/', views.PaymentSuccessView.as_view(), name='payment_success'),
    path('failure/', views.PaymentFailureView.as_view(), name='payment_failure'),
]