from django.db import models
from django.contrib.auth.models import AbstractUser

class Personel(AbstractUser):
    TAKIM_TIPLERI = [
        ('KANAT', 'Kanat Takımı'),
        ('GOVDE', 'Gövde Takımı'),
        ('KUYRUK', 'Kuyruk Takımı'),
        ('AVIYONIK', 'Aviyonik Takımı'),
        ('MONTAJ', 'Montaj Takımı'),
    ]

    takim_tipi = models.CharField(max_length=20, choices=TAKIM_TIPLERI, null=True, blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='personel_groups',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='personel_permissions',
        blank=True,
    )

    def __str__(self):
        return self.username


class Parca(models.Model):
    PARCA_TIPLERI = [
        ('KANAT', 'Kanat'),
        ('GOVDE', 'Gövde'),
        ('KUYRUK', 'Kuyruk'),
        ('AVIYONIK', 'Aviyonik'),
    ]

    tip = models.CharField(max_length=10, choices=PARCA_TIPLERI, null=True, blank=True)
    stok_adedi = models.IntegerField(default=0, null=True, blank=True)
    ucak_tipi = models.CharField(
        max_length=20,
        choices=[
            ('TB2', 'TB2'),
            ('TB3', 'TB3'),
            ('AKINCI', 'Akıncı'),
            ('KIZILELMA', 'Kızılelma'),
        ],
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.isim} ({self.tip})"


class Ucak(models.Model):
    UCUS_TIPLERI = [
        ('TB2', 'TB2'),
        ('TB3', 'TB3'),
        ('AKINCI', 'Akıncı'),
        ('KIZILELMA', 'Kızılelma'),
    ]

    isim = models.CharField(max_length=20, choices=UCUS_TIPLERI, null=True, blank=True)
    parcalar = models.ManyToManyField(Parca, through='UcakParca', blank=True)
    stok_adedi = models.IntegerField(default=0, null=True, blank=True)

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

    isim = models.CharField(max_length=20, choices=TAKIM_TIPLERI, null=True, blank=True)
    sorumlu_personel = models.ManyToManyField(Personel, related_name="takimlar", blank=True)
    sorumlu_parca_tipi = models.CharField(max_length=10, choices=[
        ('KANAT', 'Kanat'),
        ('GOVDE', 'Gövde'),
        ('KUYRUK', 'Kuyruk'),
        ('AVIYONIK', 'Aviyonik'),
    ], null=True, blank=True)

    def __str__(self):
        return self.isim


class UcakParca(models.Model):
    ucak = models.ForeignKey(Ucak, on_delete=models.CASCADE, null=True, blank=True)
    parca = models.ForeignKey(Parca, on_delete=models.CASCADE, null=True, blank=True)
    adet = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.ucak} -> {self.parca} ({self.adet})"
