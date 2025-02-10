from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone  # Añade esta línea
from .models import AuditoriaRegistro 

def enviar_correo_activacion(usuario):
    subject = 'Activa tu cuenta'
    activation_link = f"{settings.BASE_URL}{reverse('activar_cuenta', args=[str(usuario.activation_token)])}"
    message = f'Hola {usuario.nombres},\n\nPor favor, activa tu cuenta haciendo clic en el siguiente enlace:\n\n{activation_link}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [usuario.correo_institucional]
    send_mail(subject, message, email_from, recipient_list)

    AuditoriaRegistro.objects.create(
        usuario=usuario,
        accion='Correo de activación enviado',
        detalles=f'Correo enviado a {usuario.correo_institucional}'
    )

from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.timezone import now

def enviar_correo_recuperacion(usuario):
    subject = 'Recuperación de contraseña'
    reset_link = f"{settings.BASE_URL}{reverse('resetear_password', args=[str(usuario.reset_password_token)])}"
    message = (
        f'Hola {usuario.nombres},\n\n'
        f'Hemos recibido una solicitud para restablecer tu contraseña.\n'
        f'Para continuar con el proceso, haz clic en el siguiente enlace:\n\n'
        f'{reset_link}\n\n'
        f'Si no realizaste esta solicitud, puedes ignorar este mensaje.\n'
        f'Este enlace expirará en 30 minutos.'
    )
    
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [usuario.correo_institucional]
    
    send_mail(subject, message, email_from, recipient_list)
    
    # Registrar en auditoría
    AuditoriaRegistro.objects.create(
        usuario=usuario,
        accion='Correo de recuperación enviado',
        detalles=f'Correo enviado a {usuario.correo_institucional}'
    )

