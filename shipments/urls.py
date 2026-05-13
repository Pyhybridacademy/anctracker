from django.urls import path
from . import views

urlpatterns = [
    path('track/', views.track_shipment, name='track_shipment'),
    path('track/<str:tracking_code>/', views.tracking_result, name='tracking_result'),
    path('payment/<str:tracking_code>/upload/', views.upload_payment_proof, name='upload_payment_proof'),
    path('payment/<int:payment_id>/success/', views.payment_success, name='payment_success'),
    path('payment/methods/', views.payment_methods_list, name='payment_methods'),
]