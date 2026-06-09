from rest_framework import serializers

from .models import Ingresso, Venda


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
    filme = serializers.CharField(
        source="sessao.filme.nome",
        read_only=True,
    )
    cinema = serializers.CharField(
        source="sessao.sala.cinema.nome",
        read_only=True,
    )
    sala = serializers.CharField(
        source="sessao.sala.nome",
        read_only=True,
    )
    sessao_inicio = serializers.DateTimeField(
        source="sessao.inicio",
        read_only=True,
    )
    pagamento_status = serializers.CharField(
        source="pagamento.status",
        read_only=True,
    )
    forma_pagamento = serializers.CharField(
        source="pagamento.forma",
        read_only=True,
    )

    class Meta:
        model = Venda
        fields = [
            "id",
            "usuario",
            "sessao",
            "filme",
            "cinema",
            "sala",
            "sessao_inicio",
            "status",
            "canal",
            "valor_bruto",
            "valor_desconto",
            "valor_final",
            "pagamento_status",
            "forma_pagamento",
            "criada_em",
            "ingressos",
        ]
