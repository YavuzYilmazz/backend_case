from rest_framework import serializers
from .models import Parca
from .models import Ucak
from .models import Takim
from .models import Personel

class ParcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parca
        fields = ['id', 'tip', 'stok_adedi', 'ucak_tipi']



class UcakSerializer(serializers.ModelSerializer):
    parcalar = ParcaSerializer(many=True)
    class Meta:
        model = Ucak
        fields = ['id', 'isim', 'stok_adedi', 'parcalar']



class TakimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Takim
        fields = '__all__'


class PersonelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personel
        fields = '__all__'
