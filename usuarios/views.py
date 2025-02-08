from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.utils import timezone
from .forms import FormularioCreacionUsuario, FormularioReenvioActivacion
from .utils import enviar_correo_activacion
from .models import AuditoriaRegistro, Usuario
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from uuid import UUID   

class RegistroUsuarioView(View):
    template_name = 'usuarios/registro.html'

    def get(self, request):
        form = FormularioCreacionUsuario()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = FormularioCreacionUsuario(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            
            DOMINIOS_PERMITIDOS = ["soy.sena.edu.co", "gmail.com", "misena.edu.co"]

            try:
                validate_email(usuario.correo_institucional)  
                dominio = usuario.correo_institucional.split('@')[-1].lower()  
                
                if dominio not in DOMINIOS_PERMITIDOS:
                    raise ValidationError("El correo debe pertenecer a @soy.sena.edu.co o @misena.edu.co.")
            
            except ValidationError:
                form.add_error('correo_institucional', "El correo institucional no es válido.")
                return render(request, self.template_name, {'form': form})

            if not usuario.rol:
                form.add_error('rol', "Debe seleccionar un rol válido.")
                return render(request, self.template_name, {'form': form})

            usuario.is_active = False
            usuario.generar_nuevo_token()
            usuario.save()
            
            enviar_correo_activacion(usuario)
            
            AuditoriaRegistro.objects.create(
                usuario=usuario,
                accion='Registro de usuario',
                detalles=f'Usuario registrado con rol: {usuario.rol.nombre if usuario.rol else "Sin rol"}, esperando activación'
            )
            
            return redirect(reverse('confirmacion_registro'))
        return render(request, self.template_name, {'form': form})

class ConfirmacionRegistroView(View):
    template_name = 'usuarios/confirmacion_registro.html'

    def get(self, request):
        return render(request, self.template_name)

class ActivarCuentaView(View):
    def get(self, request, token):
        try:
            uuid_token = UUID(token, version=4)
            usuario = Usuario.objects.get(activation_token=uuid_token)

            if not usuario.is_active:
                if timezone.now() > usuario.token_expiracion:
                    messages.error(request, 'El enlace de activación ha expirado. Por favor, solicita uno nuevo.')
                    return redirect('reenviar_activacion')
                
                usuario.is_active = True
                usuario.activation_token = None
                usuario.save()
                AuditoriaRegistro.objects.create(
                    usuario=usuario,
                    accion='Activación de cuenta',
                    detalles='Cuenta activada exitosamente'
                )
                messages.success(request, '¡Tu cuenta ha sido activada exitosamente! Ahora puedes iniciar sesión.')
            else:
                messages.info(request, 'Esta cuenta ya está activa.')
        except Usuario.DoesNotExist:
            messages.error(request, 'El enlace de activación no es válido.')
        
        return redirect('ingreso')

class ReenviarActivacionView(View):
    template_name = 'usuarios/reenviar_activacion.html'

    def get(self, request):
        form = FormularioReenvioActivacion()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = FormularioReenvioActivacion(request.POST)
        if form.is_valid():
            correo = form.cleaned_data.get('correo').lower().strip()  
            try:
                # Usar iexact para búsqueda insensible a mayúsculas/minúsculas
                usuario = Usuario.objects.get(correo_institucional__iexact=correo)
                
                # Verificar si la cuenta ya está activa
                if usuario.is_active:
                    messages.error(request, 'Esta cuenta ya está activa. No es necesario reenviar el correo de activación.')
                    AuditoriaRegistro.objects.create(
                        usuario=usuario,
                        accion='Intento de reenvío de activación',
                        detalles='Se intentó reenviar correo de activación a una cuenta ya activa'
                    )
                    return redirect('ingreso')
                
                # Si la cuenta no está activa, verificar límites de reenvío
                if usuario.puede_reenviar_correo():
                    usuario.generar_nuevo_token()
                    usuario.contador_reenvios += 1
                    usuario.ultimo_reenvio = timezone.now()
                    usuario.save()
                    
                    try:
                        enviar_correo_activacion(usuario)
                        messages.success(request, 'Se ha reenviado el correo de activación.')
                        
                        AuditoriaRegistro.objects.create(
                            usuario=usuario,
                            accion='Reenvío de correo de activación',
                            detalles=f'Reenvío exitoso. Contador: {usuario.contador_reenvios}'
                        )
                    except Exception as e:
                        messages.error(request, 'Hubo un error al enviar el correo. Por favor, intenta nuevamente.')
                        AuditoriaRegistro.objects.create(
                            usuario=usuario,
                            accion='Error en reenvío',
                            detalles=f'Error al enviar correo: {str(e)}'
                        )
                else:
                    messages.error(request, 'Has excedido el límite de reenvíos. Por favor, contacta al soporte.')
                    AuditoriaRegistro.objects.create(
                        usuario=usuario,
                        accion='Límite de reenvíos excedido',
                        detalles=f'Se intentó reenviar pero se excedió el límite. Contador: {usuario.contador_reenvios}'
                    )
                return redirect('ingreso')
                
            except Usuario.DoesNotExist:
                # Agregar registro de auditoría para intentos fallidos
                AuditoriaRegistro.objects.create(
                    usuario=None,
                    accion='Intento fallido de reenvío',
                    detalles=f'Correo no encontrado: {correo}'
                )
                messages.error(request, f'No se encontró ninguna cuenta con el correo: {correo}')
        
        return render(request, self.template_name, {'form': form})

class IngresoView(View):
    template_name = 'usuarios/ingreso.html'

    def get(self, request):
        return render(request, self.template_name)