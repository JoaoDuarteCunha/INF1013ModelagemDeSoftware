from django.db import models
from apps.cinemas.models import Sala


class Assento(models.Model):
    sala = models.ForeignKey(
        Sala,
        on_delete=models.CASCADE,
        related_name="assentos",
    )
    fila = models.CharField(max_length=5)
    numero = models.PositiveIntegerField()

    class Meta:
        unique_together = ("sala", "fila", "numero")
        ordering = ["fila", "numero"]

    def __str__(self):
        return f"{self.fila}{self.numero}"
