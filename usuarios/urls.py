from django.urls import path
from .views import RegistroUsuarioView, ConfirmacionRegistroView, ActivarCuentaView, ReenviarActivacionView, IngresoView, InicioView, RecuperarPasswordView
from .views import ResetearPasswordView  # Asegúrate de que está bien escrito

urlpatterns = [
    path('registro/', RegistroUsuarioView.as_view(), name='registro'),
    path('confirmacion-registro/', ConfirmacionRegistroView.as_view(), name='confirmacion_registro'),
    path('activar/<str:token>/', ActivarCuentaView.as_view(), name='activar_cuenta'),
    path('reenviar-activacion/', ReenviarActivacionView.as_view(), name='reenviar_activacion'),
    path('ingreso/', IngresoView.as_view(), name='ingreso'),
    path('inicio/', InicioView.as_view(), name='inicio'),

    path('recuperar-password/', RecuperarPasswordView.as_view(), name='recuperar_password'),
    path('resetear-password/<str:token>/', ResetearPasswordView.as_view(), name='resetear_password'),
]