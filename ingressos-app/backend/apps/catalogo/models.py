from django.db import models


class Filme(models.Model):
    class Formato(models.TextChoices):
        DOIS_D = "2D", "2D"
        TRES_D = "3D", "3D"
        QUATRO_D = "4D", "4D"
        IMAX = "IMAX", "IMAX"

    nome = models.CharField(max_length=255)
    genero = models.CharField(max_length=100)
    sinopse = models.TextField()
    duracao_minutos = models.PositiveIntegerField()
    formato = models.CharField(
        max_length=10,
        choices=Formato.choices,
        default=Formato.DOIS_D,
    )

    def __str__(self):
        return self.nome
