from django.conf import settings
from django.db import models


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nome


class Servico(models.Model):
    profissional = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="servicos_oferecidos",
        limit_choices_to={"user_type": "PROFISSIONAL"},
    )
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="servicos")
    nome = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    duracao = models.DurationField("duração estimada")

    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"

    def __str__(self):
        return f"{self.nome} - {self.profissional.first_name}"


class Agendamento(models.Model):
    class StatusAgendamento(models.TextChoices):
        AGENDADO = "AGENDADO", "Agendado"
        CONCLUIDO = "CONCLUIDO", "Concluído"
        CANCELADO = "CANCELADO", "Cancelado"

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="agendamentos_feitos", limit_choices_to={"user_type": "CLIENTE"}
    )
    profissional = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="agendamentos_recebidos", limit_choices_to={"user_type": "PROFISSIONAL"}
    )
    servico = models.ForeignKey(Servico, on_delete=models.PROTECT)
    data_hora_inicio = models.DateTimeField("início do agendamento")
    data_hora_fim = models.DateTimeField("fim do agendamento", blank=True)
    status = models.CharField(max_length=10, choices=StatusAgendamento.choices, default=StatusAgendamento.AGENDADO)

    def save(self, *args, **kwargs):
        if self.data_hora_inicio and self.servico:
            self.data_hora_fim = self.data_hora_inicio + self.servico.duracao
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.servico.nome} para {self.cliente.first_name} em {self.data_hora_inicio.strftime('%d/%m/%Y %H:%M')}"