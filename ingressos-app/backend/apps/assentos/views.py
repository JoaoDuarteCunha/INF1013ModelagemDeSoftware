from rest_framework.viewsets import ModelViewSet
from .models import Assento
from .serializers import AssentoSerializer


class AssentoViewSet(ModelViewSet):
    queryset = Assento.objects.select_related("sala").all()
    serializer_class = AssentoSerializer
