from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Sessao, AssentoSessao
from .serializers import SessaoSerializer, AssentoSessaoSerializer


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

        assentos = AssentoSessao.objects.select_related(
            "assento",
            "sessao",
        ).filter(sessao=sessao)

        serializer = AssentoSessaoSerializer(assentos, many=True)
        return Response(serializer.data)
