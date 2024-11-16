from rest_framework import viewsets
from .models import Parca
from .serializers import ParcaSerializer

class ParcaViewSet(viewsets.ModelViewSet):
    queryset = Parca.objects.all()
    serializer_class = ParcaSerializer
