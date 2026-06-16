from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Sessao, AssentoSessao
from .serializers import SessaoSerializer, AssentoSessaoSerializer
from .services import (
    reservar_assentos,
    liberar_reservas_expiradas,
    garantir_assentos_da_sessao,
    AssentoIndisponivelError,
    AssentoInvalidoError,
)

from apps.vendas.models import Venda
from apps.vendas.serializers import VendaSerializer
from apps.vendas.services import (
    confirmar_venda,
    ReservaInvalidaError,
    PagamentoRecusadoError,
)
from apps.cupons.services import CupomInvalidoError
from datetime import datetime, time

from django.utils import timezone


class SessaoViewSet(ModelViewSet):
    serializer_class = SessaoSerializer

    def get_queryset(self):
        queryset = Sessao.objects.select_related(
            "filme",
            "sala",
            "sala__cinema",
        ).all()

        params = getattr(self.request, "query_params", self.request.GET)

        filme_id = params.get("filme")
        cinema_id = params.get("cinema")
        sala_id = params.get("sala")
        data = params.get("data")
        ativas = params.get("ativas")
        futuras = params.get("futuras")

        if filme_id:
            queryset = queryset.filter(filme_id=filme_id)

        if cinema_id:
            queryset = queryset.filter(sala__cinema_id=cinema_id)

        if sala_id:
            queryset = queryset.filter(sala_id=sala_id)

        if data:
            try:
                data_convertida = datetime.strptime(
                    data,
                    "%Y-%m-%d",
                ).date()

                inicio_dia = timezone.make_aware(
                    datetime.combine(data_convertida, time.min)
                )
                fim_dia = timezone.make_aware(
                    datetime.combine(data_convertida, time.max)
                )

                queryset = queryset.filter(inicio__range=(inicio_dia, fim_dia))
            except ValueError:
                queryset = queryset.none()

        if ativas is not None:
            ativas_normalizado = ativas.lower()

            if ativas_normalizado in ["true", "1", "sim", "yes"]:
                queryset = queryset.filter(ativa=True)

            elif ativas_normalizado in ["false", "0", "nao", "não", "no"]:
                queryset = queryset.filter(ativa=False)

        if futuras is not None:
            futuras_normalizado = futuras.lower()

            if futuras_normalizado in ["true", "1", "sim", "yes"]:
                queryset = queryset.filter(inicio__gte=timezone.now())

            elif futuras_normalizado in ["false", "0", "nao", "não", "no"]:
                queryset = queryset.filter(inicio__lt=timezone.now())

        return queryset.order_by("inicio")

    @action(
        detail=True,
        methods=["post"],
        url_path="reservar-assentos",
    )
    def reservar_assentos_action(self, request, pk=None):
        sessao = self.get_object()
        assento_ids = request.data.get("assento_ids", [])

        try:
            assentos_reservados = reservar_assentos(
                sessao=sessao,
                assento_ids=assento_ids,
            )
        except AssentoInvalidoError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except AssentoIndisponivelError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = AssentoSessaoSerializer(
            assentos_reservados,
            many=True,
        )

        return Response(
            {
                "detail": "Assentos reservados com sucesso.",
                "assentos": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="confirmar-venda",
    )
    def confirmar_venda_action(self, request, pk=None):
        sessao = self.get_object()

        itens = request.data.get("itens", [])
        forma_pagamento = request.data.get("forma_pagamento")
        pagamento_aprovado = request.data.get(
            "pagamento_aprovado",
            True,
        )
        codigo_cupom = request.data.get("codigo_cupom")

        if not request.user.is_authenticated:
            return Response(
                {"detail": "Autenticação obrigatória."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            venda, _ = confirmar_venda(
                usuario=request.user,
                sessao=sessao,
                itens=itens,
                forma_pagamento=forma_pagamento,
                codigo_cupom=codigo_cupom,
                canal=Venda.Canal.WEB,
                pagamento_aprovado=pagamento_aprovado,
            )
        except ReservaInvalidaError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except PagamentoRecusadoError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )
        except CupomInvalidoError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            VendaSerializer(venda).data,
            status=status.HTTP_201_CREATED,
        )
