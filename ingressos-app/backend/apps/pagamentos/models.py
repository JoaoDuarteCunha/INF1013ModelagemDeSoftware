import uuid

from django.db import models

from apps.vendas.models import Venda


class Pagamento(models.Model):
    class Forma(models.TextChoices):
        PIX = "pix", "Pix"
        CARTAO = "cartao", "Cartão"
        DINHEIRO = "dinheiro", "Dinheiro"

    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        APROVADO = "aprovado", "Aprovado"
        RECUSADO = "recusado", "Recusado"
        ESTORNADO = "estornado", "Estornado"

    venda = models.OneToOneField(
        Venda,
        on_delete=models.CASCADE,
        related_name="pagamento",
    )
    forma = models.CharField(
        max_length=20,
        choices=Forma.choices,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE,
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    transacao_externa = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pagamento #{self.id} - {self.status}"
