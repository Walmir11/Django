from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from .models import Servico, Agendamento
from .forms import AgendamentoForm

class HomePageView(ListView):
    """
    View para a página inicial que lista todos os serviços disponíveis.
    """
    model = Servico
    template_name = 'home.html'
    context_object_name = 'servicos' # Nome da variável no template


class ServicoCreateView(LoginRequiredMixin, CreateView):
    """
    View para que um profissional possa cadastrar um novo serviço.
    """
    model = Servico
    fields = ['categoria', 'nome', 'valor', 'duracao']
    template_name = 'servico_form.html'
    success_url = reverse_lazy('painel') # Redireciona para o painel após o sucesso

    def form_valid(self, form):
        # Associa o profissional logado automaticamente ao serviço criado
        form.instance.profissional = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Cadastrar Novo Serviço'
        return context


class AgendamentoCreateView(LoginRequiredMixin, CreateView):
    """
    View para um cliente criar um novo agendamento para um serviço.
    """
    model = Agendamento
    form_class = AgendamentoForm
    template_name = 'agendar.html'
    success_url = reverse_lazy('home') # Redireciona para a home (ou um painel) após o sucesso

    def dispatch(self, request, *args, **kwargs):
        """
        Carrega o objeto 'servico' antes de qualquer outro método da view.
        """
        self.servico = get_object_or_404(Servico, pk=self.kwargs['servico_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # O 'servico' já foi carregado no dispatch, apenas o adicionamos ao contexto.
        context['servico'] = self.servico
        context['titulo_pagina'] = f'Agendar "{self.servico.nome}"'
        return context

    def form_valid(self, form):
        # Antes de salvar, preenche os campos que não vêm do formulário
        agendamento = form.save(commit=False)
        agendamento.cliente = self.request.user
        agendamento.servico = self.servico # Agora self.servico existe tanto em GET quanto em POST
        # TODO: Adicionar validação de conflito de horário aqui
        return super().form_valid(form)
