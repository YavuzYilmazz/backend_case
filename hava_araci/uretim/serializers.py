from rest_framework import serializers
from .models import Parca

class ParcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parca
        fields = '__all__'
