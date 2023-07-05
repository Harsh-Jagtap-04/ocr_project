from django.db import models
from django.utils import timezone

# Create your models here.

class Contact(models.Model):
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    subject = models.CharField(max_length=30)
    message = models.TextField()

    def __str__(self):
        return self.name
    

class CarPlate(models.Model):
    text = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.text
    

class Invoice(models.Model):
    tel = models.CharField(max_length=255, null=True, blank=True)
    invoice_no = models.CharField(max_length=255, null=True, blank=True)
    date = models.CharField(max_length=255, null=True, blank=True)
    bill_to = models.CharField(max_length=255, null=True, blank=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    bank_account = models.CharField(max_length=255, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    total_amount = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice #{self.id}"