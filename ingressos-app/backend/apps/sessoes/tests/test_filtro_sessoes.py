from datetime import timedelta
from decimal import Decimal

from django.test import RequestFactory, TestCase
from django.utils import timezone

from apps.catalogo.models import Filme
from apps.cinemas.models import Cinema, Sala
from apps.sessoes.views import SessaoViewSet
from apps.vendas.tests.factories import criar_sessao


class FiltrosSessaoTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.filme_1 = Filme.objects.create(
            nome="Filme 1",
            genero="Ação",
            sinopse="Sinopse 1",
            duracao_minutos=120,
            formato="2D",
        )
        self.filme_2 = Filme.objects.create(
            nome="Filme 2",
            genero="Drama",
            sinopse="Sinopse 2",
            duracao_minutos=110,
            formato="2D",
        )

        self.cinema_1 = Cinema.objects.create(
            cnpj="11.111.111/0001-11",
            nome="Cinema 1",
            endereco="Rua 1",
        )
        self.cinema_2 = Cinema.objects.create(
            cnpj="22.222.222/0001-22",
            nome="Cinema 2",
            endereco="Rua 2",
        )

        self.sala_1 = Sala.objects.create(
            cinema=self.cinema_1,
            nome="Sala 1",
            capacidade=100,
            suporta_2d=True,
        )
        self.sala_2 = Sala.objects.create(
            cinema=self.cinema_2,
            nome="Sala 2",
            capacidade=100,
            suporta_2d=True,
        )

        self.inicio_amanha = timezone.now() + timedelta(days=1)
        self.inicio_depois = timezone.now() + timedelta(days=2)
        self.inicio_passado = timezone.now() - timedelta(days=1)

        self.sessao_1 = criar_sessao(
            filme=self.filme_1,
            sala=self.sala_1,
            preco_base=Decimal("30.00"),
            inicio=self.inicio_amanha,
        )
        self.sessao_2 = criar_sessao(
            filme=self.filme_2,
            sala=self.sala_2,
            preco_base=Decimal("40.00"),
            inicio=self.inicio_depois,
        )
        self.sessao_passada = criar_sessao(
            filme=self.filme_1,
            sala=self.sala_1,
            preco_base=Decimal("25.00"),
            inicio=self.inicio_passado,
        )

        self.sessao_2.ativa = False
        self.sessao_2.save(update_fields=["ativa"])

    def get_queryset_com_params(self, params):
        request = self.factory.get("/api/sessoes/", data=params)

        view = SessaoViewSet()
        view.request = request

        return view.get_queryset()

    def test_deve_filtrar_por_filme(self):
        queryset = self.get_queryset_com_params({"filme": self.filme_2.id})

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.sessao_2)

    def test_deve_filtrar_por_cinema(self):
        queryset = self.get_queryset_com_params({"cinema": self.cinema_2.id})

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.sessao_2)

    def test_deve_filtrar_por_data(self):
        data = self.inicio_amanha.date().isoformat()

        queryset = self.get_queryset_com_params({"data": data})

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.sessao_1)

    def test_deve_filtrar_apenas_ativas(self):
        queryset = self.get_queryset_com_params({"ativas": "true"})

        self.assertNotIn(self.sessao_2, list(queryset))
        self.assertIn(self.sessao_1, list(queryset))

    def test_deve_filtrar_apenas_futuras(self):
        queryset = self.get_queryset_com_params({"futuras": "true"})

        self.assertNotIn(self.sessao_passada, list(queryset))
        self.assertIn(self.sessao_1, list(queryset))
        self.assertIn(self.sessao_2, list(queryset))

    def test_deve_combinar_filtros(self):
        data = self.inicio_amanha.date().isoformat()

        queryset = self.get_queryset_com_params(
            {
                "filme": self.filme_1.id,
                "cinema": self.cinema_1.id,
                "data": data,
                "ativas": "true",
                "futuras": "true",
            }
        )

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.sessao_1)
