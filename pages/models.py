from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.urls import reverse

class SiteSettings(models.Model):
    company_name = models.CharField(max_length=200, default='Global Logistics Inc.')
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, default='+1 (555) 123-4567')
    email = models.EmailField(default='info@logistics.com')
    address = models.TextField(default='123 Logistics Street\nBusiness District\nNew York, NY 10001')
    footer_text = models.TextField(default='© 2024 Global Logistics Inc. All rights reserved.')
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return self.company_name
    
    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError('Only one SiteSettings instance allowed')
        return super().save(*args, **kwargs)

class AboutPage(models.Model):
    title = models.CharField(max_length=200, default='About Us')
    content = models.TextField(default='Global Logistics Inc. is a premier logistics and shipping company with over 15 years of experience in providing reliable transportation solutions worldwide. We specialize in freight forwarding, warehousing, and supply chain management.')
    mission = models.TextField(default='To provide efficient, reliable, and cost-effective logistics solutions that exceed customer expectations while maintaining the highest standards of service and integrity.')
    vision = models.TextField(default="To be the world's most trusted logistics partner, connecting businesses globally through innovative supply chain solutions.")
    history = models.TextField(default='Founded in 2008, Global Logistics started as a small freight forwarding company. Through strategic partnerships and continuous innovation, we have grown into a global logistics provider serving clients in over 50 countries.')
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'About Page'
        verbose_name_plural = 'About Page'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.pk and AboutPage.objects.exists():
            raise ValidationError('Only one AboutPage instance allowed')
        return super().save(*args, **kwargs)

class Executive(models.Model):
    full_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='executives/', blank=True, null=True)
    bio = models.TextField()
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['display_order']
        verbose_name = 'Executive'
        verbose_name_plural = 'Executives'
    
    def __str__(self):
        return f"{self.full_name} - {self.position}"

class Service(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon_class = models.CharField(max_length=50, default='fas fa-shipping-fast')
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['display_order']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
    
    def __str__(self):
        return self.title

class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'Archived'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    admin_notes = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
    
    def __str__(self):
        return f"{self.subject} - {self.name} ({self.created_at.date()})"