from django.contrib import admin
from django.urls import include, path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portal.urls', namespace='portal')),
    path('usuarios/', include('usuarios.urls', namespace='usuarios')),
    path('interfaz/', include('interfaz.urls', namespace='interfaz')),
]

urlpatterns += staticfiles_urlpatterns()