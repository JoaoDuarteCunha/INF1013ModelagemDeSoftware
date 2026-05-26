from rest_framework.viewsets import ModelViewSet
from .models import Cinema, Sala
from .serializers import CinemaSerializer, SalaSerializer


class CinemaViewSet(ModelViewSet):
    queryset = Cinema.objects.all()
    serializer_class = CinemaSerializer


class SalaViewSet(ModelViewSet):
    queryset = Sala.objects.select_related("cinema").all()
    serializer_class = SalaSerializer
