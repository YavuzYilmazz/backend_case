from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParcaViewSet
from .views import UcakViewSet
from .views import TakimViewSet
from .views import PersonelViewSet

router = DefaultRouter()
router.register(r'parcalar', ParcaViewSet)
router.register(r'ucaklar', UcakViewSet)
router.register(r'takimlar', TakimViewSet)
router.register(r'personeller', PersonelViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
