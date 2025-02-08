from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

class UsuarioManager(BaseUserManager):
    def create_user(self, numero_documento, tipo_documento, correo_institucional, nombres, apellidos, password=None, **extra_fields):
        if not numero_documento:
            raise ValueError("El número de documento es obligatorio")
        if not correo_institucional:
            raise ValueError("El correo institucional es obligatorio")

        extra_fields.setdefault("is_active", True)
        user = self.model(
            numero_documento=numero_documento,
            tipo_documento=tipo_documento,
            correo_institucional=correo_institucional,
            nombres=nombres,
            apellidos=apellidos,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, numero_documento, tipo_documento, correo_institucional, nombres, apellidos, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(numero_documento, tipo_documento, correo_institucional, nombres, apellidos, password, **extra_fields)

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    TIPOS_DOCUMENTO = [
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        ('CE', 'Cédula de Extranjería'),
        ('PA', 'Pasaporte'),
    ]

    username = None  # Deshabilitamos el campo username por defecto
    tipo_documento = models.CharField(_('tipo de documento'), max_length=2, choices=TIPOS_DOCUMENTO)
    numero_documento = models.CharField(_('número de documento'), max_length=20, unique=True, primary_key=True)
    correo_institucional = models.EmailField(_('correo institucional'), unique=True)
    nombres = models.CharField(_('nombres'), max_length=150)
    apellidos = models.CharField(_('apellidos'), max_length=150)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)

    is_active = models.BooleanField(default=False)
    activation_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True, blank=True) 
    activation_token_created = models.DateTimeField(default=timezone.now)
    email_sent_count = models.IntegerField(default=0)
    last_email_sent = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'numero_documento'
    REQUIRED_FIELDS = ['tipo_documento', 'correo_institucional', 'nombres', 'apellidos']

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.numero_documento})"

    def generate_new_activation_token(self):
        self.activation_token = uuid.uuid4()
        self.activation_token_created = timezone.now()
        self.save()
    
    token_expiracion = models.DateTimeField(null=True, blank=True)
    contador_reenvios = models.IntegerField(default=0)
    ultimo_reenvio = models.DateTimeField(null=True, blank=True)

    def generar_nuevo_token(self):
        self.activation_token = uuid.uuid4()
        self.activation_token_created = timezone.now()
        self.token_expiracion = timezone.now() + timezone.timedelta(minutes=60) 
        self.save()

    def puede_reenviar_correo(self):
        if self.contador_reenvios >= 3:  # Límite de 3 reenvíos
            return False
        if self.ultimo_reenvio:
            tiempo_desde_ultimo_reenvio = timezone.now() - self.ultimo_reenvio
            return tiempo_desde_ultimo_reenvio > timezone.timedelta(minutes=5) 

    class Meta:
        verbose_name = _('usuario')
        verbose_name_plural = _('usuarios')

class AuditoriaRegistro(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    accion = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    detalles = models.TextField(blank=True)

    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.fecha}"

