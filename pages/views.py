from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import AboutPage, Executive, Service, ContactMessage

def home(request):
    """Home page view"""
    return render(request, 'pages/home.html')

def about(request):
    """About page view"""
    try:
        about_page = AboutPage.objects.first()
    except:
        about_page = None
    
    # FIXED: Changed 'order' to 'display_order'
    executives = Executive.objects.all().order_by('display_order')
    services = Service.objects.all().order_by('display_order')
    
    context = {
        'about_page': about_page,
        'executives': executives,
        'services': services,
    }
    return render(request, 'pages/about.html', context)

def services(request):
    """Services page view"""
    # FIXED: Changed 'order' to 'display_order'
    services_list = Service.objects.all().order_by('display_order')
    context = {
        'services': services_list,
    }
    return render(request, 'pages/services.html', context)

def service_detail(request, service_id):
    """Service detail page view"""
    service = get_object_or_404(Service, id=service_id, is_active=True)
    context = {
        'service': service,
    }
    return render(request, 'pages/service_detail.html', context)

def contact(request):
    """Contact page view"""
    return render(request, 'pages/contact.html')

def contact_submit(request):
    """Handle contact form submission"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message_content = request.POST.get('message')
        
        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Save to database
        contact_message = ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message_content,
            ip_address=ip
        )
        
        # Send email notification (optional)
        try:
            send_mail(
                f'New Contact Message: {subject}',
                f'Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message_content}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Email error: {e}")  # Log error but continue
        
        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        return redirect('contact')
    
    return redirect('contact')