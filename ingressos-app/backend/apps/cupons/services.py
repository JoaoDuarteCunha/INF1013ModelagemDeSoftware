from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .models import Cupom


class CupomInvalidoError(Exception):
    pass


def buscar_cupom_valido(codigo):
    if not codigo:
        return None

    codigo = codigo.strip().upper()

    try:
        cupom = Cupom.objects.get(codigo=codigo)
    except Cupom.DoesNotExist as error:
        raise CupomInvalidoError("Cupom não encontrado.") from error

    if not cupom.ativo:
        raise CupomInvalidoError("Este cupom está inativo.")

    if cupom.validade <= timezone.now():
        raise CupomInvalidoError("Este cupom está expirado.")

    if cupom.limite_usos is not None and cupom.quantidade_usos >= cupom.limite_usos:
        raise CupomInvalidoError("Este cupom atingiu o limite de utilizações.")

    return cupom


def calcular_desconto(cupom, valor_bruto):
    if cupom is None:
        return Decimal("0.00")

    if valor_bruto <= 0:
        return Decimal("0.00")

    if cupom.tipo_desconto == Cupom.TipoDesconto.PERCENTUAL:
        desconto = valor_bruto * cupom.valor / Decimal("100.00")
    else:
        desconto = cupom.valor

    return min(
        desconto.quantize(Decimal("0.01")),
        valor_bruto,
    )


@transaction.atomic
def registrar_utilizacao(cupom):
    if cupom is None:
        return

    cupom = Cupom.objects.select_for_update().get(pk=cupom.pk)

    if not cupom.disponivel:
        raise CupomInvalidoError("O cupom não está mais disponível.")

    cupom.quantidade_usos += 1
    cupom.save(
        update_fields=["quantidade_usos"],
        validate=False,
    )
