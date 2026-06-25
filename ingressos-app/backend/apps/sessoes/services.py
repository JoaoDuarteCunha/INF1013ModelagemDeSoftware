from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.assentos.models import Assento
from .models import AssentoSessao

from apps.vendas.services import (
    ReservaInvalidaError,
)

TEMPO_RESERVA_MINUTOS = 10


class AssentoIndisponivelError(Exception):
    pass


class AssentoInvalidoError(Exception):
    pass


def liberar_reservas_expiradas(sessao):
    agora = timezone.now()

    AssentoSessao.objects.filter(
        sessao=sessao,
        status=AssentoSessao.Status.RESERVADO,
        reservado_ate__lt=agora,
    ).update(
        status=AssentoSessao.Status.DISPONIVEL,
        reservado_ate=None,
        reservado_por=None,
    )


def garantir_assentos_da_sessao(sessao):
    assentos = Assento.objects.filter(sala=sessao.sala)

    existentes = set(
        AssentoSessao.objects.filter(sessao=sessao).values_list("assento_id", flat=True)
    )

    novos = [
        AssentoSessao(
            sessao=sessao,
            assento=assento,
            status=AssentoSessao.Status.DISPONIVEL,
        )
        for assento in assentos
        if assento.id not in existentes
    ]

    if novos:
        AssentoSessao.objects.bulk_create(novos)


@transaction.atomic
def reservar_assentos(sessao, assento_ids, usuario=None):
    if not assento_ids:
        raise AssentoInvalidoError("Nenhum assento foi informado.")

    garantir_assentos_da_sessao(sessao)
    liberar_reservas_expiradas(sessao)

    assentos_validos = set(
        Assento.objects.filter(
            sala=sessao.sala,
            id__in=assento_ids,
        ).values_list("id", flat=True)
    )

    assentos_informados = set(assento_ids)

    if assentos_validos != assentos_informados:
        raise AssentoInvalidoError(
            "Um ou mais assentos não pertencem à sala desta sessão."
        )

    assentos_sessao = (
        AssentoSessao.objects.select_for_update()
        .select_related("assento")
        .filter(
            sessao=sessao,
            assento_id__in=assento_ids,
        )
    )

    indisponiveis = [
        assento_sessao
        for assento_sessao in assentos_sessao
        if assento_sessao.status != AssentoSessao.Status.DISPONIVEL
    ]

    if indisponiveis:
        labels = [f"{item.assento.fila}{item.assento.numero}" for item in indisponiveis]

        raise AssentoIndisponivelError(
            f"Assento(s) indisponível(is): {', '.join(labels)}"
        )

    reservas_de_outro_usuario = [
        item
        for item in assentos_sessao
        if item.reservado_por_id is not None and item.reservado_por_id != usuario.id
    ]

    if reservas_de_outro_usuario:
        raise ReservaInvalidaError(
            "Um ou mais assentos foram reservados por outro usuário."
        )

    reservado_ate = timezone.now() + timedelta(minutes=TEMPO_RESERVA_MINUTOS)

    for assento_sessao in assentos_sessao:
        assento_sessao.status = AssentoSessao.Status.RESERVADO
        assento_sessao.reservado_ate = reservado_ate
        assento_sessao.reservado_por = usuario
        assento_sessao.save(update_fields=["status", "reservado_ate", "reservado_por"])

    return list(assentos_sessao)
