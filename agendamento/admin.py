from django.contrib import admin
from .models import Categoria, Servico, Agendamento

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'profissional', 'categoria', 'valor', 'duracao')
    list_filter = ('categoria', 'profissional')
    search_fields = ('nome', 'profissional__username', 'profissional__first_name')
    autocomplete_fields = ('profissional', 'categoria')


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('servico', 'cliente', 'get_profissional', 'data_hora_inicio', 'status')
    # Corrigido: Filtra através do relacionamento Servico -> Profissional
    list_filter = ('status', 'servico__profissional', 'data_hora_inicio')
    search_fields = ('cliente__username', 'servico__nome', 'servico__profissional__username')
    # Corrigido: 'profissional' foi removido pois não é um campo direto
    autocomplete_fields = ('cliente', 'servico')

    @admin.display(description='Profissional', ordering='servico__profissional')
    def get_profissional(self, obj):
        """Retorna o nome do profissional a partir do serviço agendado."""
        if obj.servico and obj.servico.profissional:
            return obj.servico.profissional.first_name
        return "N/A"