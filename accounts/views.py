from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ClienteCreationForm, ProfissionalCreationForm

class CadastroClienteView(CreateView):
    form_class = ClienteCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')

class CadastroProfissionalView(CreateView):
    form_class = ProfissionalCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')

class PainelView(LoginRequiredMixin, TemplateView):
    def get_template_name(self):
        # Decide qual painel mostrar baseado no tipo de usuário
        if self.request.user.user_type == 'PROFISSIONAL':
            return 'accounts/painel_profissional.html'
        return 'accounts/painel_cliente.html'