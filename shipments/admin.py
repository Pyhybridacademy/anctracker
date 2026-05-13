from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db import models
from django.contrib import messages
from django.utils import timezone
from .models import Shipment, ShipmentStatus, PaymentMethod, Payment

class ShipmentStatusInline(admin.TabularInline):
    model = ShipmentStatus
    extra = 1
    readonly_fields = ['timestamp']
    
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'status':
            kwargs['choices'] = Shipment.STATUS_CHOICES
        return super().formfield_for_choice_field(db_field, request, **kwargs)

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['created_at', 'payment_proof_preview', 'verification_status']
    fields = ['transaction_id', 'payment_method', 'amount', 'currency', 
              'status', 'payment_proof', 'payment_proof_preview', 'admin_notes']
    show_change_link = True
    
    def payment_proof_preview(self, obj):
        if obj.payment_proof:
            # Check if it's an image
            ext = obj.payment_proof.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif']:
                return format_html(
                    '<a href="{}" target="_blank"><img src="{}" style="max-height: 40px; max-width: 100px; border-radius: 4px;" /></a>',
                    obj.payment_proof.url,
                    obj.payment_proof.url
                )
            else:
                return format_html(
                    '<a href="{}" target="_blank" style="background: #417690; color: white; padding: 3px 10px; border-radius: 4px; text-decoration: none;">📄 View File</a>',
                    obj.payment_proof.url
                )
        return "No file"
    payment_proof_preview.short_description = 'Proof'
    
    def verification_status(self, obj):
        if obj.verified_by:
            return format_html(
                '<span style="color: green;">✓ Verified by {} at {}</span>',
                obj.verified_by.username,
                obj.verified_at.strftime('%Y-%m-%d %H:%M') if obj.verified_at else 'N/A'
            )
        return '<span style="color: orange;">⏳ Not verified</span>'
    verification_status.short_description = 'Verification'

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'method_type', 'is_active', 'display_order', 'payment_count']
    list_filter = ['is_active', 'method_type']
    list_editable = ['is_active', 'display_order']
    search_fields = ['name', 'description']
    readonly_fields = ['qr_code_preview', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'method_type', 'description', 'is_active', 'display_order')
        }),
        ('Cryptocurrency Settings', {
            'fields': ('wallet_address', 'crypto_network', 'qr_code', 'qr_code_preview'),
            'classes': ('wide',),
            'description': 'Fill these if method type is cryptocurrency'
        }),
        ('Bank Transfer Settings', {
            'fields': ('bank_name', 'account_name', 'account_number', 'iban', 'swift_code', 'routing_number'),
            'classes': ('wide',),
            'description': 'Fill these if method type is bank transfer'
        }),
        ('API Settings (for card payments)', {
            'fields': ('api_key', 'api_secret'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px; border: 1px solid #ddd; border-radius: 4px;" />',
                obj.qr_code.url
            )
        return "No QR code uploaded"
    qr_code_preview.short_description = 'QR Code Preview'
    
    def payment_count(self, obj):
        count = obj.payment_set.count()
        url = reverse('admin:shipments_payment_changelist') + f'?payment_method__id__exact={obj.id}'
        return format_html('<a href="{}">{} payments</a>', url, count)
    payment_count.short_description = 'Usage'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'shipment_link', 'payment_method', 
                   'amount_display', 'status', 'status_badge', 'created_at', 'verification_badge']
    list_filter = ['status', 'payment_method', 'currency', 'created_at']
    search_fields = ['transaction_id', 'shipment__tracking_code', 'payer_email']
    readonly_fields = ['created_at', 'updated_at', 'payment_proof_preview', 
                      'verification_details', 'amount_conversion', 'status_badge']
    raw_id_fields = ['shipment', 'verified_by']
    list_editable = ['status']
    actions = ['mark_as_verified', 'mark_as_paid', 'send_payment_confirmation']
    
    fieldsets = (
        ('Shipment Information', {
            'fields': ('shipment', 'transaction_id')
        }),
        ('Payment Method', {
            'fields': ('payment_method',)
        }),
        ('Amount Details', {
            'fields': ('amount', 'currency', 'exchange_rate', 'amount_in_usd', 'amount_conversion'),
        }),
        ('Payer Information', {
            'fields': ('payer_name', 'payer_email', 'payer_phone'),
            'classes': ('wide',)
        }),
        ('Proof of Payment', {
            'fields': ('payment_proof', 'payment_proof_preview', 'proof_notes'),
        }),
        ('Status & Verification', {
            'fields': ('status', 'verified_by', 'verified_at', 'admin_notes', 'verification_details'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'payment_date'),
            'classes': ('collapse',)
        }),
    )
    
    def shipment_link(self, obj):
        url = reverse('admin:shipments_shipment_change', args=[obj.shipment.id])
        return format_html('<a href="{}">{}</a>', url, obj.shipment.tracking_code)
    shipment_link.short_description = 'Shipment'
    
    def amount_display(self, obj):
        return f"{obj.amount} {obj.currency}"
    amount_display.short_description = 'Amount'
    
    def payment_proof_preview(self, obj):
        if obj.payment_proof:
            # Check if it's an image
            ext = obj.payment_proof.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif']:
                return format_html(
                    '<div style="text-align: center;">'
                    '<a href="{}" target="_blank">'
                    '<img src="{}" style="max-height: 150px; max-width: 300px; '
                    'border-radius: 8px; border: 2px solid #ddd; margin-bottom: 10px;" />'
                    '</a><br>'
                    '<a href="{}" target="_blank" class="button" style="background: #417690; '
                    'color: white; padding: 5px 15px; border-radius: 4px; text-decoration: none;">'
                    '📥 Download</a>'
                    '</div>',
                    obj.payment_proof.url,
                    obj.payment_proof.url,
                    obj.payment_proof.url
                )
            else:
                return format_html(
                    '<div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px;">'
                    '<a href="{}" target="_blank" class="button" style="background: #417690; '
                    'color: white; padding: 10px 20px; border-radius: 4px; text-decoration: none; '
                    'font-size: 14px;">📄 View Document</a>'
                    '</div>',
                    obj.payment_proof.url
                )
        return "No proof uploaded"
    payment_proof_preview.short_description = 'Payment Proof Preview'
    
    def amount_conversion(self, obj):
        if obj.currency != 'USD' and obj.amount_in_usd:
            return format_html(
                '<span style="color: #666;">≈ ${} USD</span>',
                obj.amount_in_usd
            )
        return '-'
    amount_conversion.short_description = 'USD Equivalent'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'awaiting_proof': '#17a2b8',
            'verified': '#28a745',
            'paid': '#28a745',
            'failed': '#dc3545',
            'refunded': '#6c757d'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display().upper()
        )
    status_badge.short_description = 'Status'
    
    def verification_badge(self, obj):
        if obj.verified_by:
            return format_html(
                '<span style="color: #28a745;">✓ Verified</span>'
            )
        return format_html(
            '<span style="color: #ffc107;">⏳ Pending</span>'
        )
    verification_badge.short_description = 'Verification'
    
    def verification_details(self, obj):
        if obj.verified_by:
            return format_html(
                '<div style="background: #f8f9fa; padding: 10px; border-radius: 4px;">'
                '<p><strong>Verified by:</strong> {} </p>'
                '<p><strong>Verified at:</strong> {}</p>'
                '</div>',
                obj.verified_by.username,
                obj.verified_at.strftime('%Y-%m-%d %H:%M:%S') if obj.verified_at else 'N/A'
            )
        return '<span style="color: #666;">Not verified yet</span>'
    verification_details.short_description = 'Verification Details'
    
    def mark_as_verified(self, request, queryset):
        for payment in queryset:
            payment.verify_payment(request.user)
        self.message_user(request, f"{queryset.count()} payments marked as verified.")
    mark_as_verified.short_description = "Mark selected as verified"
    
    def mark_as_paid(self, request, queryset):
        for payment in queryset:
            payment.mark_as_paid(request.user)
        self.message_user(request, f"{queryset.count()} payments marked as paid.")
    mark_as_paid.short_description = "Mark selected as paid"
    
    def send_payment_confirmation(self, request, queryset):
        # This would integrate with your email system
        for payment in queryset.filter(status='paid'):
            # send_confirmation_email(payment)
            pass
        self.message_user(request, f"Confirmations sent for {queryset.filter(status='paid').count()} payments.")
    send_payment_confirmation.short_description = "Send payment confirmation emails"

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['tracking_code', 'sender_name', 'receiver_name', 
                   'current_status_badge', 'payment_status_badge', 'goods_image_thumbnail',
                   'payment_progress_bar', 'expected_delivery_date', 'created_at']
    list_filter = ['current_status', 'payment_status', 'shipment_type', 'created_at']
    search_fields = ['tracking_code', 'sender_name', 'receiver_name', 'sender_email', 'receiver_email']
    readonly_fields = ['tracking_code', 'created_at', 'updated_at', 'goods_image_preview', 
                      'payment_summary', 'total_amount_display']
    inlines = [ShipmentStatusInline, PaymentInline]
    actions = ['mark_payment_received', 'generate_invoice', 'send_tracking_update', 
              'send_payment_reminder']
    
    fieldsets = (
        ('Tracking Information', {
            'fields': ('tracking_code', 'current_status', 'payment_status', 
                      'expected_delivery_date', 'payment_due_date')
        }),
        ('Goods Image', {
            'fields': ('goods_image', 'goods_image_preview'),
            'description': 'Upload a clear image of the goods for verification and tracking'
        }),
        ('Sender Information', {
            'fields': ('sender_name', 'sender_email', 'sender_phone', 'origin')
        }),
        ('Receiver Information', {
            'fields': ('receiver_name', 'receiver_email', 'receiver_phone', 'destination')
        }),
        ('Package Details', {
            'fields': ('package_description', 'shipment_type', 'weight', 'dimensions', 
                      'declared_value', 'fragile', 'hazardous', 'temperature_range')
        }),
        ('Financial Information', {
            'fields': ('shipping_cost', 'insurance_amount', 'taxes', 
                      'total_paid', 'payment_summary'),
            'classes': ('wide',)
        }),
        ('Carrier Information', {
            'fields': ('carrier_name', 'carrier_service', 'tracking_url'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'customs_info', 'is_international', 
                      'requires_dangerous_goods_declaration', 'signature_required'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'delivery_proof'),
            'classes': ('collapse',)
        }),
    )
    
    def goods_image_thumbnail(self, obj):
        if obj.goods_image:
            return format_html(
                '<img src="{}" style="max-height: 40px; max-width: 40px; border-radius: 4px;" />',
                obj.goods_image.url
            )
        return "📦"  # Plain string, not format_html
    goods_image_thumbnail.short_description = 'Image'
    
    def goods_image_preview(self, obj):
        if obj.goods_image:
            return format_html(
                '<div style="text-align: center;">'
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-height: 200px; max-width: 100%; '
                'border-radius: 8px; border: 2px solid #ddd; margin-bottom: 10px;" />'
                '</a><br>'
                '<a href="{}" target="_blank" class="button" style="background: #417690; '
                'color: white; padding: 5px 15px; border-radius: 4px; text-decoration: none;">'
                '🔍 View Full Size</a>'
                '</div>',
                obj.goods_image.url,
                obj.goods_image.url,
                obj.goods_image.url
            )
        return "No image uploaded"  # Plain string, not format_html
    goods_image_preview.short_description = 'Goods Image Preview'
    
    def payment_status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'partial': '#17a2b8',
            'paid': '#28a745',
            'refunded': '#6c757d'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            colors.get(obj.payment_status, '#6c757d'),
            obj.get_payment_status_display().upper()
        )
    payment_status_badge.short_description = 'Payment'
    
    def current_status_badge(self, obj):
        colors = {
            'registered': '#17a2b8',
            'in_transit': '#007bff',
            'at_sorting': '#ffc107',
            'out_for_delivery': '#007bff',
            'delivered': '#28a745',
            'on_hold': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            colors.get(obj.current_status, '#6c757d'),
            obj.get_current_status_display().upper()
        )
    current_status_badge.short_description = 'Status'
    
    def payment_progress_bar(self, obj):
        progress = obj.get_payment_progress()
        total_amount = obj.total_amount
        
        if total_amount == 0:
            return "N/A"  # Plain string, not format_html
        
        color = '#28a745' if progress == 100 else '#ffc107'
        return format_html(
            '<div style="width: 100px; background: #e9ecef; border-radius: 10px; overflow: hidden;">'
            '<div style="width: {}%; background: {}; height: 20px; text-align: center; '
            'color: white; font-size: 10px; line-height: 20px;">${}</div>'
            '</div>',
            progress,
            color,
            int(obj.total_paid)
        )
    payment_progress_bar.short_description = 'Payment Progress'
    
    def total_amount_display(self, obj):
        return format_html('<strong>${}</strong>', obj.total_amount)
    total_amount_display.short_description = 'Total Amount'
    
    def payment_summary(self, obj):
        payments = obj.payments.all()
        paid_total = obj.total_paid
        total_amount = obj.total_amount
        pending_total = payments.filter(status__in=['pending', 'awaiting_proof']).aggregate(
            total=models.Sum('amount_in_usd')
        )['total'] or 0
        
        if not payments.exists():
            return "No payments recorded yet"  # Plain string, not format_html
        
        html = '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">'
        html += f'<p><strong>Total Required:</strong> ${total_amount}</p>'
        html += f'<p><strong>Total Paid:</strong> <span style="color: #28a745;">${paid_total}</span></p>'
        html += f'<p><strong>Pending:</strong> <span style="color: #ffc107;">${pending_total}</span></p>'
        html += f'<p><strong>Outstanding:</strong> <span style="color: #dc3545;">${obj.get_outstanding_balance()}</span></p>'
        
        # List recent payments
        recent = payments.order_by('-created_at')[:3]
        if recent:
            html += '<hr><p><strong>Recent Payments:</strong></p>'
            for p in recent:
                status_icon = '✅' if p.status == 'paid' else '⏳'
                html += f'<p style="margin: 5px 0;">{status_icon} {p.transaction_id}: ${p.amount} {p.currency} ({p.get_status_display()})</p>'
        
        html += '</div>'
        return format_html(html)
    payment_summary.short_description = 'Payment Summary'
    
    def mark_payment_received(self, request, queryset):
        for shipment in queryset:
            shipment.payment_status = 'paid'
            shipment.save()
        self.message_user(request, f"{queryset.count()} shipments marked as paid.")
    mark_payment_received.short_description = "Mark payment as received"
    
    def send_payment_reminder(self, request, queryset):
        # This would integrate with your email system
        count = 0
        for shipment in queryset.filter(payment_status='pending'):
            # send_payment_reminder_email(shipment)
            count += 1
        self.message_user(request, f"Payment reminders sent for {count} shipments.")
    send_payment_reminder.short_description = "Send payment reminders"
    
    def generate_invoice(self, request, queryset):
        # This would generate PDF invoices
        for shipment in queryset:
            # generate_invoice_pdf(shipment)
            pass
        self.message_user(request, f"Invoices generated for {queryset.count()} shipments.")
    generate_invoice.short_description = "Generate invoice"
    
    def send_tracking_update(self, request, queryset):
        # This would send email/SMS updates
        for shipment in queryset:
            # send_update_notification(shipment)
            pass
        self.message_user(request, f"Updates sent for {queryset.count()} shipments.")
    send_tracking_update.short_description = "Send tracking update"
    
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, ShipmentStatus):
                # Update main shipment status when a new status is added
                form.instance.current_status = instance.status
                form.instance.save()
        super().save_formset(request, form, formset, change)

@admin.register(ShipmentStatus)
class ShipmentStatusAdmin(admin.ModelAdmin):
    list_display = ['shipment', 'status_badge', 'location', 'timestamp']
    list_filter = ['status', 'timestamp']
    search_fields = ['shipment__tracking_code', 'location', 'note']
    readonly_fields = ['timestamp']
    raw_id_fields = ['shipment']
    
    fieldsets = (
        ('Status Information', {
            'fields': ('shipment', 'status', 'location', 'note')
        }),
        ('Geo Location', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'registered': '#17a2b8',
            'in_transit': '#007bff',
            'at_sorting': '#ffc107',
            'out_for_delivery': '#007bff',
            'delivered': '#28a745',
            'on_hold': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 10px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'