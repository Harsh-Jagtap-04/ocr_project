from django.contrib import admin
from home.models import Contact
from home.models import CarPlate
from home.models import Invoice

# Register your models here.

admin.site.register(Contact)

@admin.register(CarPlate)
class CarPlateAdmin(admin.ModelAdmin):
    list_display = ('text', 'created_at')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice_no', 'date', 'bill_to', 'bank_name', 'total_amount', 'created_at']
    search_fields = ['invoice_no', 'bill_to']
    list_filter = ['date']
