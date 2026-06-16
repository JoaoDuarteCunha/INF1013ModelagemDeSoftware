from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from apps.sessoes.models import AssentoSessao
from apps.sessoes.services import (
    reservar_assentos,
    liberar_reservas_expiradas,
    AssentoIndisponivelError,
)
from apps.vendas.tests.factories import criar_sala, criar_assento, criar_sessao


class ReservaAssentosTestCase(TestCase):
    def setUp(self):
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
        )

    def test_deve_reservar_assentos_disponiveis(self):
        assentos_reservados = reservar_assentos(
            sessao=self.sessao,
            assento_ids=[
                self.assento_1.id,
                self.assento_2.id,
            ],
        )

        self.assertEqual(len(assentos_reservados), 2)

        statuses = AssentoSessao.objects.filter(
            sessao=self.sessao,
        ).values_list("status", flat=True)

        self.assertIn(
            AssentoSessao.Status.RESERVADO,
            list(statuses),
        )

    def test_nao_deve_reservar_assento_ja_reservado(self):
        reservar_assentos(
            sessao=self.sessao,
            assento_ids=[self.assento_1.id],
        )

        with self.assertRaises(AssentoIndisponivelError):
            reservar_assentos(
                sessao=self.sessao,
                assento_ids=[self.assento_1.id],
            )

    def test_deve_liberar_reserva_expirada(self):
        reservar_assentos(
            sessao=self.sessao,
            assento_ids=[self.assento_1.id],
        )

        assento_sessao = AssentoSessao.objects.get(
            sessao=self.sessao,
            assento=self.assento_1,
        )

        assento_sessao.reservado_ate = timezone.now() - timedelta(minutes=1)
        assento_sessao.save(update_fields=["reservado_ate"])

        liberar_reservas_expiradas(self.sessao)

        assento_sessao.refresh_from_db()

        self.assertEqual(
            assento_sessao.status,
            AssentoSessao.Status.DISPONIVEL,
        )
        self.assertIsNone(assento_sessao.reservado_ate)
