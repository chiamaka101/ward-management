
from django.contrib import admin
from django.utils.html import format_html
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'illness', 'bill_balance', 'bill_status', 'admitted_on']
    list_filter = ['admitted_on', 'illness']
    search_fields = ['name', 'illness', 'prescription']
    list_editable = ['bill_balance']  
    list_per_page = 25
    ordering = ['-admitted_on']  
    
    fieldsets = (
        ('Patient Details', {
            'fields': ('name', 'illness', 'prescription')
        }),
        ('Billing', {
            'fields': ('bill_balance',),
            'description': 'Set to 0 when patient is cleared to go home'
        }),
    )
    
    
    def bill_status(self, obj):
        if obj.bill_balance > 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">Owes ₦{}</span>', 
                obj.bill_balance
            )
        return format_html('<span style="color: green; font-weight: bold;">Cleared</span>')
    bill_status.short_description = 'Status'

# Register your models here.
