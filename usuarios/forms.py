from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Rol

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
        self.fields['rol'].error_messages = {
            'required': 'Debe seleccionar un rol.',
            'invalid_choice': 'Por favor seleccione un rol válido.'
        }

    def clean_rol(self):
        rol = self.cleaned_data.get('rol')
        if not rol:
            raise forms.ValidationError("Debe seleccionar un rol válido para continuar.")
        return rol

class FormularioReenvioActivacion(forms.Form):
    correo_institucional = forms.EmailField(
        label="Correo Institucional",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

