from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParcaViewSet
from .views import UcakViewSet

router = DefaultRouter()
router.register(r'parcalar', ParcaViewSet)
router.register(r'ucaklar', UcakViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
