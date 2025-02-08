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
    
    usuario.email_sent_count += 1
    usuario.last_email_sent = timezone.now()
    usuario.save()

    AuditoriaRegistro.objects.create(
        usuario=usuario,
        accion='Correo de activación enviado',
        detalles=f'Correo enviado a {usuario.correo_institucional}'
    )

