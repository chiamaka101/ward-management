from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.contrib import messages

from .models import Patient, Bed, Staff, Shift, Department, Doctor, Appointment, MedicalRecord
from .forms import EmailRegisterForm

# -------------------------
# AUTH
# -------------------------
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

# -------------------------
# HOME
# -------------------------
@login_required
def home(request):
    # Handle Add Patient POST from modal
    if request.method == 'POST':
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob') or None
        phone = request.POST.get('phone')
        insurance = request.POST.get('insurance', '')
        address = request.POST.get('address', '')

        if name:
            Patient.objects.create(
                name=name,
                gender=gender,
                dob=dob,
                phone=phone,
                insurance=insurance,
                address=address,
                bill_balance=0
            )
            messages.success(request, f"{name} admitted successfully.")
        else:
            messages.error(request, "Patient name is required.")
        return redirect('home')

    # GET request - show dashboard
    context = {
        'patients': Patient.objects.filter(is_discharged=False).select_related('bed'),
        'available_beds': Bed.objects.filter(status='available'),
        'doctors_count': Doctor.objects.count(),
        'appointments_today': Appointment.objects.filter(
            date_time__date=timezone.now().date()
        ).count(),
        'departments': Department.objects.all(),  # Added for doctor modal
    }
    return render(request, 'home.html', context)

# -------------------------
# ADD DEPARTMENT
# -------------------------
@login_required
@require_POST
def add_department(request):
    name = request.POST.get('name')
    if name:
        Department.objects.get_or_create(name=name)
        messages.success(request, f"Department '{name}' created.")
    else:
        messages.error(request, "Department name is required.")
    return redirect('home')

# -------------------------
# DISCHARGE PATIENT
# -------------------------
@login_required
@require_POST
def discharge_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk, is_discharged=False)

    patient.is_discharged = True
    patient.discharged_at = timezone.now()

    if patient.bed:
        patient.bed.status = 'available'
        patient.bed.save()
        patient.bed = None

    patient.save()
    messages.success(request, f"{patient.name} discharged successfully.")
    return redirect('home')

# -------------------------
# EDIT PATIENT
# -------------------------
@login_required
@require_POST
def edit_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    old_bed = patient.bed
    new_bed_id = request.POST.get('bed')

    patient.name = request.POST.get('name')
    patient.gender = request.POST.get('gender')
    patient.dob = request.POST.get('dob') or None
    patient.phone = request.POST.get('phone')
    patient.insurance = request.POST.get('insurance', '')
    patient.address = request.POST.get('address', '')
    patient.bill_balance = int(request.POST.get('bill_balance', 0))

    # BED LOGIC
    if new_bed_id:
        if not old_bed or str(old_bed.id) != str(new_bed_id):
            new_bed = get_object_or_404(Bed, id=new_bed_id)

            if new_bed.status != 'available':
                messages.error(request, f"Bed {new_bed.bed_number} is not available.")
                return redirect('home')

            if old_bed:
                old_bed.status = 'available'
                old_bed.save()

            patient.bed = new_bed
            new_bed.status = 'occupied'
            new_bed.save()
    else:
        if old_bed:
            old_bed.status = 'available'
            old_bed.save()
        patient.bed = None

    patient.save()
    messages.success(request, f"{patient.name} updated successfully.")
    return redirect('home')

# -------------------------
# APPOINTMENTS
# -------------------------
@login_required
def appointments(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        doctor_id = request.POST.get('doctor')
        date_time = request.POST.get('date_time')
        reason = request.POST.get('reason')

        if patient_id and doctor_id and date_time and reason:
            Appointment.objects.create(
                patient_id=int(patient_id),
                doctor_id=int(doctor_id),
                date_time=date_time,
                reason=reason
            )
            messages.success(request, "Appointment scheduled successfully.")
        else:
            messages.error(request, "Please fill all fields.")

        return redirect('appointments')

    return render(request, 'appointments.html', {
        'appointments': Appointment.objects.select_related('patient', 'doctor').order_by('-date_time'),
        'patients': Patient.objects.filter(is_discharged=False),
        'doctors': Doctor.objects.all(),
    })

# -------------------------
# DOCTORS
# -------------------------
@login_required
def doctors(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        specialization = request.POST.get('specialization')
        department_id = request.POST.get('department')
        phone = request.POST.get('phone')

        if name and specialization and department_id:
            Doctor.objects.create(
                name=name,
                specialization=specialization,
                department_id=int(department_id),
                phone=phone
            )
            messages.success(request, f"Dr. {name} added successfully.")
        else:
            messages.error(request, "Fill all required fields.")

        return redirect('home')  # Changed to home so modal works from dashboard

    return render(request, 'doctors.html', {
        'doctors': Doctor.objects.select_related('department'),
        'departments': Department.objects.all(),
    })

# -------------------------
# REPORTS
# -------------------------
@login_required
def reports(request):
    total_admissions = Patient.objects.count()
    total_discharged = Patient.objects.filter(is_discharged=True).count()
    active_patients = Patient.objects.filter(is_discharged=False).count()

    total_outstanding = Patient.objects.filter(
        is_discharged=False
    ).aggregate(total=Sum('bill_balance'))['total'] or 0

    bed_stats = Bed.objects.aggregate(
        total=Count('id'),
        available=Count('id', filter=Q(status='available')),
        occupied=Count('id', filter=Q(status='occupied')),
        maintenance=Count('id', filter=Q(status='maintenance'))
    )

    return render(request, 'reports.html', {
        'total_admissions': total_admissions,
        'total_discharged': total_discharged,
        'active_patients': active_patients,
        'total_outstanding': total_outstanding,
        'bed_stats': bed_stats,
    })

# -------------------------
# STAFF SCHEDULE
# -------------------------
@login_required
def staff_schedule(request):
    if request.method == 'POST':
        staff_id = request.POST.get('staff')
        ward = request.POST.get('ward')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        if staff_id and ward and start_time and end_time:
            Shift.objects.create(
                staff_id=int(staff_id),
                ward=ward,
                start_time=start_time,
                end_time=end_time
            )
            messages.success(request, "Shift scheduled successfully.")
        else:
            messages.error(request, "Fill all fields.")

        return redirect('staff_schedule')

    return render(request, 'staff_schedule.html', {
        'staff_list': Staff.objects.all(),
        'shifts': Shift.objects.select_related('staff').order_by('-start_time')[:50],
        'wards': Bed.objects.values_list('ward', flat=True).distinct(),
    })

# -------------------------
# SHIFT EDIT
# -------------------------
@login_required
@require_POST
def edit_shift(request, pk):
    shift = get_object_or_404(Shift, pk=pk)
    shift.staff_id = request.POST.get('staff')
    shift.ward = request.POST.get('ward')
    shift.start_time = request.POST.get('start_time')
    shift.end_time = request.POST.get('end_time')
    shift.save()
    messages.success(request, "Shift updated.")
    return redirect('staff_schedule')

# -------------------------
# DELETE SHIFT
# -------------------------
@login_required
@require_POST
def delete_shift(request, pk):
    Shift.objects.filter(pk=pk).delete()
    messages.success(request, "Shift deleted.")
    return redirect('staff_schedule')