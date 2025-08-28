from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from datetime import datetime, time, timedelta
from .models import Servico, Agendamento, Categoria
from .forms import ServicoForm, AgendamentoForm, CancelamentoAgendamentoForm


class HomePageView(ListView):
    """
    View para a página inicial que lista todos os serviços disponíveis.
    """
    model = Servico
    template_name = 'home.html'
    context_object_name = 'servicos'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.user_type == 'PROFISSIONAL':
            return Servico.objects.filter(profissional=user)
        return Servico.objects.all()


class ServicoCreateView(LoginRequiredMixin, CreateView):
    """
    View para que um profissional possa cadastrar um novo serviço.
    """
    model = Servico
    form_class = ServicoForm
    template_name = 'servico_form.html'
    success_url = reverse_lazy('painel')

    def form_valid(self, form):
        form.instance.profissional = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Cadastrar Novo Serviço'
        return context


class ServicoUpdateView(LoginRequiredMixin, UpdateView):
    """
    View para que um profissional possa editar um de seus serviços.
    """
    model = Servico
    form_class = ServicoForm
    template_name = 'servico_form.html'
    success_url = reverse_lazy('painel')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(profissional=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f'Editar Serviço: "{self.object.nome}"'
        return context

class AgendamentoCreateView(LoginRequiredMixin, CreateView):
    """
    View para um cliente criar um novo agendamento para um serviço.
    """
    model = Agendamento
    form_class = AgendamentoForm
    template_name = 'agendar.html'
    success_url = reverse_lazy('painel')

    def dispatch(self, request, *args, **kwargs):
        self.servico = get_object_or_404(Servico, pk=self.kwargs['servico_id'])
        if request.user.user_type == 'PROFISSIONAL':
            messages.error(request, "Apenas clientes podem agendar serviços.")
            return redirect('painel')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Passa o objeto 'servico' para o __init__ do formulário."""
        kwargs = super().get_form_kwargs()
        kwargs['servico'] = self.servico
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['servico'] = self.servico
        context['titulo_pagina'] = f'Agendar "{self.servico.nome}"'
        return context

    def form_valid(self, form):
        form.instance.cliente = self.request.user
        form.instance.servico = self.servico
        messages.success(self.request, f"Serviço '{self.servico.nome}' agendado com sucesso!")
        return super().form_valid(form)


@login_required
def cancelar_agendamento(request, agendamento_id):
    """
    View para que um cliente ou profissional possa cancelar um agendamento,
    fornecendo um motivo.
    """
    agendamento = get_object_or_404(Agendamento, pk=agendamento_id)
    user = request.user

    # Verifica se o usuário tem permissão para cancelar
    is_cliente_do_agendamento = (user.user_type == 'CLIENTE' and agendamento.cliente == user)
    is_profissional_do_agendamento = (user.user_type == 'PROFISSIONAL' and agendamento.profissional == user)

    if not (is_cliente_do_agendamento or is_profissional_do_agendamento or user.is_superuser):
        raise PermissionDenied("Você não tem permissão para cancelar este agendamento.")

    # Impede o cancelamento de agendamentos que já ocorreram ou já foram cancelados
    if agendamento.data_hora_inicio < timezone.now():
        messages.error(request, "Não é possível cancelar um agendamento que já ocorreu.")
        return redirect('painel')
    if agendamento.status == Agendamento.StatusAgendamento.CANCELADO:
        messages.warning(request, "Este agendamento já foi cancelado.")
        return redirect('painel')

    if request.method == 'POST':
        form = CancelamentoAgendamentoForm(request.POST)
        if form.is_valid():
            agendamento.status = Agendamento.StatusAgendamento.CANCELADO
            agendamento.motivo_cancelamento = form.cleaned_data['motivo']
            agendamento.cancelado_por = user
            agendamento.save()
            messages.success(request, "Agendamento cancelado com sucesso.")
            return redirect('painel')
    else:
        form = CancelamentoAgendamentoForm()

    context = {'form': form, 'agendamento': agendamento, 'titulo_pagina': 'Cancelar Agendamento'}
    return render(request, 'cancelar_agendamento.html', context)


@login_required
def buscar_horarios_disponiveis(request, servico_id):
    """
    Retorna uma lista de horários disponíveis em formato JSON para um determinado serviço e data.
    """
    data_str = request.GET.get('data')
    if not data_str:
        return JsonResponse({'error': 'A data não foi fornecida.'}, status=400)

    try:
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Formato de data inválido. Use YYYY-MM-DD.'}, status=400)

    servico = get_object_or_404(Servico, pk=servico_id)
    profissional = servico.profissional
    duracao = servico.duracao

    # --- Lógica para gerar horários ---
    # TODO: Futuramente, buscar estes horários de um modelo do Profissional
    horario_inicio_trabalho = time(9, 0)
    horario_fim_trabalho = time(18, 0)

    # Pega todos os agendamentos do profissional para o dia
    agendamentos_do_dia = Agendamento.objects.filter(
        servico__profissional=profissional,
        data_hora_inicio__date=data,
        status=Agendamento.StatusAgendamento.AGENDADO
    ).values('data_hora_inicio', 'data_hora_fim')

    horarios_disponiveis = []
    slot_atual = datetime.combine(data, horario_inicio_trabalho)

    while slot_atual.time() < horario_fim_trabalho:
        slot_fim = slot_atual + duracao

        # O slot só é válido se terminar dentro do expediente
        if slot_fim.time() > horario_fim_trabalho and not (slot_fim.time() == horario_fim_trabalho and slot_fim.second == 0):
             break

        # Verifica se o slot atual está no passado
        if slot_atual < timezone.now():
            slot_atual += timedelta(minutes=15) # Incrementa para o próximo bloco
            continue

        # Verifica se o slot se sobrepõe a um agendamento existente
        sobreposto = False
        for agendamento in agendamentos_do_dia:
            if max(slot_atual, agendamento['data_hora_inicio']) < min(slot_fim, agendamento['data_hora_fim']):
                sobreposto = True
                break

        if not sobreposto:
            horarios_disponiveis.append(slot_atual.strftime('%H:%M'))

        # Incrementa o slot. Usar um intervalo fixo (ex: 15 min) permite mais flexibilidade.
        slot_atual += timedelta(minutes=15)

    return JsonResponse({'horarios': horarios_disponiveis})