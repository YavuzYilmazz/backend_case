from rest_framework import serializers
from .models import Parca
from .models import Ucak

class ParcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parca
        fields = '__all__'


class UcakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ucak
        fields = '__all__'