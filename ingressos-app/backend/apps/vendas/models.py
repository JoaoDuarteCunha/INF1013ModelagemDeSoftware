import uuid

from django.conf import settings
from django.db import models

from apps.sessoes.models import Sessao, AssentoSessao
from apps.cupons.models import Cupom


class Venda(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        CONFIRMADA = "confirmada", "Confirmada"
        CANCELADA = "cancelada", "Cancelada"

    class Canal(models.TextChoices):
        WEB = "web", "Web"
        APP = "app", "Aplicativo"
        BILHETERIA = "bilheteria", "Bilheteria"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="vendas",
    )
    sessao = models.ForeignKey(
        Sessao,
        on_delete=models.PROTECT,
        related_name="vendas",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE,
    )
    canal = models.CharField(
        max_length=20,
        choices=Canal.choices,
        default=Canal.WEB,
    )
    valor_bruto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    valor_desconto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    valor_final = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    cupom = models.ForeignKey(
        Cupom,
        on_delete=models.PROTECT,
        related_name="vendas",
        null=True,
        blank=True,
    )
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Venda #{self.id} - {self.status}"


class Ingresso(models.Model):
    class Tipo(models.TextChoices):
        INTEIRA = "inteira", "Inteira"
        MEIA = "meia", "Meia-entrada"
        MEIA_IDOSO = "meia_idoso", "Meia-entrada idoso"
        MEIA_SANTANDER = "meia_santander", "Meia Santander"

    venda = models.ForeignKey(
        Venda,
        on_delete=models.CASCADE,
        related_name="ingressos",
    )
    assento_sessao = models.OneToOneField(
        AssentoSessao,
        on_delete=models.PROTECT,
        related_name="ingresso",
    )
    tipo = models.CharField(
        max_length=30,
        choices=Tipo.choices,
    )
    preco = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    codigo = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ingresso {self.codigo}"
