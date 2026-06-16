from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from apps.catalogo.models import Filme
from apps.sessoes.models import Sessao, AssentoSessao
from apps.sessoes.services import (
    garantir_assentos_da_sessao,
    liberar_reservas_expiradas,
    reservar_assentos,
    AssentoInvalidoError,
    AssentoIndisponivelError,
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


def reservar_assentos_front(request, sessao_id):
    if request.method != "POST":
        return redirect("sessao_detalhe", sessao_id=sessao_id)

    sessao = get_object_or_404(
        Sessao.objects.select_related(
            "filme",
            "sala",
            "sala__cinema",
        ),
        pk=sessao_id,
    )

    assento_ids = request.POST.getlist("assento_ids")

    try:
        assentos_reservados = reservar_assentos(
            sessao=sessao,
            assento_ids=[int(assento_id) for assento_id in assento_ids],
        )
    except ValueError:
        messages.error(request, "Seleção de assentos inválida.")
        return redirect("sessao_detalhe", sessao_id=sessao.id)
    except AssentoInvalidoError as error:
        messages.error(request, str(error))
        return redirect("sessao_detalhe", sessao_id=sessao.id)
    except AssentoIndisponivelError as error:
        messages.error(request, str(error))
        return redirect("sessao_detalhe", sessao_id=sessao.id)

    ids_reservados = ",".join(str(item.assento_id) for item in assentos_reservados)

    messages.success(request, "Assentos reservados com sucesso.")

    return redirect(
        f"{reverse('reserva_detalhe', args=[sessao.id])}?assentos={ids_reservados}"
    )


def reserva_detalhe(request, sessao_id):
    sessao = get_object_or_404(
        Sessao.objects.select_related(
            "filme",
            "sala",
            "sala__cinema",
        ),
        pk=sessao_id,
    )

    liberar_reservas_expiradas(sessao)

    assentos_param = request.GET.get("assentos", "")

    try:
        assento_ids = [
            int(assento_id) for assento_id in assentos_param.split(",") if assento_id
        ]
    except ValueError:
        assento_ids = []

    assentos_reservados = (
        AssentoSessao.objects.select_related("assento")
        .filter(
            sessao=sessao,
            assento_id__in=assento_ids,
            status=AssentoSessao.Status.RESERVADO,
        )
        .order_by("assento__fila", "assento__numero")
    )

    return render(
        request,
        "core/reserva_detalhe.html",
        {
            "sessao": sessao,
            "assentos_reservados": assentos_reservados,
        },
    )
