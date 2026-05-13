from django.urls import path
from . import views

urlpatterns = [
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('services/<int:service_id>/', views.service_detail, name='service_detail'),  # ADD THIS LINE
    path('contact/', views.contact, name='contact'),
    path('contact/submit/', views.contact_submit, name='contact_submit'),
]