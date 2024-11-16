from rest_framework import serializers
from .models import Parca
from .models import Ucak
from .models import Takim
from .models import Personel

class ParcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parca
        fields = '__all__'


class UcakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ucak
        fields = '__all__'


class TakimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Takim
        fields = '__all__'


class PersonelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personel
        fields = '__all__'
