from django.test import TestCase

from apps.sessoes.models import AssentoSessao
from apps.sessoes.services import (
    reservar_assentos,
    cancelar_reserva_temporaria,
)
from apps.vendas.tests.factories import (
    criar_usuario,
    criar_sala,
    criar_assento,
    criar_sessao,
)


class CancelarReservaTestCase(TestCase):
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
        )

    def test_deve_cancelar_reserva_temporaria_do_usuario(self):
        reservar_assentos(
            sessao=self.sessao,
            assento_ids=[self.assento.id],
            usuario=self.usuario,
        )

        cancelar_reserva_temporaria(
            sessao=self.sessao,
            assento_ids=[self.assento.id],
            usuario=self.usuario,
        )

        assento_sessao = AssentoSessao.objects.get(
            sessao=self.sessao,
            assento=self.assento,
        )

        self.assertEqual(
            assento_sessao.status,
            AssentoSessao.Status.DISPONIVEL,
        )
        self.assertIsNone(assento_sessao.reservado_ate)
        self.assertIsNone(assento_sessao.reservado_por)
