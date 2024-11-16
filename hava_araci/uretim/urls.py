from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParcaViewSet

router = DefaultRouter()
router.register(r'parcalar', ParcaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
