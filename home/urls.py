from django.urls import path, include
from home import views


urlpatterns = [
    path('', views.home, name='home'),
    path('contact', views.contact, name='contact'),
    path('text_extract', views.text_extract, name='text_extract'),
    path('download/<str:file_name>/', views.download_file, name='download_file'),
    path('licence_plate', views.licence_plate, name='licence_plate'),
    path('id', views.id, name='id'),
    path('Invoice_Reader', views.Invoice_Reader, name='Invoice_Reader'),
    path('Handwritten_Text', views.Handwritten_Text, name='Handwritten_Text')

]
