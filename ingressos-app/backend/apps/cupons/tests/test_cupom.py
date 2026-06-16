from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.cupons.models import Cupom
from apps.cupons.services import (
    buscar_cupom_valido,
    calcular_desconto,
    CupomInvalidoError,
)


class CupomTestCase(TestCase):
    def test_deve_calcular_desconto_percentual(self):
        cupom = Cupom.objects.create(
            codigo="PROMO20",
            tipo_desconto=Cupom.TipoDesconto.PERCENTUAL,
            valor=Decimal("20.00"),
            validade=timezone.now() + timedelta(days=1),
            ativo=True,
        )

        desconto = calcular_desconto(
            cupom,
            Decimal("100.00"),
        )

        self.assertEqual(desconto, Decimal("20.00"))

    def test_deve_calcular_desconto_fixo(self):
        cupom = Cupom.objects.create(
            codigo="FIXO10",
            tipo_desconto=Cupom.TipoDesconto.FIXO,
            valor=Decimal("10.00"),
            validade=timezone.now() + timedelta(days=1),
            ativo=True,
        )

        desconto = calcular_desconto(
            cupom,
            Decimal("100.00"),
        )

        self.assertEqual(desconto, Decimal("10.00"))

    def test_desconto_fixo_nao_deve_passar_do_valor_bruto(self):
        cupom = Cupom.objects.create(
            codigo="FIXO100",
            tipo_desconto=Cupom.TipoDesconto.FIXO,
            valor=Decimal("100.00"),
            validade=timezone.now() + timedelta(days=1),
            ativo=True,
        )

        desconto = calcular_desconto(
            cupom,
            Decimal("30.00"),
        )

        self.assertEqual(desconto, Decimal("30.00"))

    def test_nao_deve_aceitar_cupom_inativo(self):
        Cupom.objects.create(
            codigo="INATIVO",
            tipo_desconto=Cupom.TipoDesconto.PERCENTUAL,
            valor=Decimal("10.00"),
            validade=timezone.now() + timedelta(days=1),
            ativo=False,
        )

        with self.assertRaises(CupomInvalidoError):
            buscar_cupom_valido("INATIVO")
