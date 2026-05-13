from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps

@receiver(post_migrate)
def create_default_site_settings(sender, **kwargs):
    if sender.name == 'pages':
        SiteSettings = apps.get_model('pages', 'SiteSettings')
        AboutPage = apps.get_model('pages', 'AboutPage')
        
        if not SiteSettings.objects.exists():
            SiteSettings.objects.create(
                company_name='Global Logistics Inc.',
                phone_number='+1 (555) 123-4567',
                email='info@logistics.com'
            )
        
        if not AboutPage.objects.exists():
            AboutPage.objects.create(
                title='About Us',
                content='Company overview...'
            )