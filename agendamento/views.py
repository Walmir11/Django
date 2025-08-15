from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Servico, Agendamento

# Create your views here.

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
