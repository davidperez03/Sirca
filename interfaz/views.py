from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from usuarios.views import BaseView

@method_decorator(login_required(login_url='usuarios:ingreso'), name='dispatch')
class InicioView(BaseView):
    template_name = 'interfaz/inicio.html'

    def get(self, request):
        return render(request, self.template_name)