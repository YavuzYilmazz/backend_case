from rest_framework import viewsets
from .models import Parca
from .serializers import ParcaSerializer
from .models import Ucak
from .serializers import UcakSerializer

class ParcaViewSet(viewsets.ModelViewSet):
    queryset = Parca.objects.all()
    serializer_class = ParcaSerializer

class UcakViewSet(viewsets.ModelViewSet):
    queryset = Ucak.objects.all()
    serializer_class = UcakSerializer

