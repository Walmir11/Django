from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from .models import Servico, Agendamento
from .forms import AgendamentoForm, ServicoForm

class HomePageView(ListView):
    """
    View para a página inicial que lista todos os serviços disponíveis.
    """
    model = Servico
    template_name = 'home.html'
    context_object_name = 'servicos' # Nome da variável no template

    def get_queryset(self):
        """
        Sobrescreve o queryset padrão.
        - Se o usuário for um profissional, mostra apenas os seus serviços.
        - Para outros usuários (clientes, anônimos), mostra todos os serviços.
        """
        user = self.request.user
        if user.is_authenticated and user.user_type == 'PROFISSIONAL':
            # Retorna apenas os serviços pertencentes ao profissional logado.
            return Servico.objects.filter(profissional=user)
        # Para todos os outros casos, retorna todos os serviços.
        return Servico.objects.all()


class ServicoCreateView(LoginRequiredMixin, CreateView):
    """
    View para que um profissional possa cadastrar um novo serviço.
    """
    model = Servico
    form_class = ServicoForm
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


class ServicoUpdateView(LoginRequiredMixin, UpdateView):
    """
    View para que um profissional possa editar um de seus serviços.
    """
    model = Servico
    form_class = ServicoForm
    template_name = 'servico_form.html'
    success_url = reverse_lazy('painel')

    def get_queryset(self):
        """
        Garante que o profissional só possa editar os seus próprios serviços.
        """
        queryset = super().get_queryset()
        return queryset.filter(profissional=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f'Editar Serviço: "{self.object.nome}"'
        return context

class AgendamentoCreateView(LoginRequiredMixin, CreateView):
    """
    View para um cliente criar um novo agendamento para um serviço.
    Impede que um profissional agende um serviço consigo mesmo.
    """
    model = Agendamento
    form_class = AgendamentoForm
    template_name = 'agendar.html'
    # Redireciona para o painel para que o usuário veja o agendamento na lista
    success_url = reverse_lazy('painel')

    def dispatch(self, request, *args, **kwargs):
        """
        Carrega o 'servico' e garante que apenas usuários do tipo 'CLIENTE' possam agendar.
        """
        self.servico = get_object_or_404(Servico, pk=self.kwargs['servico_id'])
        # Apenas usuários do tipo CLIENTE podem agendar.
        if request.user.user_type == 'PROFISSIONAL':
            messages.error(request, "Apenas clientes podem agendar serviços. Você está logado como um profissional.")
            return redirect('painel')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # O 'servico' já foi carregado no dispatch, apenas o adicionamos ao contexto.
        context['servico'] = self.servico
        context['titulo_pagina'] = f'Agendar "{self.servico.nome}"'
        return context

    def form_valid(self, form):
        """
        Define o cliente e o serviço antes de salvar e adiciona uma mensagem de sucesso.
        """
        # Antes de salvar, preenche os campos que não vêm do formulário
        form.instance.cliente = self.request.user
        form.instance.servico = self.servico
        # TODO: Adicionar validação de conflito de horário aqui
        messages.success(self.request, f"Serviço '{self.servico.nome}' agendado com sucesso!")
        return super().form_valid(form)

    # def _send_confirmation_emails(self, agendamento):
    #     """
    #     Envia e-mails de confirmação para o cliente e para o profissional.
    #     O e-mail do cliente terá o 'Reply-To' configurado para o profissional.
    #     """
    #     # E-mail para o Cliente
    #     subject_cliente = f"Agendamento Confirmado: {agendamento.servico.nome}"
    #     message_cliente = (
    #         f"Olá, {agendamento.cliente.first_name}!\n\n"
    #         f"Seu agendamento para o serviço '{agendamento.servico.nome}' com {agendamento.profissional.get_full_name()} "
    #         f"foi confirmado para o dia {agendamento.data_hora_inicio.strftime('%d/%m/%Y')} às {agendamento.data_hora_inicio.strftime('%H:%M')}.\n\n"
    #         "Caso precise entrar em contato, basta responder a este e-mail.\n\n"
    #         "Obrigado por usar nossos serviços!"
    #     )
    #     email_para_cliente = EmailMessage(
    #         subject_cliente,
    #         message_cliente,
    #         None,  # Usa o DEFAULT_FROM_EMAIL das configurações
    #         [agendamento.cliente.email],
    #         reply_to=[agendamento.profissional.email]  # A mágica acontece aqui!
    #     )
    #     email_para_cliente.send()
    #
    #     # E-mail para o Profissional (notificação interna simples)
    #     subject_profissional = f"Novo Agendamento: {agendamento.servico.nome}"
    #     message_profissional = (
    #         f"Olá, {agendamento.profissional.first_name}!\n\n"
    #         f"Você tem um novo agendamento para o serviço '{agendamento.servico.nome}'.\n"
    #         f"Cliente: {agendamento.cliente.get_full_name()}\n"
    #         f"Data: {agendamento.data_hora_inicio.strftime('%d/%m/%Y')} às {agendamento.data_hora_inicio.strftime('%H:%M')}.\n"
    #     )
    #     send_mail(subject_profissional, message_profissional, None, [agendamento.profissional.email])
