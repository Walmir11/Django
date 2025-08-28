from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
from django.utils import timezone
from .forms import ClienteCreationForm, ProfissionalCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from agendamento.models import Agendamento, Servico

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
        if user.user_type == 'PROFISSIONAL' or user.is_superuser:
            return ['painel_profissional.html']
        elif user.user_type == 'CLIENTE':
            return ['painel_cliente.html']

    def get_context_data(self, **kwargs):
        """Adiciona os dados específicos de cada painel ao contexto."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.now()

        # Base queryset para os agendamentos do usuário logado
        if user.user_type == 'CLIENTE':
            base_queryset = Agendamento.objects.filter(cliente=user)
        elif user.user_type == 'PROFISSIONAL' or user.is_superuser:
            base_queryset = Agendamento.objects.filter(servico__profissional=user)
        else:
            base_queryset = Agendamento.objects.none()

        # Filtra agendamentos por status
        context['agendamentos_futuros'] = base_queryset.filter(
            data_hora_inicio__gte=now, status=Agendamento.StatusAgendamento.AGENDADO
        ).order_by('data_hora_inicio')

        # Considera agendamentos passados como concluídos ou agendados (que não ocorreram)
        context['agendamentos_passados'] = base_queryset.filter(
            data_hora_inicio__lt=now, status__in=[Agendamento.StatusAgendamento.AGENDADO, Agendamento.StatusAgendamento.CONCLUIDO]
        ).order_by('-data_hora_inicio')

        context['agendamentos_cancelados'] = base_queryset.filter(
            status=Agendamento.StatusAgendamento.CANCELADO
        ).order_by('-data_hora_inicio')

        # Adiciona contexto específico para cada tipo de usuário
        if user.user_type == 'PROFISSIONAL' or user.is_superuser:
            # Mantém a lista de serviços que o profissional oferece
            context['servicos'] = Servico.objects.filter(profissional=user)

        return context


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                login(request, user)
                return redirect('painel')
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')