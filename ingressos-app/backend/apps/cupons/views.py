from decimal import Decimal, InvalidOperation

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Cupom
from .serializers import CupomSerializer
from .services import (
    CupomInvalidoError,
    buscar_cupom_valido,
    calcular_desconto,
)


class CupomViewSet(ReadOnlyModelViewSet):
    queryset = Cupom.objects.filter(ativo=True)
    serializer_class = CupomSerializer

    @action(
        detail=False,
        methods=["post"],
        url_path="validar",
    )
    def validar(self, request):
        codigo = request.data.get("codigo")
        valor_bruto = request.data.get("valor_bruto")

        try:
            valor_bruto = Decimal(str(valor_bruto))
        except (InvalidOperation, TypeError, ValueError):
            return Response(
                {"detail": "Valor bruto inválido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cupom = buscar_cupom_valido(codigo)
            desconto = calcular_desconto(cupom, valor_bruto)
        except CupomInvalidoError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "codigo": cupom.codigo,
                "tipo_desconto": cupom.tipo_desconto,
                "valor_desconto": desconto,
                "valor_final": valor_bruto - desconto,
            }
        )
