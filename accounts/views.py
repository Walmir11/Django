from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
from django.utils import timezone
from agendamento.models import Agendamento, Servico
from .forms import ClienteCreationForm, ProfissionalCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect

class CadastroClienteView(CreateView):
    """
    View para o cadastro de novos usuários do tipo Cliente.
    """
    form_class = ClienteCreationForm
    template_name = 'cadastro_form.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Cadastro de Cliente'
        return context


class CadastroProfissionalView(CreateView):
    """
    View para o cadastro de novos usuários do tipo Profissional.
    """
    form_class = ProfissionalCreationForm
    template_name = 'cadastro_form.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Cadastro de Profissional'
        return context


class PainelView(LoginRequiredMixin, TemplateView):
    """
    View que direciona o usuário para o painel correto (cliente ou profissional)
    e carrega os dados necessários para cada um.
    """

    def get_template_names(self):
        """Define qual template será usado com base no tipo de usuário."""
        user = self.request.user
        if user.user_type == 'CLIENTE':
            return ['painel_cliente.html']
        elif user.user_type == 'PROFISSIONAL':
            return ['painel_profissional.html']
        # Fallback para um template genérico, caso necessário
        return ['painel_base.html']

    def get_context_data(self, **kwargs):
        """Adiciona os dados específicos de cada painel ao contexto."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.now()

        if user.user_type == 'CLIENTE':
            # Para clientes, busca os agendamentos futuros
            context['agendamentos_futuros'] = Agendamento.objects.filter(
                cliente=user, data_hora_inicio__gte=now
            ).order_by('data_hora_inicio')
            # Adiciona a busca por agendamentos passados para o histórico
            context['agendamentos_passados'] = Agendamento.objects.filter(
                cliente=user, data_hora_inicio__lt=now
            ).order_by('-data_hora_inicio')

        elif user.user_type == 'PROFISSIONAL':
            # Para profissionais, busca agendamentos futuros e passados
            context['agendamentos_futuros'] = Agendamento.objects.filter(
                servico__profissional=user, data_hora_inicio__gte=now
            ).order_by('data_hora_inicio')
            context['agendamentos_passados'] = Agendamento.objects.filter(
                servico__profissional=user, data_hora_inicio__lt=now
            ).order_by('-data_hora_inicio')
            # Mantém a lista de serviços que o profissional oferece
            context['servicos'] = Servico.objects.filter(profissional=user)

        return context


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            # Como o USERNAME_FIELD é 'email', o form.cleaned_data['username'] conterá o email.
            user = form.get_user()
            if user is not None:
                login(request, user)
                return redirect('painel')
    # Passa o formulário (com erros, se houver) para o template com o nome 'form'
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    # Redireciona para a URL de login, conforme definido em settings.py
    return redirect('login')