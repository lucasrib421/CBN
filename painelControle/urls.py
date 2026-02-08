from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MediaViewSet

app_name = "painelControle"

router = DefaultRouter()
router.register(r"media", MediaViewSet, basename="media")

urlpatterns = [
    path("", include(router.urls)),
]
