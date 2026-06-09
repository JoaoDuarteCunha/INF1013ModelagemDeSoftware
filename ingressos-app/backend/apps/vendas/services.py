from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.pagamentos.models import Pagamento
from apps.sessoes.models import AssentoSessao

from .models import Venda, Ingresso


class ReservaInvalidaError(Exception):
    pass


class PagamentoRecusadoError(Exception):
    pass


def calcular_preco(preco_base, tipo_ingresso):
    if tipo_ingresso == Ingresso.Tipo.INTEIRA:
        return preco_base

    return preco_base * Decimal("0.50")


def processar_pagamento_simulado(forma, aprovado=True):
    formas_validas = {
        Pagamento.Forma.PIX,
        Pagamento.Forma.CARTAO,
        Pagamento.Forma.DINHEIRO,
    }

    if forma not in formas_validas:
        raise PagamentoRecusadoError("Forma de pagamento inválida.")

    return aprovado


@transaction.atomic
def confirmar_venda(
    *,
    usuario,
    sessao,
    itens,
    forma_pagamento,
    canal=Venda.Canal.WEB,
    pagamento_aprovado=True,
):
    if not itens:
        raise ReservaInvalidaError("Nenhum ingresso foi informado.")

    assento_ids = [item["assento_id"] for item in itens]

    assentos_sessao = list(
        AssentoSessao.objects.select_for_update()
        .select_related("assento")
        .filter(
            sessao=sessao,
            assento_id__in=assento_ids,
        )
    )

    if len(assentos_sessao) != len(set(assento_ids)):
        raise ReservaInvalidaError("Um ou mais assentos não pertencem à sessão.")

    agora = timezone.now()

    for item in assentos_sessao:
        if item.status != AssentoSessao.Status.RESERVADO:
            raise ReservaInvalidaError(f"O assento {item.assento} não está reservado.")

        if not item.reservado_ate or item.reservado_ate <= agora:
            raise ReservaInvalidaError(f"A reserva do assento {item.assento} expirou.")

    tipo_por_assento = {item["assento_id"]: item["tipo"] for item in itens}

    valor_bruto = Decimal("0.00")
    precos = {}

    for assento_sessao in assentos_sessao:
        tipo = tipo_por_assento[assento_sessao.assento_id]

        tipos_validos = {escolha[0] for escolha in Ingresso.Tipo.choices}

        if tipo not in tipos_validos:
            raise ReservaInvalidaError(
                f"Tipo de ingresso inválido para o assento "
                f"{assento_sessao.assento}."
            )

        preco = calcular_preco(
            sessao.preco_base,
            tipo,
        )

        precos[assento_sessao.assento_id] = preco
        valor_bruto += preco

    venda = Venda.objects.create(
        usuario=usuario,
        sessao=sessao,
        status=Venda.Status.PENDENTE,
        canal=canal,
        valor_bruto=valor_bruto,
        valor_desconto=Decimal("0.00"),
        valor_final=valor_bruto,
    )

    pagamento = Pagamento.objects.create(
        venda=venda,
        forma=forma_pagamento,
        valor=venda.valor_final,
        status=Pagamento.Status.PENDENTE,
    )

    aprovado = processar_pagamento_simulado(
        forma=forma_pagamento,
        aprovado=pagamento_aprovado,
    )

    if not aprovado:
        pagamento.status = Pagamento.Status.RECUSADO
        pagamento.save(update_fields=["status"])

        venda.status = Venda.Status.CANCELADA
        venda.save(update_fields=["status"])

        raise PagamentoRecusadoError("Pagamento recusado.")

    ingressos = []

    for assento_sessao in assentos_sessao:
        ingresso = Ingresso.objects.create(
            venda=venda,
            assento_sessao=assento_sessao,
            tipo=tipo_por_assento[assento_sessao.assento_id],
            preco=precos[assento_sessao.assento_id],
        )
        ingressos.append(ingresso)

        assento_sessao.status = AssentoSessao.Status.VENDIDO
        assento_sessao.reservado_ate = None
        assento_sessao.save(update_fields=["status", "reservado_ate"])

    pagamento.status = Pagamento.Status.APROVADO
    pagamento.save(update_fields=["status"])

    venda.status = Venda.Status.CONFIRMADA
    venda.save(update_fields=["status"])

    return venda, ingressos
