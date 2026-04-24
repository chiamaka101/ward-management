from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from ward import views
from ward.forms import EmailLoginForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='registration/login.html', authentication_form=EmailLoginForm), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register/', views.register, name='register'),
    path('', views.home, name='home'),
    path('patient/<int:pk>/edit/', views.edit_patient, name='edit_patient'),
    path('patient/<int:pk>/discharge/', views.discharge_patient, name='discharge'),
    path('reports/', views.reports, name='reports'),
    path('staff/', views.staff_schedule, name='staff_schedule'),
    path('staff-schedule/edit/<int:pk>/', views.edit_shift, name='edit_shift'),
    path('staff-schedule/delete/<int:pk>/', views.delete_shift, name='delete_shift'),
    path('appointments/', views.appointments, name='appointments'),
    path('doctors/', views.doctors, name='doctors'),
]