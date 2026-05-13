from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from .models import Shipment, Payment, PaymentMethod
from django.db.models import Sum
import uuid

def track_shipment(request):
    tracking_code = request.GET.get('tracking_code', '').strip()
    
    if tracking_code:
        try:
            shipment = Shipment.objects.get(tracking_code=tracking_code)
            return redirect('tracking_result', tracking_code=tracking_code)
        except Shipment.DoesNotExist:
            messages.error(request, f'No shipment found with tracking code: {tracking_code}')
    
    return render(request, 'shipments/track.html')

def tracking_result(request, tracking_code):
    shipment = get_object_or_404(Shipment, tracking_code=tracking_code)
    status_updates = shipment.status_updates.all().order_by('-timestamp')
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    # Get payment information
    payments = shipment.payments.all().order_by('-created_at')
    paid_payments = payments.filter(status='paid')
    
    # Calculate total amount from shipment fields
    total_amount = shipment.shipping_cost + shipment.insurance_amount + (shipment.taxes if hasattr(shipment, 'taxes') else 0)
    
    # Calculate payment totals
    total_paid = paid_payments.aggregate(total=Sum('amount_in_usd'))['total'] or 0
    outstanding = total_amount - total_paid
    progress = int((total_paid / total_amount * 100)) if total_amount > 0 else 0
    
    context = {
        'shipment': shipment,
        'status_updates': status_updates,
        'payment_methods': payment_methods,
        'payments': payments,
        'total_amount': total_amount,
        'total_paid': total_paid,
        'outstanding': outstanding,
        'payment_progress': progress,
    }
    return render(request, 'shipments/tracking_result.html', context)

def upload_payment_proof(request, tracking_code):
    """Upload payment proof for a shipment"""
    shipment = get_object_or_404(Shipment, tracking_code=tracking_code)
    
    if request.method == 'POST':
        payment_method_id = request.POST.get('payment_method')
        amount = request.POST.get('amount')
        currency = request.POST.get('currency', 'USD')
        payer_name = request.POST.get('payer_name', shipment.sender_name)
        payer_email = request.POST.get('payer_email', shipment.sender_email)
        payer_phone = request.POST.get('payer_phone', shipment.sender_phone)
        payment_proof = request.FILES.get('payment_proof')
        proof_notes = request.POST.get('proof_notes', '')
        
        # Validate required fields
        if not all([payment_method_id, amount, payment_proof]):
            messages.error(request, 'Please fill in all required fields and upload proof.')
            return redirect('upload_payment_proof', tracking_code=tracking_code)
        
        try:
            payment_method = PaymentMethod.objects.get(id=payment_method_id, is_active=True)
        except PaymentMethod.DoesNotExist:
            messages.error(request, 'Invalid payment method selected.')
            return redirect('upload_payment_proof', tracking_code=tracking_code)
        
        # Create payment record
        payment = Payment.objects.create(
            shipment=shipment,
            payment_method=payment_method,
            amount=amount,
            currency=currency,
            payer_name=payer_name,
            payer_email=payer_email,
            payer_phone=payer_phone,
            payment_proof=payment_proof,
            proof_notes=proof_notes,
            status='awaiting_proof'
        )
        
        # Update shipment payment status if it was pending
        if shipment.payment_status == 'pending':
            shipment.payment_status = 'partial'
            shipment.save()
        
        messages.success(request, 'Payment proof uploaded successfully! Our team will verify it shortly.')
        return redirect('payment_success', payment_id=payment.id)
    
    # GET request - show upload form
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    # Calculate total amount
    total_amount = shipment.shipping_cost + shipment.insurance_amount + (shipment.taxes if hasattr(shipment, 'taxes') else 0)
    
    # Calculate outstanding balance
    paid_total = shipment.payments.filter(status='paid').aggregate(total=Sum('amount_in_usd'))['total'] or 0
    outstanding = total_amount - paid_total
    
    context = {
        'shipment': shipment,
        'payment_methods': payment_methods,
        'outstanding': outstanding,
        'paid_total': paid_total,
        'total_amount': total_amount,
    }
    return render(request, 'shipments/upload_payment.html', context)

def payment_success(request, payment_id):
    """Show payment success page"""
    payment = get_object_or_404(Payment, id=payment_id)
    return render(request, 'shipments/payment_success.html', {'payment': payment})

def payment_methods_list(request):
    """Display all active payment methods"""
    methods = PaymentMethod.objects.filter(is_active=True).order_by('display_order')
    return render(request, 'shipments/payment_methods.html', {'methods': methods})