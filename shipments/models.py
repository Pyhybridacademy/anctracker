import uuid
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
import os

def validate_file_size(value):
    """Validate file size"""
    filesize = value.size
    if filesize > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(f"Maximum file size is {settings.MAX_UPLOAD_SIZE/(1024*1024)}MB")

def validate_image_extension(value):
    """Validate image file extension"""
    ext = os.path.splitext(value.name)[1][1:].lower()
    if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(f"Allowed image extensions: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}")

def validate_document_extension(value):
    """Validate document file extension"""
    ext = os.path.splitext(value.name)[1][1:].lower()
    if ext not in settings.ALLOWED_DOCUMENT_EXTENSIONS:
        raise ValidationError(f"Allowed document extensions: {', '.join(settings.ALLOWED_DOCUMENT_EXTENSIONS)}")

class PaymentMethod(models.Model):
    """
    Payment methods available for customers
    """
    METHOD_TYPES = [
        ('crypto', 'Cryptocurrency'),
        ('bank', 'Bank Transfer'),
        ('card', 'Credit/Debit Card'),
        ('mobile_money', 'Mobile Money'),
        ('cash', 'Cash'),
    ]
    
    name = models.CharField(max_length=100)
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES)
    description = models.TextField(blank=True, help_text="Instructions for this payment method")
    
    # For cryptocurrency
    wallet_address = models.CharField(max_length=255, blank=True, help_text="BTC/USDT wallet address")
    crypto_network = models.CharField(max_length=50, blank=True, help_text="e.g., Bitcoin, ERC20, TRC20")
    
    # For bank transfers
    bank_name = models.CharField(max_length=200, blank=True)
    account_name = models.CharField(max_length=200, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    iban = models.CharField(max_length=50, blank=True)
    swift_code = models.CharField(max_length=20, blank=True)
    routing_number = models.CharField(max_length=50, blank=True)
    
    # For card payments (you'd integrate with payment gateway)
    api_key = models.CharField(max_length=255, blank=True)
    api_secret = models.CharField(max_length=255, blank=True)
    
    # QR code for easy payment
    qr_code = models.ImageField(
        upload_to='payment_qrcodes/', 
        blank=True, 
        null=True,
        validators=[validate_file_size, validate_image_extension]
    )
    
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
    
    def __str__(self):
        return f"{self.name} ({self.get_method_type_display()})"
    
    def get_payment_instructions(self):
        """Return formatted payment instructions based on method type"""
        if self.method_type == 'crypto':
            return {
                'wallet': self.wallet_address,
                'network': self.crypto_network
            }
        elif self.method_type == 'bank':
            return {
                'bank': self.bank_name,
                'account_name': self.account_name,
                'account_number': self.account_number,
                'iban': self.iban,
                'swift': self.swift_code,
                'routing': self.routing_number
            }
        return self.description

class Payment(models.Model):
    """
    Track payments made for shipments
    """
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('awaiting_proof', 'Awaiting Proof'),
        ('verified', 'Verified'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    CURRENCIES = [
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('GBP', 'GBP'),
        ('BTC', 'Bitcoin'),
        ('USDT', 'USDT'),
        ('ETH', 'Ethereum'),
    ]
    
    shipment = models.ForeignKey('Shipment', on_delete=models.CASCADE, related_name='payments')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, unique=True, blank=True)
    
    # Amount details
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, choices=CURRENCIES, default='USD')
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=1.0)
    amount_in_usd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Payer information
    payer_name = models.CharField(max_length=200, blank=True)
    payer_email = models.EmailField(blank=True)
    payer_phone = models.CharField(max_length=20, blank=True)
    
    # Proof of payment
    payment_proof = models.FileField(
        upload_to='payment_proofs/%Y/%m/%d/', 
        blank=True, 
        null=True,
        help_text="Upload receipt, screenshot, or transaction proof",
        validators=[validate_file_size, validate_document_extension]
    )
    proof_notes = models.TextField(blank=True, help_text="Additional notes about the proof")
    
    # Admin verification
    verified_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_payments'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True, help_text="Internal notes about this payment")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['shipment', 'status']),
        ]
    
    def __str__(self):
        return f"{self.transaction_id} - {self.amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        
        # Calculate USD amount if needed
        if self.currency != 'USD' and self.amount and self.exchange_rate:
            self.amount_in_usd = self.amount * self.exchange_rate
        elif self.currency == 'USD':
            self.amount_in_usd = self.amount
            
        if self.status == 'paid' and not self.payment_date:
            self.payment_date = timezone.now()
        super().save(*args, **kwargs)
    
    def generate_transaction_id(self):
        """Generate a unique transaction ID"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        unique_id = uuid.uuid4().hex[:8].upper()
        return f"PAY-{timestamp}-{unique_id}"
    
    def verify_payment(self, user):
        """Mark payment as verified"""
        self.status = 'verified'
        self.verified_by = user
        self.verified_at = timezone.now()
        self.save()
    
    def mark_as_paid(self, user):
        """Mark payment as paid"""
        self.status = 'paid'
        self.payment_date = timezone.now()
        self.verified_by = user
        self.verified_at = timezone.now()
        self.save()
        
        # Update shipment payment status
        shipment = self.shipment
        shipment.payment_status = 'paid'
        shipment.total_paid = shipment.payments.filter(status='paid').aggregate(
            total=models.Sum('amount_in_usd')
        )['total'] or 0
        shipment.save()

class Shipment(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('in_transit', 'In Transit'),
        ('at_sorting', 'At Sorting Facility'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('on_hold', 'On Hold'),
    ]
    
    SHIPMENT_TYPES = [
        ('express', 'Express Delivery'),
        ('standard', 'Standard Delivery'),
        ('economy', 'Economy Delivery'),
        ('freight', 'Freight'),
        ('air_cargo', 'Air Cargo'),
        ('sea_cargo', 'Sea Cargo'),
        ('cold_chain', 'Cold Chain'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Payment Pending'),
        ('partial', 'Partial Payment'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    tracking_code = models.CharField(max_length=20, unique=True, db_index=True)
    sender_name = models.CharField(max_length=200)
    receiver_name = models.CharField(max_length=200)
    sender_email = models.EmailField(blank=True)
    receiver_email = models.EmailField(blank=True)
    sender_phone = models.CharField(max_length=20, blank=True)
    receiver_phone = models.CharField(max_length=20, blank=True)
    origin = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    package_description = models.TextField()
    weight = models.DecimalField(max_digits=10, decimal_places=2, help_text='Weight in kg')
    current_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='registered')
    expected_delivery_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    # Enhanced fields
    shipment_type = models.CharField(max_length=50, choices=SHIPMENT_TYPES, default='standard')
    dimensions = models.CharField(max_length=100, blank=True, help_text='L x W x H in cm')
    declared_value = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text='Declared value in USD')
    insurance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text='Insurance amount in USD')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    taxes = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text='Taxes and duties')
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS, default='pending')
    delivery_proof = models.FileField(
        upload_to='delivery_proofs/', 
        blank=True, 
        null=True,
        validators=[validate_file_size, validate_document_extension]
    )
    signature_required = models.BooleanField(default=True)
    fragile = models.BooleanField(default=False)
    hazardous = models.BooleanField(default=False)
    temperature_range = models.CharField(max_length=50, blank=True, help_text='For cold chain shipments')
    barcode = models.ImageField(
        upload_to='barcodes/', 
        blank=True, 
        null=True,
        validators=[validate_file_size, validate_image_extension]
    )
    
    # NEW FIELDS FOR GOODS IMAGE AND PAYMENT TRACKING
    goods_image = models.ImageField(
        upload_to='shipment_goods/%Y/%m/%d/', 
        blank=True, 
        null=True,
        help_text="Picture of the goods being shipped",
        validators=[validate_file_size, validate_image_extension]
    )
    
    # Payment tracking (summary)
    total_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payment_due_date = models.DateField(null=True, blank=True)
    
    # Tracking URLs for different carriers
    tracking_url = models.URLField(blank=True, help_text="Custom tracking URL if different from internal")
    
    # Additional shipment flags
    requires_dangerous_goods_declaration = models.BooleanField(default=False)
    is_international = models.BooleanField(default=True)
    customs_info = models.TextField(blank=True, help_text="Customs declaration information")
    
    # Carrier information
    carrier_name = models.CharField(max_length=100, blank=True)
    carrier_service = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Shipment'
        verbose_name_plural = 'Shipments'
        indexes = [
            models.Index(fields=['tracking_code']),
            models.Index(fields=['current_status']),
            models.Index(fields=['expected_delivery_date']),
            models.Index(fields=['payment_status']),
        ]
    
    def __str__(self):
        return f"{self.tracking_code} - {self.sender_name} to {self.receiver_name}"
    
    @property
    def total_amount(self):
        """Calculate total amount from shipping_cost, insurance_amount, and taxes"""
        return self.shipping_cost + self.insurance_amount + self.taxes
    
    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = self.generate_tracking_code()
        
        # Update total paid from payments if this is not a new instance
        if self.pk:
            self.total_paid = self.payments.filter(status='paid').aggregate(
                total=models.Sum('amount_in_usd')
            )['total'] or 0
        
        super().save(*args, **kwargs)
    
    def generate_tracking_code(self):
        return f"{settings.TRACKING_CODE_PREFIX}{uuid.uuid4().hex[:8].upper()}"
    
    def get_status_display_class(self):
        status_classes = {
            'registered': 'bg-primary',
            'in_transit': 'bg-info',
            'at_sorting': 'bg-warning',
            'out_for_delivery': 'bg-primary',
            'delivered': 'bg-success',
            'on_hold': 'bg-danger',
        }
        return status_classes.get(self.current_status, 'bg-secondary')
    
    def get_shipment_type_icon(self):
        icons = {
            'express': 'fas fa-bolt',
            'standard': 'fas fa-truck',
            'economy': 'fas fa-shipping-fast',
            'freight': 'fas fa-truck-loading',
            'air_cargo': 'fas fa-plane',
            'sea_cargo': 'fas fa-ship',
            'cold_chain': 'fas fa-snowflake',
        }
        return icons.get(self.shipment_type, 'fas fa-box')
    
    def get_outstanding_balance(self):
        """Calculate remaining balance"""
        return self.total_amount - self.total_paid
    
    def get_payment_progress(self):
        """Get payment progress percentage"""
        total = self.total_amount
        if total == 0:
            return 100
        return min(100, int((self.total_paid / total) * 100))

class ShipmentStatus(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='status_updates')
    status = models.CharField(max_length=50, choices=Shipment.STATUS_CHOICES)
    location = models.CharField(max_length=200)
    note = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Optional geo-location
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Shipment Status Update'
        verbose_name_plural = 'Shipment Status Updates'
    
    def __str__(self):
        return f"{self.shipment.tracking_code} - {self.status} at {self.timestamp}"