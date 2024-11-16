from django.db import models

class Parca(models.Model):
    PARCA_TIPLERI = [
        ('KANAT', 'Kanat'),
        ('GOVDE', 'Gövde'),
        ('KUYRUK', 'Kuyruk'),
        ('AVIYONIK', 'Aviyonik'),
    ]

    isim = models.CharField(max_length=50)
    tip = models.CharField(max_length=10, choices=PARCA_TIPLERI)
    stok_adedi = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.isim} ({self.tip})"


class Ucak(models.Model):
    UCUS_TIPLERI = [
        ('TB2', 'TB2'),
        ('TB3', 'TB3'),
        ('AKINCI', 'Akıncı'),
        ('KIZILELMA', 'Kızılelma'),
    ]

    isim = models.CharField(max_length=20, choices=UCUS_TIPLERI)
    parcalar = models.ManyToManyField(Parca, through='UcakParca')

    def __str__(self):
        return self.isim


class Takim(models.Model):
    TAKIM_TIPLERI = [
        ('KANAT', 'Kanat Takımı'),
        ('GOVDE', 'Gövde Takımı'),
        ('KUYRUK', 'Kuyruk Takımı'),
        ('AVIYONIK', 'Aviyonik Takımı'),
        ('MONTAJ', 'Montaj Takımı'),
    ]

    isim = models.CharField(max_length=20, choices=TAKIM_TIPLERI)
    sorumlu_parca = models.ForeignKey(Parca, on_delete=models.CASCADE, related_name="sorumlu_takim")

    def __str__(self):
        return self.isim


class Personel(models.Model):
    isim = models.CharField(max_length=50)
    takim = models.ForeignKey(Takim, on_delete=models.CASCADE, related_name="personeller")

    def __str__(self):
        return self.isim


class UcakParca(models.Model):
    ucak = models.ForeignKey(Ucak, on_delete=models.CASCADE)
    parca = models.ForeignKey(Parca, on_delete=models.CASCADE)
    adet = models.IntegerField()

    def __str__(self):
        return f"{self.ucak} -> {self.parca} ({self.adet})"

