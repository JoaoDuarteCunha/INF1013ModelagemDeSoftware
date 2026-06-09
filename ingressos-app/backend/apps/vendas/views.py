from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Venda
from .serializers import VendaSerializer
from .services import cancelar_venda, VendaNaoCancelavelError


class VendaViewSet(ReadOnlyModelViewSet):
    serializer_class = VendaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Venda.objects.select_related(
                "usuario",
                "sessao",
                "sessao__filme",
                "sessao__sala",
            )
            .prefetch_related(
                "ingressos",
                "ingressos__assento_sessao",
                "ingressos__assento_sessao__assento",
            )
            .filter(usuario=self.request.user)
            .order_by("-criada_em")
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="cancelar",
    )
    def cancelar(self, request, pk=None):
        venda = self.get_object()

        try:
            venda = cancelar_venda(
                venda=venda,
                usuario=request.user,
            )
        except VendaNaoCancelavelError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": "Venda cancelada com sucesso.",
                "venda": VendaSerializer(venda).data,
            },
            status=status.HTTP_200_OK,
        )
