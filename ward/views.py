from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .models import Patient

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_staff = True
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def home(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        illness = request.POST.get('illness')
        prescription = request.POST.get('prescription')
        bill_balance = int(request.POST.get('bill_balance', 0))
        Patient.objects.create(
            name=name,
            illness=illness,
            prescription=prescription,
            bill_balance=bill_balance
        )
        return redirect('home')
    
    patients = Patient.objects.all().order_by('-id')
    context = {'patients': patients}
    return render(request, 'home.html', context)

@login_required
@require_POST
def discharge_patient(request, pk):
    Patient.objects.filter(pk=pk).delete()
    return redirect('home')