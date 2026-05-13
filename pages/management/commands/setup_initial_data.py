from django.core.management.base import BaseCommand
from pages.models import SiteSettings, AboutPage, Executive, Service, ContactMessage
from shipments.models import Shipment, ShipmentStatus
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Sets up initial data for the logistics application'

    def handle(self, *args, **kwargs):
        # Create Site Settings
        if not SiteSettings.objects.exists():
            SiteSettings.objects.create(
                company_name='Global Logistics Inc.',
                phone_number='+1 (555) 123-4567',
                email='info@globallogistics.com',
                address='123 Logistics Street\nBusiness District\nNew York, NY 10001',
                footer_text='© 2024 Global Logistics Inc. All rights reserved.',
                facebook_url='https://facebook.com/globallogistics',
                twitter_url='https://twitter.com/globallogistics',
                linkedin_url='https://linkedin.com/company/globallogistics',
                instagram_url='https://instagram.com/globallogistics'
            )
            self.stdout.write(self.style.SUCCESS('✅ Created Site Settings'))

        # Create About Page
        if not AboutPage.objects.exists():
            AboutPage.objects.create(
                title='About Global Logistics Inc.',
                content='Global Logistics Inc. is a premier logistics and shipping company with over 15 years of experience in providing reliable transportation solutions worldwide. We specialize in freight forwarding, warehousing, and supply chain management.',
                mission='To provide efficient, reliable, and cost-effective logistics solutions that exceed customer expectations while maintaining the highest standards of service and integrity.',
                vision="To be the world's most trusted logistics partner, connecting businesses globally through innovative supply chain solutions.",
                history='Founded in 2008, Global Logistics started as a small freight forwarding company. Through strategic partnerships and continuous innovation, we have grown into a global logistics provider serving clients in over 50 countries.'
            )
            self.stdout.write(self.style.SUCCESS('✅ Created About Page'))

        # Create Sample Services
        if not Service.objects.exists():
            services = [
                {
                    'title': 'Air Freight Solutions',
                    'description': 'Time-sensitive air cargo solutions with global coverage, customs clearance, and temperature-controlled options for perishable goods.',
                    'icon_class': 'fas fa-plane-departure',
                    'display_order': 1
                },
                {
                    'title': 'Ocean Freight Services',
                    'description': 'Cost-effective sea freight solutions for bulk and container shipments worldwide, including FCL, LCL, and dangerous goods handling.',
                    'icon_class': 'fas fa-ship',
                    'display_order': 2
                },
                {
                    'title': 'Road Transport Network',
                    'description': 'Domestic and cross-border road transport with temperature-controlled options, GPS tracking, and express delivery services.',
                    'icon_class': 'fas fa-truck',
                    'display_order': 3
                },
                {
                    'title': 'Warehousing & Distribution',
                    'description': 'Modern warehouse facilities with inventory management, order fulfillment, cross-docking, and value-added services.',
                    'icon_class': 'fas fa-warehouse',
                    'display_order': 4
                },
                {
                    'title': 'Supply Chain Management',
                    'description': 'End-to-end supply chain solutions including procurement, inventory optimization, and distribution management.',
                    'icon_class': 'fas fa-boxes',
                    'display_order': 5
                },
                {
                    'title': 'Cold Chain Logistics',
                    'description': 'Temperature-controlled logistics for pharmaceuticals, food, and chemicals with real-time temperature monitoring.',
                    'icon_class': 'fas fa-temperature-low',
                    'display_order': 6
                },
            ]
            
            for service_data in services:
                Service.objects.create(**service_data)
            self.stdout.write(self.style.SUCCESS('✅ Created Sample Services'))

        # Create Sample Executives
        if not Executive.objects.exists():
            executives = [
                {
                    'full_name': 'John Anderson',
                    'position': 'Chief Executive Officer',
                    'bio': 'With over 20 years in logistics, John has transformed Global Logistics into an industry leader.',
                    'display_order': 1
                },
                {
                    'full_name': 'Sarah Chen',
                    'position': 'Chief Operations Officer',
                    'bio': 'Sarah oversees global operations with expertise in supply chain optimization and process improvement.',
                    'display_order': 2
                },
                {
                    'full_name': 'Michael Rodriguez',
                    'position': 'Chief Technology Officer',
                    'bio': 'Michael leads our digital transformation initiatives and technology innovation strategies.',
                    'display_order': 3
                },
            ]
            
            for executive_data in executives:
                Executive.objects.create(**executive_data)
            self.stdout.write(self.style.SUCCESS('✅ Created Sample Executives'))

        # Create Sample Shipments
        if not Shipment.objects.exists():
            sample_shipments = [
                {
                    'tracking_code': 'TRK12345678',
                    'sender_name': 'John Smith',
                    'receiver_name': 'Sarah Johnson',
                    'origin': 'New York, USA',
                    'destination': 'London, UK',
                    'package_description': 'Electronics - 2 laptops and accessories',
                    'weight': 5.5,
                    'current_status': 'delivered',
                    'expected_delivery_date': timezone.now().date() - timedelta(days=2),
                    'shipment_type': 'express',
                    'dimensions': '45x30x15 cm',
                    'declared_value': 2500.00,
                    'insurance_amount': 2500.00,
                    'shipping_cost': 125.50,
                    'payment_status': 'paid',
                    'signature_required': True,
                    'fragile': True
                },
                {
                    'tracking_code': 'TRK87654321',
                    'sender_name': 'TechCorp Inc.',
                    'receiver_name': 'Global Solutions Ltd.',
                    'origin': 'Tokyo, Japan',
                    'destination': 'Sydney, Australia',
                    'package_description': 'Industrial equipment parts',
                    'weight': 125.0,
                    'current_status': 'in_transit',
                    'expected_delivery_date': timezone.now().date() + timedelta(days=5),
                    'shipment_type': 'air_cargo',
                    'dimensions': '120x80x60 cm',
                    'declared_value': 15000.00,
                    'insurance_amount': 15000.00,
                    'shipping_cost': 850.00,
                    'payment_status': 'partial',
                    'signature_required': True
                },
                {
                    'tracking_code': 'TRK24681357',
                    'sender_name': 'Maria Garcia',
                    'receiver_name': 'Robert Chen',
                    'origin': 'Madrid, Spain',
                    'destination': 'Beijing, China',
                    'package_description': 'Art collection - fragile items',
                    'weight': 15.0,
                    'current_status': 'at_sorting',
                    'expected_delivery_date': timezone.now().date() + timedelta(days=7),
                    'shipment_type': 'cold_chain',
                    'dimensions': '80x60x40 cm',
                    'declared_value': 7500.00,
                    'insurance_amount': 7500.00,
                    'shipping_cost': 320.75,
                    'payment_status': 'pending',
                    'signature_required': True,
                    'fragile': True,
                    'temperature_range': '2-8°C'
                },
            ]
            
            for shipment_data in sample_shipments:
                shipment = Shipment.objects.create(**shipment_data)
                
                # Create status history
                statuses = [
                    ('registered', 'New York Facility', 'Shipment registered and received'),
                    ('in_transit', 'In Transit', 'Departed from origin facility'),
                ]
                
                if shipment.current_status == 'delivered':
                    statuses.append(('delivered', 'London Facility', 'Successfully delivered to recipient'))
                elif shipment.current_status == 'in_transit':
                    statuses.append(('in_transit', 'Pacific Ocean', 'Currently in transit'))
                elif shipment.current_status == 'at_sorting':
                    statuses.append(('at_sorting', 'Madrid Sorting Center', 'Package being sorted'))
                
                for i, (status, location, note) in enumerate(statuses):
                    ShipmentStatus.objects.create(
                        shipment=shipment,
                        status=status,
                        location=location,
                        note=note,
                        timestamp=timezone.now() - timedelta(days=len(statuses)-i)
                    )
            
            self.stdout.write(self.style.SUCCESS('✅ Created Sample Shipments'))

        # Create sample contact message
        if not ContactMessage.objects.exists():
            ContactMessage.objects.create(
                name='David Wilson',
                email='david@example.com',
                phone='+1 (555) 987-6543',
                subject='Request for Logistics Quote',
                message='Hello, I would like to get a quote for shipping industrial equipment from USA to Germany.',
                status='read',
                admin_notes='Customer is interested in freight services. Follow up with quote.'
            )
            self.stdout.write(self.style.SUCCESS('✅ Created Sample Contact Message'))

        self.stdout.write(self.style.SUCCESS('\n✨ Initial setup completed successfully!'))
        self.stdout.write(self.style.SUCCESS('\nAdmin Login Credentials:'))
        self.stdout.write(self.style.SUCCESS('Run: python manage.py createsuperuser'))
        self.stdout.write(self.style.SUCCESS('\nSample Tracking Codes:'))
        self.stdout.write(self.style.SUCCESS('• TRK12345678 (Delivered)'))
        self.stdout.write(self.style.SUCCESS('• TRK87654321 (In Transit)'))
        self.stdout.write(self.style.SUCCESS('• TRK24681357 (At Sorting)'))