from rest_framework import serializers

from .models import Venda, Ingresso


class IngressoSerializer(serializers.ModelSerializer):
    assento = serializers.CharField(
        source="assento_sessao.assento",
        read_only=True,
    )

    class Meta:
        model = Ingresso
        fields = [
            "id",
            "codigo",
            "assento",
            "tipo",
            "preco",
        ]


class VendaSerializer(serializers.ModelSerializer):
    ingressos = IngressoSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Venda
        fields = [
            "id",
            "usuario",
            "sessao",
            "status",
            "canal",
            "valor_bruto",
            "valor_desconto",
            "valor_final",
            "criada_em",
            "ingressos",
        ]
