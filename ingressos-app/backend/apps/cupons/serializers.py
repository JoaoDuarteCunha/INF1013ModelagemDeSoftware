from rest_framework import serializers

from .models import Cupom


class CupomSerializer(serializers.ModelSerializer):
    disponivel = serializers.BooleanField(read_only=True)

    class Meta:
        model = Cupom
        fields = [
            "id",
            "codigo",
            "tipo_desconto",
            "valor",
            "validade",
            "ativo",
            "disponivel",
        ]
