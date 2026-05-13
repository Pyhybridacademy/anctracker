from django.contrib import admin
from django.utils.html import format_html
from .models import SiteSettings, AboutPage, Executive, Service, ContactMessage

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'email', 'phone_number']
    
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'last_updated']
    
    def has_add_permission(self, request):
        return not AboutPage.objects.exists()

@admin.register(Executive)
class ExecutiveAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'position', 'display_order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['full_name', 'position']
    list_editable = ['display_order', 'is_active']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'display_order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title']
    list_editable = ['display_order', 'is_active']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status_badge', 'created_at', 'admin_actions']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'ip_address', 'created_at']
    fieldsets = (
        ('Message Details', {
            'fields': ('name', 'email', 'phone', 'subject', 'message', 'ip_address', 'created_at')
        }),
        ('Admin Management', {
            'fields': ('status', 'admin_notes')
        }),
    )
    
    def status_badge(self, obj):
        status_colors = {
            'new': 'warning',
            'read': 'info',
            'replied': 'success',
            'archived': 'secondary',
        }
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            status_colors.get(obj.status, 'secondary'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def admin_actions(self, obj):
        return format_html(
            '<a href="mailto:{}?subject=Re: {}" class="btn btn-sm btn-outline-primary" target="_blank">Reply</a>',
            obj.email, obj.subject
        )
    admin_actions.short_description = 'Actions'
    
    def has_add_permission(self, request):
        return False