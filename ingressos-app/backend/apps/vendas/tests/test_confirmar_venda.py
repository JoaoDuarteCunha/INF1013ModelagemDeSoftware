from decimal import Decimal

from django.test import TestCase

from apps.pagamentos.models import Pagamento
from apps.sessoes.models import AssentoSessao
from apps.sessoes.services import reservar_assentos
from apps.vendas.models import Ingresso, Venda
from apps.vendas.services import confirmar_venda, PagamentoRecusadoError
from apps.vendas.tests.factories import (
    criar_usuario,
    criar_sala,
    criar_assento,
    criar_sessao,
)


class ConfirmarVendaTestCase(TestCase):
    def setUp(self):
        self.usuario = criar_usuario()
        self.sala = criar_sala()
        self.assento_1 = criar_assento(
            sala=self.sala,
            fila="A",
            numero=1,
        )
        self.assento_2 = criar_assento(
            sala=self.sala,
            fila="A",
            numero=2,
        )
        self.sessao = criar_sessao(
            sala=self.sala,
            preco_base=Decimal("30.00"),
        )

        reservar_assentos(
            sessao=self.sessao,
            assento_ids=[
                self.assento_1.id,
                self.assento_2.id,
            ],
        )

    def test_deve_confirmar_venda_com_pagamento_aprovado(self):
        venda, ingressos = confirmar_venda(
            usuario=self.usuario,
            sessao=self.sessao,
            itens=[
                {
                    "assento_id": self.assento_1.id,
                    "tipo": Ingresso.Tipo.INTEIRA,
                },
                {
                    "assento_id": self.assento_2.id,
                    "tipo": Ingresso.Tipo.MEIA,
                },
            ],
            forma_pagamento=Pagamento.Forma.PIX,
            pagamento_aprovado=True,
        )

        self.assertEqual(venda.status, Venda.Status.CONFIRMADA)
        self.assertEqual(venda.valor_bruto, Decimal("45.00"))
        self.assertEqual(venda.valor_final, Decimal("45.00"))
        self.assertEqual(len(ingressos), 2)

        pagamento = Pagamento.objects.get(venda=venda)
        self.assertEqual(pagamento.status, Pagamento.Status.APROVADO)

        assentos_vendidos = AssentoSessao.objects.filter(
            sessao=self.sessao,
            status=AssentoSessao.Status.VENDIDO,
        ).count()

        self.assertEqual(assentos_vendidos, 2)

    def test_deve_recusar_venda_com_pagamento_recusado(self):
        with self.assertRaises(PagamentoRecusadoError):
            confirmar_venda(
                usuario=self.usuario,
                sessao=self.sessao,
                itens=[
                    {
                        "assento_id": self.assento_1.id,
                        "tipo": Ingresso.Tipo.INTEIRA,
                    },
                ],
                forma_pagamento=Pagamento.Forma.PIX,
                pagamento_aprovado=False,
            )

        self.assertEqual(Venda.objects.count(), 0)
        self.assertEqual(Pagamento.objects.count(), 0)

        assento_sessao = AssentoSessao.objects.get(
            sessao=self.sessao,
            assento=self.assento_1,
        )

        self.assertEqual(
            assento_sessao.status,
            AssentoSessao.Status.RESERVADO,
        )
