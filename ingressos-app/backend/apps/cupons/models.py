from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Cupom(models.Model):
    class TipoDesconto(models.TextChoices):
        PERCENTUAL = "percentual", "Percentual"
        FIXO = "fixo", "Valor fixo"

    codigo = models.CharField(
        max_length=50,
        unique=True,
    )
    tipo_desconto = models.CharField(
        max_length=20,
        choices=TipoDesconto.choices,
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    validade = models.DateTimeField()
    ativo = models.BooleanField(default=True)
    limite_usos = models.PositiveIntegerField(
        null=True,
        blank=True,
    )
    quantidade_usos = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return self.codigo

    @property
    def expirado(self):
        return self.validade <= timezone.now()

    @property
    def atingiu_limite(self):
        return self.limite_usos is not None and self.quantidade_usos >= self.limite_usos

    @property
    def disponivel(self):
        return self.ativo and not self.expirado and not self.atingiu_limite

    def clean(self):
        if self.valor <= 0:
            raise ValidationError(
                {"valor": "O valor do desconto deve ser maior que zero."}
            )

        if self.tipo_desconto == self.TipoDesconto.PERCENTUAL and self.valor > Decimal(
            "100.00"
        ):
            raise ValidationError(
                {"valor": "O desconto percentual não pode ultrapassar 100%."}
            )

        if self.validade and self.validade <= timezone.now():
            raise ValidationError({"validade": "A validade deve ser uma data futura."})

    def save(self, *args, validate=True, **kwargs):
        self.codigo = self.codigo.strip().upper()

        if validate:
            self.full_clean()

        super().save(*args, **kwargs)
