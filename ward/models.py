from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Bed(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
    ]
    bed_number = models.CharField(max_length=10, unique=True)
    ward = models.CharField(max_length=50, default="General")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    def __str__(self):
        return f"Bed {self.bed_number} - {self.ward}"


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='doctors')
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"


class Patient(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='O')
    dob = models.DateField(null=True, blank=True, verbose_name="Date of Birth")
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    insurance = models.CharField(max_length=100, blank=True)
    
    
    illness = models.CharField(max_length=200, blank=True)
    prescription = models.TextField(blank=True)
    bill_balance = models.IntegerField(default=0)
    bed = models.OneToOneField(Bed, on_delete=models.SET_NULL, null=True, blank=True)
    admitted_on = models.DateTimeField(default=timezone.now)
    discharged_at = models.DateTimeField(null=True, blank=True)
    is_discharged = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date_time = models.DateTimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.patient.name} - Dr. {self.doctor.name} on {self.date_time.strftime('%b %d')}"


class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    diagnosis = models.TextField()
    medications = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Record for {self.patient.name} - {self.created_at.date()}"


class Staff(models.Model):
    ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('admin', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    ward = models.CharField(max_length=50, default="General")
    
    def __str__(self):
        return f"{self.user.email} - {self.get_role_display()}"


class Shift(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='shifts')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    ward = models.CharField(max_length=50, default="General")
    
    def __str__(self):
        return f"{self.staff.user.email} | {self.start_time.strftime('%b %d, %H:%M')}"