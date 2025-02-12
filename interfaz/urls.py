from django.urls import path
from .views import InicioView

app_name = 'interfaz'

urlpatterns = [
    path('inicio/', InicioView.as_view(), name='inicio'),
]