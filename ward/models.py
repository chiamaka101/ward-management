from django.db import models
from django.utils import timezone

class Patient(models.Model):
    name = models.CharField(max_length=100)
    illness = models.CharField(max_length=200)
    prescription = models.CharField(max_length=200, blank=True)
    bill_balance = models.IntegerField(default=0)
    admitted_on = models.DateTimeField(default=timezone.now)  

    def __str__(self):
        return self.name