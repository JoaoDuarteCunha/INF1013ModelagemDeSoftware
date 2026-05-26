from rest_framework import serializers
from .models import Assento


class AssentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assento
        fields = "__all__"
