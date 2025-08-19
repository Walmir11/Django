from django.urls import path
from .views import HomePageView, ServicoCreateView, AgendamentoCreateView

# Adicione aqui as URLs para a página inicial, agendamento, etc.
urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('servico/novo/', ServicoCreateView.as_view(), name='servico_create'),
    path('agendar/<int:servico_id>/', AgendamentoCreateView.as_view(), name='agendar_servico'),
]