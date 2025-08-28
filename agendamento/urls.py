from django.urls import path
from .views import (
    HomePageView,
    ServicoCreateView,
    AgendamentoCreateView,
    ServicoUpdateView,
    cancelar_agendamento
)

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('servico/novo/', ServicoCreateView.as_view(), name='criar_servico'),
    path('servico/editar/<int:pk>/', ServicoUpdateView.as_view(), name='editar_servico'),
    path('agendar/<int:servico_id>/', AgendamentoCreateView.as_view(), name='agendar_servico'),
    path('agendamento/cancelar/<int:agendamento_id>/', cancelar_agendamento, name='cancelar_agendamento'),
]