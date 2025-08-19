from django.urls import path
from .views import HomePageView, ServicoCreateView, AgendamentoCreateView, ServicoUpdateView

# Adicione aqui as URLs para a página inicial, agendamento, etc.
urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('servico/novo/', ServicoCreateView.as_view(), name='criar_servico'),
    # A rota de edição espera um 'pk' (primary key) do serviço
    path('servico/editar/<int:pk>/', ServicoUpdateView.as_view(), name='editar_servico'),
    path('agendar/<int:servico_id>/', AgendamentoCreateView.as_view(), name='agendar_servico'),
]