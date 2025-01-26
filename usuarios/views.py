from django.shortcuts import render
from django.http import HttpResponse

# Registro de nuevos usuarios
def registro(request):
    return HttpResponse("Registro de usuarios")

def correo_activacion(request):
    return HttpResponse("Activación de usuarios")

def reenvio_correo_activacion(request):
    return HttpResponse("Reenvío de correo de activación")

def estado_activacion(request):
    return HttpResponse("Estado de activación de usuarios")


# Autenticación de usuarios

def login(request):
    return HttpResponse("Login de usuarios")

def restablecer_password(request):
    return HttpResponse("Restablecimiento de contraseña")

def editar_perfil(request):
    return HttpResponse("Edición del perfil de usuario")

def cambiar_password(request):
    return HttpResponse("Cambio de contraseña para usuarios autenticados")

def logout(request):
    return HttpResponse("Logout de usuarios")