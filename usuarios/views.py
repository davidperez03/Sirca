from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views import View
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache, cache_page
from django.utils.decorators import method_decorator
from django.db import transaction
from functools import wraps
from uuid import UUID
import uuid
import logging


from .forms import( 
    FormularioCreacionUsuario, 
    FormularioReenvioActivacion,
    FormularioIngreso, 
    FormularioRecuperarPassword, 
    FormularioResetearPassword
)
from .utils import( 
    enviar_correo_activacion, 
    enviar_correo_recuperacion
)
from .models import AuditoriaRegistro, Usuario

# Configurar logger
logger = logging.getLogger(__name__)

def rate_limit(key_prefix, limit=5, period=300):
    """
    Decorador para limitar el número de intentos en un período de tiempo.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            client_ip = request.META.get('REMOTE_ADDR')
            cache_key = f"{key_prefix}_{client_ip}"
            
            # Obtener el número actual de intentos
            attempts = cache.get(cache_key, 0)
            
            if attempts >= limit:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                messages.error(request, 'Has excedido el límite de intentos. Espera unos minutos.')
                return redirect('ingreso')
            
            response = view_func(request, *args, **kwargs)
            
            # Si la solicitud no fue exitosa, aumentar el contador
            if response.status_code != 302:  # 302 indica redirección (éxito)
                cache.set(cache_key, attempts + 1, period)
            else:
                cache.delete(cache_key)  # Si fue exitoso, resetear el contador
            
            return response
        
        return _wrapped_view
    return decorator

class BaseView(View):
    """Vista base con funcionalidad común"""
    
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


    def log_action(self, action, details, usuario=None, level='INFO'):
        """Método centralizado para logging y auditoría"""
        try:
            AuditoriaRegistro.objects.create(
                usuario=usuario,
                accion=action,
                detalles=details
            )
            
            if level == 'INFO':
                logger.info(f"{action}: {details}")
            elif level == 'WARNING':
                logger.warning(f"{action}: {details}")
            elif level == 'ERROR':
                logger.error(f"{action}: {details}")
                
        except Exception as e:
            logger.error(f"Error al registrar auditoría: {str(e)}")

class RegistroUsuarioView(BaseView):
    template_name = 'usuarios/registro.html'

    @method_decorator(rate_limit('registro', limit=10, period=3600))
    def post(self, request):
        form = FormularioCreacionUsuario(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    usuario = form.save(commit=False)
                    
                    # Validar correo
                    try:
                        validate_email(usuario.correo_institucional)
                        dominio = usuario.correo_institucional.split('@')[-1].lower()
                        
                        if dominio not in settings.ALLOWED_EMAIL_DOMAINS:
                            raise ValidationError(
                                f"El correo debe pertenecer a: {', '.join(settings.ALLOWED_EMAIL_DOMAINS)}"
                            )
                    
                    except ValidationError as e:
                        form.add_error('correo_institucional', str(e))
                        return render(request, self.template_name, {'form': form})

                    if not usuario.rol:
                        form.add_error('rol', "Debe seleccionar un rol válido.")
                        return render(request, self.template_name, {'form': form})

                    # Configurar usuario
                    usuario.is_active = False
                    usuario.correo_institucional = usuario.correo_institucional.lower()
                    usuario.generar_nuevo_token()
                    usuario.save()
                    
                    # Enviar correo
                    try:
                        enviar_correo_activacion(usuario)
                    except Exception as e:
                        logger.error(f"Error al enviar correo: {str(e)}")
                        raise ValidationError("Error al enviar el correo de activación.")
                    
                    self.log_action(
                        'Registro de usuario',
                        f'Usuario registrado con rol: {usuario.rol.nombre if usuario.rol else "Sin rol"}',
                        usuario=usuario
                    )
                    
                    return redirect(reverse('confirmacion_registro'))
                    
            except Exception as e:
                logger.error(f"Error en registro: {str(e)}")
                messages.error(request, "Ocurrió un error durante el registro. Por favor, intenta nuevamente.")
                
        return render(request, self.template_name, {'form': form})

    def get(self, request):
        form = FormularioCreacionUsuario()
        return render(request, self.template_name, {'form': form})

class ConfirmacionRegistroView(BaseView):
    template_name = 'usuarios/confirmacion_registro.html'
    
    @method_decorator(cache_page(60 * 15))  # Cache por 15 minutos
    def get(self, request):
        return render(request, self.template_name)

class ActivarCuentaView(BaseView):
    @transaction.atomic
    def get(self, request, token):
        try:
            uuid_token = UUID(token, version=4)
            usuario = Usuario.objects.select_for_update().get(activation_token=uuid_token)

            if not usuario.is_active:
                if timezone.now() > usuario.token_expiracion:
                    self.log_action(
                        'Token expirado',
                        f'Token expirado para usuario: {usuario.correo_institucional}',
                        usuario=usuario,
                        level='WARNING'
                    )
                    messages.error(request, 'El enlace de activación ha expirado. Por favor, solicita uno nuevo.')
                    return redirect('reenviar_activacion')
                
                usuario.is_active = True
                usuario.activation_token = None
                usuario.save()
                
                self.log_action(
                    'Activación de cuenta',
                    'Cuenta activada exitosamente',
                    usuario=usuario
                )
                messages.success(request, '¡Tu cuenta ha sido activada exitosamente! Ahora puedes iniciar sesión.')
            else:
                messages.info(request, 'Esta cuenta ya está activa.')
                
        except (ValueError, TypeError):
            logger.warning(f"Intento de activación con token inválido: {token}")
            messages.error(request, 'El enlace de activación no es válido.')
        except Usuario.DoesNotExist:
            logger.warning(f"Intento de activación con token no existente: {token}")
            messages.error(request, 'El enlace de activación no es válido.')
        except Exception as e:
            logger.error(f"Error en activación de cuenta: {str(e)}")
            messages.error(request, 'Ocurrió un error al activar la cuenta. Por favor, intenta nuevamente.')
        
        return redirect('ingreso')

class ReenviarActivacionView(BaseView):
    template_name = 'usuarios/reenviar_activacion.html'
    
    def get(self, request):
        form = FormularioReenvioActivacion()
        return render(request, self.template_name, {'form': form})
    
    @method_decorator(rate_limit('reenvio_activacion', limit=3, period=900))  # 3 intentos cada 15 minutos
    @transaction.atomic
    def post(self, request):
        form = FormularioReenvioActivacion(request.POST)
        mensaje_generico = "Si existe una cuenta asociada a este correo, recibirás un enlace de activación."
        
        if form.is_valid():
            correo = form.cleaned_data['correo_institucional'].lower()
            
            try:
                usuario = Usuario.objects.select_for_update().get(
                    correo_institucional=correo,
                    is_active=False
                )
                
                # Verificar límites de reenvío
                ahora = timezone.now()
                if usuario.ultimo_reenvio and (ahora - usuario.ultimo_reenvio) < timezone.timedelta(minutes=1):
                    self.log_action(
                        'Intento de reenvío frecuente',
                        f'Intento de reenvío muy frecuente para: {correo}',
                        usuario=usuario,
                        level='WARNING'
                    )
                    messages.warning(request, "Por favor espera 1 minuto antes de solicitar otro correo.")
                    return render(request, self.template_name, {'form': form})
                
                if usuario.contador_reenvios >= settings.MAX_ACTIVATION_RESENDS:
                    self.log_action(
                        'Límite de reenvíos excedido',
                        f'Límite excedido para: {correo}',
                        usuario=usuario,
                        level='WARNING'
                    )
                    messages.error(request, "Has excedido el límite de reenvíos. Contacta a soporte.")
                    return render(request, self.template_name, {'form': form})
                
                # Actualizar usuario
                usuario.generar_nuevo_token()
                usuario.contador_reenvios += 1
                usuario.ultimo_reenvio = ahora
                usuario.save()
                
                # Enviar correo
                try:
                    enviar_correo_activacion(usuario)
                    self.log_action(
                        'Reenvío de activación',
                        f'Correo de activación reenviado a: {correo}',
                        usuario=usuario
                    )
                except Exception as e:
                    logger.error(f"Error al reenviar correo: {str(e)}")
                    raise ValidationError("Error al enviar el correo de activación.")
                
            except Usuario.DoesNotExist:
                # No revelamos si el correo existe o no
                logger.info(f"Intento de reenvío para correo no existente: {correo}")
            except Exception as e:
                logger.error(f"Error en reenvío de activación: {str(e)}")
                messages.error(request, "Ocurrió un error. Por favor, intenta nuevamente.")
                return render(request, self.template_name, {'form': form})
        
        messages.success(request, mensaje_generico)
        return render(request, self.template_name, {'form': form})


class RecuperarPasswordView(BaseView):
    template_name = 'usuarios/recuperar_password.html'
    
    def get(self, request):
        form = FormularioRecuperarPassword()
        return render(request, self.template_name, {'form': form})
    
    @method_decorator(rate_limit('recuperar_password', limit=3, period=900))
    @transaction.atomic
    def post(self, request):
        form = FormularioRecuperarPassword(request.POST)
        mensaje_generico = "Si existe una cuenta asociada a este correo, recibirás instrucciones para restablecer tu contraseña."
        
        if form.is_valid():
            correo = form.cleaned_data['correo_institucional']
            try:
                usuario = Usuario.objects.select_for_update().get(
                    correo_institucional=correo
                )
                
                usuario.reset_password_token = uuid.uuid4()
                usuario.reset_password_token_created = timezone.now()
                usuario.save()
                
                enviar_correo_recuperacion(usuario)
                
                self.log_action(
                    'Solicitud de recuperación de contraseña',
                    f'Correo de recuperación enviado a {usuario.correo_institucional}',
                    usuario=usuario
                )
                
            except Usuario.DoesNotExist:
                logger.info(f"Intento de recuperación para correo no existente: {correo}")
            except Exception as e:
                logger.error(f"Error en recuperación de contraseña: {str(e)}")
                messages.error(request, "Ocurrió un error. Por favor, intenta nuevamente.")
                return render(request, self.template_name, {'form': form})
        
        messages.success(request, mensaje_generico)
        return render(request, self.template_name, {'form': form})
    

class ResetearPasswordView(BaseView):
    template_name = 'usuarios/resetear_password.html'

    def get(self, request, token):
        try:
            usuario = Usuario.objects.get(reset_password_token=token)
            
            tiempo_limite = usuario.reset_password_token_created + timezone.timedelta(minutes=30)
            if timezone.now() > tiempo_limite:
                messages.error(request, "El enlace de recuperación ha expirado.")
                return redirect('recuperar_password')

            form = FormularioResetearPassword()
            return render(request, self.template_name, {'form': form, 'token': token})

        except Usuario.DoesNotExist:
            messages.error(request, "El enlace de recuperación no es válido.")
            return redirect('recuperar_password')

    @transaction.atomic
    def post(self, request, token):
        form = FormularioResetearPassword(request.POST)
        if form.is_valid():
            try:
                usuario = Usuario.objects.get(reset_password_token=token)
                
                tiempo_limite = usuario.reset_password_token_created + timezone.timedelta(minutes=30)
                if timezone.now() > tiempo_limite:
                    messages.error(request, "El enlace de recuperación ha expirado.")
                    return redirect('recuperar_password')

                usuario.set_password(form.cleaned_data['password'])
                usuario.reset_password_token = None
                usuario.reset_password_token_created = None
                usuario.save()

                messages.success(request, "Tu contraseña ha sido actualizada con éxito.")
                return redirect('ingreso')

            except Usuario.DoesNotExist:
                messages.error(request, "El enlace de recuperación no es válido.")
                return redirect('recuperar_password')
        
        return render(request, self.template_name, {'form': form, 'token': token})


class IngresoView(BaseView):
    template_name = 'usuarios/ingreso.html'
    
    def get(self, request):
        form = FormularioIngreso()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = FormularioIngreso(request.POST)
        if form.is_valid():
            numero_documento = form.cleaned_data['numero_documento']
            password = form.cleaned_data['password']
            
            try:
                usuario = Usuario.objects.get(numero_documento=numero_documento)
                
                if not usuario.is_active:
                    messages.warning(
                        request, 
                        'Tu cuenta no está activada. Por favor, actívala para continuar.'
                    )
                    return redirect('reenviar_activacion')
                
                usuario_auth = authenticate(
                    request, 
                    numero_documento=numero_documento, 
                    password=password
                )
                
                if usuario_auth is not None:
                    login(request, usuario_auth)
                    return redirect('inicio')
                else:
                    messages.error(request, 'Contraseña incorrecta.')
                    
            except Usuario.DoesNotExist:
                messages.error(request, 'No existe un usuario con ese número de documento.')
        
        return render(request, self.template_name, {'form': form})

class InicioView(BaseView):
    template_name = 'usuarios/inicio.html'
    
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('ingreso')
        return render(request, self.template_name)