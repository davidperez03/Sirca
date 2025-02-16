from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Rol

class FormularioBase(forms.Form):
    """Clase base para formularios con estilos comunes"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class FormularioCreacionUsuario(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['tipo_documento', 'numero_documento', 'rol', 'correo_institucional',
                 'nombres', 'apellidos', 'password1', 'password2']
        labels = {
            'tipo_documento': 'Tipo de Documento',
            'numero_documento': 'Número de Documento',
            'correo_institucional': 'Correo Institucional',
            'nombres': 'Nombres',
            'apellidos': 'Apellidos',
            'rol': 'Rol',
            'password1': 'Contraseña',
            'password2': 'Confirmar Contraseña',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        placeholders = {
            'tipo_documento': 'Seleccione tipo de documento',
            'numero_documento': 'Ingrese su número de documento',
            'correo_institucional': 'Ingrese su correo institucional',
            'nombres': 'Ingrese sus nombres',
            'apellidos': 'Ingrese sus apellidos',
            'password1': 'Ingrese su contraseña',
            'password2': 'Confirme su contraseña',
        }
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[field_name]
        
        # Configurar el campo de rol
        self.fields['rol'].queryset = Rol.objects.all()
        self.fields['rol'].empty_label = "Seleccione un rol"
        self.fields['rol'].required = True
        self.fields['rol'].widget.attrs['class'] = 'form-control'
        self.fields['rol'].error_messages = {
            'required': 'Debe seleccionar un rol.',
            'invalid_choice': 'Por favor seleccione un rol válido.'
        }

class FormularioReenvioActivacion(FormularioBase):
    correo_institucional = forms.EmailField(
        label="Correo Institucional",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Ingrese su correo institucional'
        })
    )

class FormularioRecuperarPassword(FormularioBase):
    correo_institucional = forms.EmailField(
        label="Correo Institucional",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Ingrese su correo institucional'
        })
    )

class FormularioResetearPassword(FormularioBase):
    password = forms.CharField(
        label="Nueva Contraseña",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Ingrese su nueva contraseña'
        })
    )
    confirmar_password = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirme su nueva contraseña'
        })
    )

class FormularioIngreso(FormularioBase):
    numero_documento = forms.CharField(
        label="Número de Documento",
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese su número de documento'
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Ingrese su contraseña'
        })
    )

