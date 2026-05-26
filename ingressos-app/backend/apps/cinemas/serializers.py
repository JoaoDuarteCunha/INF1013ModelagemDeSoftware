from rest_framework import serializers
from .models import Cinema, Sala


class CinemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cinema
        fields = "__all__"


class SalaSerializer(serializers.ModelSerializer):
    cinema_nome = serializers.CharField(source="cinema.nome", read_only=True)

    class Meta:
        model = Sala
        fields = "__all__"
