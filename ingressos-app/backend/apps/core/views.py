from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from apps.catalogo.models import Filme
from apps.sessoes.models import Sessao, AssentoSessao
from apps.sessoes.services import (
    garantir_assentos_da_sessao,
    liberar_reservas_expiradas,
)


def home(request):
    filmes = Filme.objects.all().order_by("nome")

    return render(
        request,
        "core/home.html",
        {
            "filmes": filmes,
        },
    )


def filme_detalhe(request, filme_id):
    filme = get_object_or_404(
        Filme,
        pk=filme_id,
    )

    sessoes = (
        Sessao.objects.select_related("filme", "sala", "sala__cinema")
        .filter(
            filme=filme,
            ativa=True,
            inicio__gte=timezone.now(),
        )
        .order_by("inicio")
    )

    return render(
        request,
        "core/filme_detalhe.html",
        {
            "filme": filme,
            "sessoes": sessoes,
        },
    )


def sessao_detalhe(request, sessao_id):
    sessao = get_object_or_404(
        Sessao.objects.select_related(
            "filme",
            "sala",
            "sala__cinema",
        ),
        pk=sessao_id,
    )

    garantir_assentos_da_sessao(sessao)
    liberar_reservas_expiradas(sessao)

    assentos_sessao = (
        AssentoSessao.objects.select_related("assento")
        .filter(sessao=sessao)
        .order_by("assento__fila", "assento__numero")
    )

    return render(
        request,
        "core/sessao_detalhe.html",
        {
            "sessao": sessao,
            "assentos_sessao": assentos_sessao,
        },
    )
