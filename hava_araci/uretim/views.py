from rest_framework import viewsets
from .models import Parca
from .serializers import ParcaSerializer
from .models import Ucak
from .serializers import UcakSerializer
from .models import Takim
from .serializers import TakimSerializer
from .models import Personel
from .serializers import PersonelSerializer

class ParcaViewSet(viewsets.ModelViewSet):
    queryset = Parca.objects.all()
    serializer_class = ParcaSerializer

class UcakViewSet(viewsets.ModelViewSet):
    queryset = Ucak.objects.all()
    serializer_class = UcakSerializer

class TakimViewSet(viewsets.ModelViewSet):
    queryset = Takim.objects.all()
    serializer_class = TakimSerializer

class PersonelViewSet(viewsets.ModelViewSet):
    queryset = Personel.objects.all()
    serializer_class = PersonelSerializer

