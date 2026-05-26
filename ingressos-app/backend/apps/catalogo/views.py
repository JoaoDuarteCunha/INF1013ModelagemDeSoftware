from rest_framework.viewsets import ModelViewSet
from .models import Filme
from .serializers import FilmeSerializer


class FilmeViewSet(ModelViewSet):
    queryset = Filme.objects.all()
    serializer_class = FilmeSerializer
