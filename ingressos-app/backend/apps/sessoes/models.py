from django.db import models
from django.conf import settings
from apps.catalogo.models import Filme
from apps.cinemas.models import Sala
from apps.assentos.models import Assento


class Sessao(models.Model):
    filme = models.ForeignKey(
        Filme,
        on_delete=models.PROTECT,
        related_name="sessoes",
    )
    sala = models.ForeignKey(
        Sala,
        on_delete=models.PROTECT,
        related_name="sessoes",
    )
    inicio = models.DateTimeField()
    fim = models.DateTimeField()
    preco_base = models.DecimalField(max_digits=10, decimal_places=2)
    ativa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.filme.nome} - {self.inicio}"


class AssentoSessao(models.Model):
    class Status(models.TextChoices):
        DISPONIVEL = "disponivel", "Disponível"
        RESERVADO = "reservado", "Reservado"
        VENDIDO = "vendido", "Vendido"

    sessao = models.ForeignKey(
        Sessao,
        on_delete=models.CASCADE,
        related_name="assentos_sessao",
    )
    assento = models.ForeignKey(
        Assento,
        on_delete=models.PROTECT,
        related_name="sessoes",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DISPONIVEL,
    )
    reservado_ate = models.DateTimeField(null=True, blank=True)
    reservado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assentos_reservados",
    )

    class Meta:
        unique_together = ("sessao", "assento")

    def __str__(self):
        return f"{self.sessao} - {self.assento} - {self.status}"
