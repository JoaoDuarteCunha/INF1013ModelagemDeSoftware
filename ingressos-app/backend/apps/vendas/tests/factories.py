from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.assentos.models import Assento
from apps.catalogo.models import Filme
from apps.cinemas.models import Cinema, Sala
from apps.sessoes.models import Sessao


def criar_usuario(
    username="cliente",
    password="senha123",
):
    User = get_user_model()

    return User.objects.create_user(
        username=username,
        email=f"{username}@teste.com",
        password=password,
    )


def criar_filme():
    return Filme.objects.create(
        nome="Filme Teste",
        genero="Ação",
        sinopse="Sinopse do filme de teste.",
        duracao_minutos=120,
        formato="2D",
    )


def criar_cinema():
    return Cinema.objects.create(
        cnpj="12.345.678/0001-90",
        nome="Cinema Teste",
        endereco="Rua Teste, 123",
    )


def criar_sala(cinema=None):
    if cinema is None:
        cinema = criar_cinema()

    return Sala.objects.create(
        cinema=cinema,
        nome="Sala 1",
        capacidade=100,
        suporta_2d=True,
        suporta_3d=True,
    )


def criar_assento(
    sala=None,
    fila="A",
    numero=1,
):
    if sala is None:
        sala = criar_sala()

    return Assento.objects.create(
        sala=sala,
        fila=fila,
        numero=numero,
    )


def criar_sessao(
    filme=None,
    sala=None,
    preco_base=Decimal("30.00"),
    inicio=None,
):
    if filme is None:
        filme = criar_filme()

    if sala is None:
        sala = criar_sala()

    if inicio is None:
        inicio = timezone.now() + timedelta(days=1)

    return Sessao.objects.create(
        filme=filme,
        sala=sala,
        inicio=inicio,
        fim=inicio + timedelta(hours=2),
        preco_base=preco_base,
        ativa=True,
    )
