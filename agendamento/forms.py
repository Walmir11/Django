from django import forms
from .models import Agendamento, Servico
from datetime import timedelta

class DurationWidget(forms.MultiWidget):
    """
    Um widget personalizado para renderizar dois menus suspensos para horas e minutos.
    """
    def __init__(self, attrs=None):
        # Define as opções para os dropdowns
        hour_choices = [(h, f'{h:02d}') for h in range(0, 11)]  # 0 a 10 horas
        minute_choices = [(m, f'{m:02d}') for m in range(0, 60, 15)] # 0, 15, 30, 45 minutos

        widgets = [
            forms.Select(attrs=attrs, choices=hour_choices),
            forms.Select(attrs=attrs, choices=minute_choices),
        ]
        super().__init__(widgets, attrs)

    def format_output(self, rendered_widgets):
        """Junta os widgets com um separador de ':' e os agrupa para melhor estilo."""
        # Agrupamos os selects com um separador para que se pareçam com um seletor de tempo (HH:MM)
        return f'<div style="display: flex; align-items: center; gap: 5px;">{rendered_widgets[0]}<span>:</span>{rendered_widgets[1]}</div>'

    def decompress(self, value):
        """
        Converte um valor timedelta (do banco de dados) em uma lista [horas, minutos].
        Exemplo: timedelta(hours=1, minutes=30) -> [1, 30]
        """
        if isinstance(value, timedelta):
            total_seconds = int(value.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return [hours, minutes]
        return [0, 30] # Valor padrão para um novo serviço

class DurationField(forms.MultiValueField):
    """
    Um campo de formulário personalizado que usa o DurationWidget e lida com a lógica
    de conversão entre o widget e o modelo.
    """
    widget = DurationWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.IntegerField(), # Campo para horas
            forms.IntegerField(), # Campo para minutos
        )
        super().__init__(fields=fields, require_all_fields=True, *args, **kwargs)

    def compress(self, data_list):
        """
        Pega a lista [horas, minutos] do widget e a converte em um
        objeto timedelta para salvar no banco de dados.
        Exemplo: [1, 30] -> timedelta(minutes=90)
        """
        if data_list:
            hours = data_list[0]
            minutes = data_list[1]
            if hours is not None and minutes is not None:
                total_minutes = (hours * 60) + minutes
                if total_minutes == 0:
                    # Impede que o serviço tenha duração zero
                    raise forms.ValidationError("A duração do serviço não pode ser zero.")
                return timedelta(minutes=total_minutes)
        return timedelta()


class ServicoForm(forms.ModelForm):
    # Substituímos o campo de texto pelo nosso novo campo de duração personalizado.
    duracao = DurationField(label="Duração")

    class Meta:
        model = Servico
        fields = ['categoria', 'nome', 'valor', 'duracao']
        # O label agora é definido diretamente no campo acima.


class AgendamentoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Remove 'servico' de kwargs antes de chamar o super(), pois o ModelForm não o espera.
        self.servico = kwargs.pop('servico', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Agendamento
        fields = ['data_hora_inicio']
        widgets = {
            'data_hora_inicio': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'})
        }

    def clean(self):
        cleaned_data = super().clean()
        data_hora_inicio = cleaned_data.get("data_hora_inicio")

        if data_hora_inicio and self.servico:
            profissional = self.servico.profissional
            duracao = self.servico.duracao
            data_hora_fim = data_hora_inicio + duracao

            # Query para encontrar agendamentos sobrepostos para o mesmo profissional.
            # Um agendamento sobrepõe se:
            # (start1 < end2) and (end1 > start2)
            agendamentos_sobrepostos = Agendamento.objects.filter(
                servico__profissional=profissional,
                status=Agendamento.StatusAgendamento.AGENDADO,
                data_hora_inicio__lt=data_hora_fim,  # O novo agendamento começa antes que o existente termine
                data_hora_fim__gt=data_hora_inicio,   # O novo agendamento termina depois que o existente começa
            )

            # Se estivermos editando um agendamento, precisamos excluí-lo da verificação.
            if self.instance and self.instance.pk:
                agendamentos_sobrepostos = agendamentos_sobrepostos.exclude(pk=self.instance.pk)

            if agendamentos_sobrepostos.exists():
                raise forms.ValidationError(
                    "Este horário já está ocupado por outro agendamento para este profissional. Por favor, escolha outro horário."
                )

        return cleaned_data


class CancelamentoAgendamentoForm(forms.Form):
    motivo = forms.CharField(
        label='Motivo do Cancelamento',
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Por favor, descreva o motivo do cancelamento.', 'class': 'form-control'}),
        required=True,
        help_text='O motivo é obrigatório para o cancelamento.'
    )