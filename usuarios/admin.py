from django.contrib import admin
from .models import Rol, Usuario

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('numero_documento', 'nombres', 'apellidos', 'correo_institucional', 'rol', 'is_active')
    search_fields = ('numero_documento', 'correo_institucional', 'nombres', 'apellidos')
    list_filter = ('rol', 'is_active', 'is_staff', 'is_superuser')
