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


class SessaoViewSet(ModelViewSet):
    queryset = Sessao.objects.select_related(
        "filme",
        "sala",
        "sala__cinema",
    ).all()
    serializer_class = SessaoSerializer

    @action(detail=True, methods=["get"])
    def assentos(self, request, pk=None):
        sessao = self.get_object()

        garantir_assentos_da_sessao(sessao)
        liberar_reservas_expiradas(sessao)

        assentos = AssentoSessao.objects.select_related(
            "assento",
            "sessao",
        ).filter(sessao=sessao)

        serializer = AssentoSessaoSerializer(assentos, many=True)
        return Response(serializer.data)

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
