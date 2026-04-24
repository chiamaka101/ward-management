from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import date
from django.contrib import messages
from .models import Patient, Bed, Staff, Shift, Department, Doctor, Appointment, MedicalRecord
from .forms import EmailRegisterForm

def register(request):
    if request.method == 'POST':
        form = EmailRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_staff = True
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = EmailRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def home(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob') or None
        phone = request.POST.get('phone')
        address = request.POST.get('address', '')
        insurance = request.POST.get('insurance', '')
        bill_balance = int(request.POST.get('bill_balance', 0))
        bed_id = request.POST.get('bed')
        
        bed = None
        if bed_id and bed_id not in ['none', '']:
            bed = Bed.objects.filter(id=bed_id, status='available').first()
            if not bed:
                messages.error(request, "Selected bed is no longer available.")
                return redirect('home')
        
        patient = Patient.objects.create(
            name=name,
            gender=gender,
            dob=dob,
            phone=phone,
            address=address,
            insurance=insurance,
            bill_balance=bill_balance,
            bed=bed
        )
        if bed:
            bed.status = 'occupied'
            bed.save()
            messages.success(request, f"{patient.name} admitted to Bed {bed.bed_number}.")
        else:
            messages.success(request, f"{patient.name} admitted successfully.")
        return redirect('home')
    
    patients = Patient.objects.filter(is_discharged=False).select_related('bed').order_by('-admitted_on')
    available_beds = Bed.objects.filter(status='available')
    all_beds_count = Bed.objects.count()
    unpaid_count = patients.filter(bill_balance__gt=0).count()
    cleared_count = patients.filter(bill_balance=0).count()
    
    context = {
        'patients': patients,
        'available_beds': available_beds,
        'all_beds_count': all_beds_count,
        'unpaid_count': unpaid_count,
        'cleared_count': cleared_count,
        'doctors_count': Doctor.objects.count(),
        'appointments_today': Appointment.objects.filter(date_time__date=date.today()).count(),
    }
    return render(request, 'home.html', context)

@login_required
@require_POST
def discharge_patient(request, pk):
    patient = Patient.objects.filter(pk=pk, is_discharged=False).first()
    if not patient:
        messages.error(request, "Patient not found or already discharged.")
        return redirect('home')
    
    patient.is_discharged = True
    patient.discharged_at = timezone.now()
    if patient.bed:
        patient.bed.status = 'available'
        patient.bed.save()
        patient.bed = None
    patient.save()
    messages.success(request, f"{patient.name} discharged successfully.")
    return redirect('home')

@login_required
@require_POST
def edit_patient(request, pk):
    patient = Patient.objects.filter(pk=pk).first()
    if not patient:
        messages.error(request, "Patient not found.")
        return redirect('home')
    
    old_bed = patient.bed
    new_bed_id = request.POST.get('bed')
    
    patient.name = request.POST.get('name')
    patient.gender = request.POST.get('gender')
    patient.dob = request.POST.get('dob') or None
    patient.phone = request.POST.get('phone')
    patient.insurance = request.POST.get('insurance', '')
    patient.address = request.POST.get('address', '')
    patient.bill_balance = int(request.POST.get('bill_balance', 0))
    
    if new_bed_id and new_bed_id != '':
        if old_bed and str(old_bed.id) == str(new_bed_id):
            pass
        else:
            new_bed = Bed.objects.filter(id=new_bed_id).first()
            if not new_bed:
                messages.error(request, "Selected bed does not exist.")
                return redirect('home')
            if new_bed.status != 'available':
                messages.error(request, f"Bed {new_bed.bed_number} is not available.")
                return redirect('home')
            
            if old_bed:
                old_bed.status = 'available'
                old_bed.save()
            patient.bed = new_bed
            new_bed.status = 'occupied'
            new_bed.save()
    elif new_bed_id == '':
        if old_bed:
            old_bed.status = 'available'
            old_bed.save()
        patient.bed = None
    
    patient.save()
    messages.success(request, f"{patient.name} updated successfully.")
    return redirect('home')

@login_required
def appointments(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        doctor_id = request.POST.get('doctor')
        date_time = request.POST.get('date_time')
        reason = request.POST.get('reason')
        
        if patient_id and doctor_id and date_time and reason:
            try:
                Appointment.objects.create(
                    patient_id=int(patient_id),
                    doctor_id=int(doctor_id),
                    date_time=date_time,
                    reason=reason
                )
                messages.success(request, "Appointment scheduled successfully.")
            except (ValueError, TypeError):
                messages.error(request, "Invalid patient or doctor selected.")
        else:
            messages.error(request, "Please fill all required fields.")
        return redirect('appointments')
    
    context = {
        'appointments': Appointment.objects.all().select_related('patient', 'doctor').order_by('-date_time'),
        'patients': Patient.objects.filter(is_discharged=False),
        'doctors': Doctor.objects.all(),
    }
    return render(request, 'appointments.html', context)

@login_required
def doctors(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        specialization = request.POST.get('specialization')
        department_id = request.POST.get('department')
        phone = request.POST.get('phone')
        
        if not name or not specialization or not department_id or department_id in ['none', '']:
            messages.error(request, "Please fill all required fields and select a valid department.")
            return redirect('doctors')
        
        try:
            Doctor.objects.create(
                name=name,
                specialization=specialization,
                department_id=int(department_id),
                phone=phone
            )
            messages.success(request, f"Dr. {name} added successfully.")
        except (ValueError, TypeError):
            messages.error(request, "Invalid department selected.")
        except Exception as e:
            messages.error(request, f"Error adding doctor: {str(e)}")
        
        return redirect('doctors')
    
    context = {
        'doctors': Doctor.objects.all().select_related('department'),
        'departments': Department.objects.all(),
    }
    return render(request, 'doctors.html', context)

@login_required
def reports(request):
    total_admissions = Patient.objects.count()
    total_discharged = Patient.objects.filter(is_discharged=True).count()
    active_patients = Patient.objects.filter(is_discharged=False).count()
    total_outstanding = Patient.objects.filter(is_discharged=False).aggregate(
        total=Sum('bill_balance')
    )['total'] or 0
    
    bed_stats = Bed.objects.aggregate(
        total=Count('id'),
        available=Count('id', filter=Q(status='available')),
        occupied=Count('id', filter=Q(status='occupied')),
        maintenance=Count('id', filter=Q(status='maintenance'))
    )
    
    def calc_percent(part, whole):
        return round((part / whole * 100), 1) if whole > 0 else 0
    
    bed_total = bed_stats['total']
    bed_percentages = {
        'available': calc_percent(bed_stats['available'], bed_total),
        'occupied': calc_percent(bed_stats['occupied'], bed_total),
        'maintenance': calc_percent(bed_stats['maintenance'], bed_total),
    }
    
    avg_bill = round(total_outstanding / active_patients, 0) if active_patients > 0 else 0
    discharge_rate = calc_percent(total_discharged, total_admissions)
    
    context = {
        'total_admissions': total_admissions,
        'total_discharged': total_discharged,
        'active_patients': active_patients,
        'total_outstanding': total_outstanding,
        'bed_stats': bed_stats,
        'bed_percentages': bed_percentages,
        'avg_bill': avg_bill,
        'discharge_rate': discharge_rate,
    }
    return render(request, 'reports.html', context)

@login_required
def staff_schedule(request):
    if request.method == 'POST':
        staff_id = request.POST.get('staff')
        ward = request.POST.get('ward')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        if staff_id and ward and start_time and end_time:
            try:
                Shift.objects.create(
                    staff_id=int(staff_id),
                    ward=ward,
                    start_time=start_time,
                    end_time=end_time
                )
                messages.success(request, "Shift scheduled successfully.")
            except (ValueError, TypeError):
                messages.error(request, "Invalid staff selected.")
        else:
            messages.error(request, "Please fill all required fields.")
        return redirect('staff_schedule')
    
    staff_list = Staff.objects.all().select_related('user')
    shifts = Shift.objects.select_related('staff__user').order_by('-start_time')[:50]
    wards = Bed.objects.values_list('ward', flat=True).distinct()
    
    context = {
        'staff_list': staff_list,
        'shifts': shifts,
        'wards': wards,
    }
    return render(request, 'staff_schedule.html', context)

@login_required
@require_POST
def edit_shift(request, pk):
    shift = Shift.objects.filter(pk=pk).first()
    if not shift:
        messages.error(request, "Shift not found.")
        return redirect('staff_schedule')
    
    staff_id = request.POST.get('staff')
    ward = request.POST.get('ward')
    start_time = request.POST.get('start_time')
    end_time = request.POST.get('end_time')
    
    if staff_id and ward and start_time and end_time:
        try:
            shift.staff_id = int(staff_id)
            shift.ward = ward
            shift.start_time = start_time
            shift.end_time = end_time
            shift.save()
            messages.success(request, "Shift updated successfully.")
        except (ValueError, TypeError):
            messages.error(request, "Invalid data provided.")
    else:
        messages.error(request, "Please fill all fields.")
    
    return redirect('staff_schedule')

@login_required
@require_POST
def delete_shift(request, pk):
    shift = Shift.objects.filter(pk=pk).first()
    if shift:
        shift.delete()
        messages.success(request, "Shift deleted successfully.")
    else:
        messages.error(request, "Shift not found.")
    return redirect('staff_schedule')