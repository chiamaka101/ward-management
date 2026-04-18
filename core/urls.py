from django.contrib import admin
from django.urls import path, include  
from ward import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register, name='register'),
    path('', views.home, name='home'),
    path('delete/<int:pk>/', views.discharge_patient, name='discharge'),
]