from rest_framework import serializers
from .models import Sessao, AssentoSessao


class SessaoSerializer(serializers.ModelSerializer):
    filme_nome = serializers.CharField(source="filme.nome", read_only=True)
    sala_nome = serializers.CharField(source="sala.nome", read_only=True)
    cinema_nome = serializers.CharField(source="sala.cinema.nome", read_only=True)

    class Meta:
        model = Sessao
        fields = "__all__"


class AssentoSessaoSerializer(serializers.ModelSerializer):
    assento_label = serializers.SerializerMethodField()

    class Meta:
        model = AssentoSessao
        fields = "__all__"

    def get_assento_label(self, obj):
        return f"{obj.assento.fila}{obj.assento.numero}"
