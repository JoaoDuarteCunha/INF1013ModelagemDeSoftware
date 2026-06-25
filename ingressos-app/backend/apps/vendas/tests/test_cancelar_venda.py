from decimal import Decimal

from django.test import TestCase

from apps.pagamentos.models import Pagamento
from apps.sessoes.models import AssentoSessao
from apps.sessoes.services import reservar_assentos
from apps.vendas.models import Ingresso, Venda
from apps.vendas.services import confirmar_venda, cancelar_venda
from apps.vendas.tests.factories import (
    criar_usuario,
    criar_sala,
    criar_assento,
    criar_sessao,
)


class CancelarVendaTestCase(TestCase):
    def setUp(self):
        self.usuario = criar_usuario()
        self.sala = criar_sala()
        self.assento = criar_assento(
            sala=self.sala,
            fila="A",
            numero=1,
        )
        self.sessao = criar_sessao(
            sala=self.sala,
            preco_base=Decimal("30.00"),
        )

        reservar_assentos(
            sessao=self.sessao,
            assento_ids=[self.assento.id],
        )

        self.venda, _ = confirmar_venda(
            usuario=self.usuario,
            sessao=self.sessao,
            itens=[
                {
                    "assento_id": self.assento.id,
                    "tipo": Ingresso.Tipo.INTEIRA,
                },
            ],
            forma_pagamento=Pagamento.Forma.PIX,
            pagamento_aprovado=True,
        )

    def test_deve_cancelar_venda_confirmada(self):
        venda = cancelar_venda(
            venda=self.venda,
            usuario=self.usuario,
        )

        venda.refresh_from_db()

        self.assertEqual(venda.status, Venda.Status.CANCELADA)
        self.assertEqual(
            venda.pagamento.status,
            Pagamento.Status.ESTORNADO,
        )

        assento_sessao = AssentoSessao.objects.get(
            sessao=self.sessao,
            assento=self.assento,
        )

        self.assertEqual(
            assento_sessao.status,
            AssentoSessao.Status.DISPONIVEL,
        )

    def test_deve_permitir_revender_assento_depois_do_cancelamento(self):
        venda_cancelada = cancelar_venda(
            venda=self.venda,
            usuario=self.usuario,
        )

        venda_cancelada.refresh_from_db()

        self.assertEqual(venda_cancelada.status, Venda.Status.CANCELADA)

        reservar_assentos(
            sessao=self.sessao,
            assento_ids=[self.assento.id],
        )

        nova_venda, ingressos = confirmar_venda(
            usuario=self.usuario,
            sessao=self.sessao,
            itens=[
                {
                    "assento_id": self.assento.id,
                    "tipo": Ingresso.Tipo.INTEIRA,
                },
            ],
            forma_pagamento=Pagamento.Forma.PIX,
            pagamento_aprovado=True,
        )

        self.assertEqual(nova_venda.status, Venda.Status.CONFIRMADA)
        self.assertEqual(len(ingressos), 1)

        self.assertEqual(
            Ingresso.objects.filter(assento_sessao__sessao=self.sessao).count(),
            2,
        )
