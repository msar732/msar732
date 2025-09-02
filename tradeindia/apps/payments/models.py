"""
Payment models for TradeIndia
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator
from apps.core.models import TimestampedModel, UUIDModel
from apps.listings.models import Listing
import uuid


class PaymentMethod(TimestampedModel):
    """
    User payment methods
    """
    PAYMENT_TYPE_CHOICES = [
        ('card', _('Credit/Debit Card')),
        ('upi', _('UPI')),
        ('netbanking', _('Net Banking')),
        ('wallet', _('Digital Wallet')),
        ('bank_transfer', _('Bank Transfer')),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_methods'
    )
    payment_type = models.CharField(
        _('Payment type'),
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES
    )
    
    # Card details (encrypted)
    card_last_four = models.CharField(_('Card last four'), max_length=4, blank=True)
    card_brand = models.CharField(_('Card brand'), max_length=20, blank=True)
    card_holder_name = models.CharField(_('Card holder name'), max_length=100, blank=True)
    
    # UPI details
    upi_id = models.CharField(_('UPI ID'), max_length=100, blank=True)
    
    # Bank details
    bank_name = models.CharField(_('Bank name'), max_length=100, blank=True)
    account_number_masked = models.CharField(_('Account number (masked)'), max_length=20, blank=True)
    ifsc_code = models.CharField(_('IFSC code'), max_length=11, blank=True)
    
    # Wallet details
    wallet_provider = models.CharField(_('Wallet provider'), max_length=50, blank=True)
    wallet_number = models.CharField(_('Wallet number'), max_length=20, blank=True)
    
    # Common fields
    is_default = models.BooleanField(_('Default payment method'), default=False)
    is_verified = models.BooleanField(_('Verified'), default=False)
    is_active = models.BooleanField(_('Active'), default=True)
    
    # Provider tokens
    provider_customer_id = models.CharField(_('Provider customer ID'), max_length=100, blank=True)
    provider_payment_method_id = models.CharField(_('Provider payment method ID'), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('Payment Method')
        verbose_name_plural = _('Payment Methods')
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active', 'is_default']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.get_payment_type_display()}'
    
    def save(self, *args, **kwargs):
        # Ensure only one default payment method per user
        if self.is_default:
            PaymentMethod.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class Transaction(UUIDModel, TimestampedModel):
    """
    Payment transactions
    """
    TRANSACTION_TYPE_CHOICES = [
        ('listing_fee', _('Listing Fee')),
        ('featured_fee', _('Featured Listing Fee')),
        ('premium_subscription', _('Premium Subscription')),
        ('commission', _('Sales Commission')),
        ('purchase', _('Purchase')),
        ('refund', _('Refund')),
        ('withdrawal', _('Withdrawal')),
        ('deposit', _('Deposit')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
    ]
    
    # Users involved
    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='payments_made'
    )
    payee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='payments_received'
    )
    
    # Transaction details
    transaction_type = models.CharField(
        _('Transaction type'),
        max_length=30,
        choices=TRANSACTION_TYPE_CHOICES
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    
    # Amount details
    amount = models.DecimalField(
        _('Amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(_('Currency'), max_length=3, default='INR')
    
    # Fees and net amount
    platform_fee = models.DecimalField(
        _('Platform fee'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    payment_gateway_fee = models.DecimalField(
        _('Payment gateway fee'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    tax_amount = models.DecimalField(
        _('Tax amount'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    net_amount = models.DecimalField(
        _('Net amount'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    # Related objects
    listing = models.ForeignKey(
        Listing,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Payment gateway details
    gateway = models.CharField(
        _('Payment gateway'),
        max_length=20,
        choices=[
            ('razorpay', 'Razorpay'),
            ('stripe', 'Stripe'),
            ('paytm', 'Paytm'),
            ('phonepe', 'PhonePe'),
            ('googlepay', 'Google Pay'),
        ],
        blank=True
    )
    gateway_transaction_id = models.CharField(
        _('Gateway transaction ID'),
        max_length=100,
        blank=True,
        db_index=True
    )
    gateway_order_id = models.CharField(
        _('Gateway order ID'),
        max_length=100,
        blank=True
    )
    gateway_response = models.JSONField(_('Gateway response'), default=dict, blank=True)
    
    # Additional info
    description = models.TextField(_('Description'), blank=True)
    metadata = models.JSONField(_('Metadata'), default=dict, blank=True)
    
    # Timestamps
    initiated_at = models.DateTimeField(_('Initiated at'), auto_now_add=True)
    completed_at = models.DateTimeField(_('Completed at'), null=True, blank=True)
    failed_at = models.DateTimeField(_('Failed at'), null=True, blank=True)
    
    # Refund details
    is_refundable = models.BooleanField(_('Is refundable'), default=True)
    refund_deadline = models.DateTimeField(_('Refund deadline'), null=True, blank=True)
    refunded_amount = models.DecimalField(
        _('Refunded amount'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payer', 'status', '-created_at']),
            models.Index(fields=['payee', 'status', '-created_at']),
            models.Index(fields=['gateway_transaction_id']),
            models.Index(fields=['listing', 'status']),
        ]
    
    def __str__(self):
        return f'{self.get_transaction_type_display()} - {self.amount} {self.currency}'
    
    def calculate_net_amount(self):
        """Calculate net amount after fees and taxes"""
        self.net_amount = self.amount - self.platform_fee - self.payment_gateway_fee - self.tax_amount
        return self.net_amount


class Wallet(TimestampedModel):
    """
    User wallet for storing funds
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    balance = models.DecimalField(
        _('Balance'),
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    held_balance = models.DecimalField(
        _('Held balance'),
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_('Amount held for pending transactions')
    )
    currency = models.CharField(_('Currency'), max_length=3, default='INR')
    is_active = models.BooleanField(_('Active'), default=True)
    
    class Meta:
        verbose_name = _('Wallet')
        verbose_name_plural = _('Wallets')
    
    def __str__(self):
        return f'{self.user.username} - {self.balance} {self.currency}'
    
    @property
    def available_balance(self):
        """Get available balance (total - held)"""
        return self.balance - self.held_balance
    
    def can_withdraw(self, amount):
        """Check if user can withdraw the amount"""
        return self.available_balance >= amount


class WalletTransaction(UUIDModel, TimestampedModel):
    """
    Wallet transaction history
    """
    TRANSACTION_TYPE_CHOICES = [
        ('credit', _('Credit')),
        ('debit', _('Debit')),
        ('hold', _('Hold')),
        ('release', _('Release')),
    ]
    
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(
        _('Transaction type'),
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES
    )
    amount = models.DecimalField(
        _('Amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    balance_before = models.DecimalField(
        _('Balance before'),
        max_digits=12,
        decimal_places=2
    )
    balance_after = models.DecimalField(
        _('Balance after'),
        max_digits=12,
        decimal_places=2
    )
    description = models.CharField(_('Description'), max_length=255)
    related_transaction = models.ForeignKey(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='wallet_transactions'
    )
    metadata = models.JSONField(_('Metadata'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('Wallet Transaction')
        verbose_name_plural = _('Wallet Transactions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wallet', '-created_at']),
        ]
    
    def __str__(self):
        return f'{self.wallet.user.username} - {self.transaction_type} - {self.amount}'


class Subscription(TimestampedModel):
    """
    Premium subscriptions
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    plan = models.ForeignKey(
        'SubscriptionPlan',
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )
    
    # Status
    is_active = models.BooleanField(_('Active'), default=True)
    start_date = models.DateTimeField(_('Start date'))
    end_date = models.DateTimeField(_('End date'))
    
    # Billing
    amount = models.DecimalField(
        _('Amount'),
        max_digits=10,
        decimal_places=2
    )
    billing_cycle = models.CharField(
        _('Billing cycle'),
        max_length=20,
        choices=[
            ('monthly', _('Monthly')),
            ('quarterly', _('Quarterly')),
            ('yearly', _('Yearly')),
        ]
    )
    auto_renew = models.BooleanField(_('Auto renew'), default=True)
    
    # Payment details
    last_payment = models.ForeignKey(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subscription_payments'
    )
    next_billing_date = models.DateTimeField(_('Next billing date'), null=True, blank=True)
    
    # Cancellation
    cancelled_at = models.DateTimeField(_('Cancelled at'), null=True, blank=True)
    cancellation_reason = models.TextField(_('Cancellation reason'), blank=True)
    
    class Meta:
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active', 'end_date']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.plan.name}'


class SubscriptionPlan(TimestampedModel):
    """
    Available subscription plans
    """
    name = models.CharField(_('Plan name'), max_length=100, unique=True)
    slug = models.SlugField(_('Slug'), unique=True)
    description = models.TextField(_('Description'))
    
    # Pricing
    monthly_price = models.DecimalField(
        _('Monthly price'),
        max_digits=10,
        decimal_places=2
    )
    quarterly_price = models.DecimalField(
        _('Quarterly price'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    yearly_price = models.DecimalField(
        _('Yearly price'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Features
    features = models.JSONField(_('Features'), default=list)
    max_listings = models.IntegerField(_('Maximum listings'), default=100)
    max_featured_listings = models.IntegerField(_('Maximum featured listings'), default=5)
    commission_discount = models.DecimalField(
        _('Commission discount %'),
        max_digits=5,
        decimal_places=2,
        default=0
    )
    
    # Visibility
    is_active = models.BooleanField(_('Active'), default=True)
    is_featured = models.BooleanField(_('Featured'), default=False)
    order = models.IntegerField(_('Display order'), default=0)
    
    # Badge
    badge_text = models.CharField(_('Badge text'), max_length=20, blank=True)
    badge_color = models.CharField(_('Badge color'), max_length=7, blank=True)
    
    class Meta:
        verbose_name = _('Subscription Plan')
        verbose_name_plural = _('Subscription Plans')
        ordering = ['order', 'monthly_price']
    
    def __str__(self):
        return self.name


class Invoice(UUIDModel, TimestampedModel):
    """
    Invoices for transactions
    """
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name='invoice'
    )
    invoice_number = models.CharField(
        _('Invoice number'),
        max_length=50,
        unique=True,
        db_index=True
    )
    
    # Billing details
    billing_name = models.CharField(_('Billing name'), max_length=200)
    billing_email = models.EmailField(_('Billing email'))
    billing_phone = models.CharField(_('Billing phone'), max_length=20, blank=True)
    billing_address = models.TextField(_('Billing address'))
    billing_gst = models.CharField(_('GST number'), max_length=15, blank=True)
    
    # Invoice details
    subtotal = models.DecimalField(
        _('Subtotal'),
        max_digits=12,
        decimal_places=2
    )
    tax_rate = models.DecimalField(
        _('Tax rate %'),
        max_digits=5,
        decimal_places=2,
        default=18.0
    )
    tax_amount = models.DecimalField(
        _('Tax amount'),
        max_digits=10,
        decimal_places=2
    )
    total_amount = models.DecimalField(
        _('Total amount'),
        max_digits=12,
        decimal_places=2
    )
    
    # Status
    is_paid = models.BooleanField(_('Paid'), default=False)
    paid_at = models.DateTimeField(_('Paid at'), null=True, blank=True)
    
    # File
    pdf_file = models.FileField(
        _('PDF file'),
        upload_to='invoices/',
        blank=True
    )
    
    class Meta:
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.invoice_number
    
    def generate_invoice_number(self):
        """Generate unique invoice number"""
        from django.utils import timezone
        import random
        
        prefix = 'INV'
        year = timezone.now().year
        random_num = random.randint(10000, 99999)
        
        return f'{prefix}-{year}-{random_num}'
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)