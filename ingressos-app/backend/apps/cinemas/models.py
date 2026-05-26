from django.db import models


class Cinema(models.Model):
    cnpj = models.CharField(max_length=18, unique=True)
    nome = models.CharField(max_length=255)
    endereco = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


class Sala(models.Model):
    cinema = models.ForeignKey(
        Cinema,
        on_delete=models.PROTECT,
        related_name="salas",
    )
    nome = models.CharField(max_length=100)
    capacidade = models.PositiveIntegerField()
    suporta_2d = models.BooleanField(default=True)
    suporta_3d = models.BooleanField(default=False)
    suporta_4d = models.BooleanField(default=False)
    suporta_imax = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.cinema.nome} - {self.nome}"
