from django.contrib import admin
from .models import Categoria, Servico, Agendamento

# Register your models here.

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """Configuração do Admin para Categoria."""
    list_display = ('nome',)
    search_fields = ('nome',)


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    """Configuração do Admin para Serviço."""
    list_display = ('nome', 'profissional', 'categoria', 'valor', 'duracao')
    list_filter = ('categoria', 'profissional')
    search_fields = ('nome', 'profissional__first_name', 'profissional__last_name')
    autocomplete_fields = ('profissional', 'categoria')


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    """Configuração do Admin para Agendamento."""
    list_display = ('servico', 'cliente', 'profissional', 'data_hora_inicio', 'status')
    list_filter = ('status', 'profissional', 'cliente', 'data_hora_inicio')
    search_fields = ('servico__nome', 'cliente__first_name', 'profissional__first_name')
    autocomplete_fields = ('cliente', 'profissional', 'servico')
    readonly_fields = ('data_hora_fim',) # Torna o campo de fim somente leitura, pois é calculado
