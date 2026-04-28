from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Patient, Bed, Staff, Shift, Department, Doctor, Appointment, MedicalRecord

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'doctor_count', 'created_at']
    search_fields = ['name']
    list_per_page = 25
    
    def doctor_count(self, obj):
        return obj.doctors.count()
    doctor_count.short_description = 'Doctors'

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialization', 'department', 'phone', 'appointment_count']
    list_filter = ['department', 'specialization']
    search_fields = ['name', 'specialization', 'phone']
    list_per_page = 25
    autocomplete_fields = ['department']
    
    def appointment_count(self, obj):
        return obj.appointments.count()
    appointment_count.short_description = 'Appointments'

@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ['bed_number', 'ward', 'status', 'status_badge', 'current_patient']
    list_filter = ['status', 'ward']
    search_fields = ['bed_number']
    list_editable = ['status']
    list_per_page = 25
    
    def status_badge(self, obj):
        colors = {
            'available': 'green',
            'occupied': 'red', 
            'maintenance': 'orange'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status Display'
    
    def current_patient(self, obj):
        patient = Patient.objects.filter(bed=obj, is_discharged=False).first()
        if patient:
            return patient.name
        return '-'
    current_patient.short_description = 'Patient'

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'gender', 'phone', 'get_bed', 'bill_balance', 'bill_status', 'admitted_on', 'is_discharged']
    list_filter = ['is_discharged', 'gender', 'admitted_on', 'illness', 'bed__ward']
    search_fields = ['name', 'phone', 'illness', 'prescription', 'bed__bed_number', 'insurance']
    list_editable = ['bill_balance']
    list_per_page = 25
    ordering = ['-admitted_on']
    date_hierarchy = 'admitted_on'
    autocomplete_fields = ['bed']
    
    fieldsets = (
        ('Patient Details', {
            'fields': ('name', 'gender', 'dob', 'phone', 'address', 'insurance')
        }),
        ('Medical Info', {
            'fields': ('illness', 'prescription')
        }),
        ('Ward Assignment', {
            'fields': ('bed',)
        }),
        ('Billing', {
            'fields': ('bill_balance',),
            'description': 'Set to 0 when patient is cleared to go home'
        }),
        ('Discharge Info', {
            'fields': ('is_discharged', 'discharged_at'),
            'classes': ('collapse',),
        }),
    )
    
    def get_bed(self, obj):
        if obj.bed:
            return obj.bed.bed_number
        return '-'
    get_bed.short_description = 'Bed'
    
    def bill_status(self, obj):
        if obj.bill_balance > 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">Owes ₦{}</span>', 
                obj.bill_balance
            )
        return format_html('<span style="color: green; font-weight: bold;">Cleared</span>')
    bill_status.short_description = 'Status'
    
    def save_model(self, request, obj, form, change):
        if obj.is_discharged and not obj.discharged_at:
            obj.discharged_at = timezone.now()
        super().save_model(request, obj, form, change)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'date_time', 'status', 'created_at']
    list_filter = ['status', 'doctor__department', 'date_time']
    search_fields = ['patient__name', 'doctor__name', 'reason']
    date_hierarchy = 'date_time'
    list_editable = ['status']
    list_per_page = 25
    autocomplete_fields = ['patient', 'doctor']
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('patient', 'doctor', 'date_time', 'reason')
        }),
        ('Status', {
            'fields': ('status',)
        }),
    )

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'appointment', 'diagnosis_short', 'created_at']
    list_filter = ['created_at', 'appointment__doctor']
    search_fields = ['patient__name', 'diagnosis', 'medications']
    date_hierarchy = 'created_at'
    list_per_page = 25
    autocomplete_fields = ['patient', 'appointment']
    
    def diagnosis_short(self, obj):
        return obj.diagnosis[:50] + '...' if len(obj.diagnosis) > 50 else obj.diagnosis
    diagnosis_short.short_description = 'Diagnosis'

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['get_email', 'role', 'phone', 'ward']
    list_filter = ['role', 'ward']
    search_fields = ['user__email', 'phone']
    list_per_page = 25
    autocomplete_fields = ['user']
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ['staff', 'ward', 'start_time', 'end_time', 'duration']
    list_filter = ['ward', 'start_time', 'staff__role']
    date_hierarchy = 'start_time'
    list_per_page = 25
    autocomplete_fields = ['staff']
    
    def duration(self, obj):
        delta = obj.end_time - obj.start_time
        hours = delta.total_seconds() / 3600
        return f"{hours:.1f} hrs"
    duration.short_description = 'Duration'