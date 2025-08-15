from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ClienteCreationForm, ProfissionalCreationForm

class CadastroClienteView(CreateView):
    form_class = ClienteCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Cadastro de Cliente'
        return context

class CadastroProfissionalView(CreateView):
    form_class = ProfissionalCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Cadastro de Profissional'
        return context

class PainelView(LoginRequiredMixin, TemplateView):
    def get_template_names(self):
        # Decide qual painel mostrar baseado no tipo de usuário
        if self.request.user.user_type == 'PROFISSIONAL':
            return ['painel_profissional.html']
        return ['painel_cliente.html']

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