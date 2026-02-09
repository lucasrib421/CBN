from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    HomeSectionItemViewSet,
    HomeSectionViewSet,
    MediaViewSet,
    MenuItemViewSet,
    MenuViewSet,
    PostViewSet,
    TagViewSet,
)

app_name = 'painelControle'

router = DefaultRouter()
router.register(r'media', MediaViewSet, basename='media')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'posts', PostViewSet, basename='post')
router.register(r'home-sections', HomeSectionViewSet, basename='home-section')
router.register(r'home-section-items', HomeSectionItemViewSet, basename='home-section-item')
router.register(r'menus', MenuViewSet, basename='menu')
router.register(r'menu-items', MenuItemViewSet, basename='menu-item')

urlpatterns = [
    path('', include(router.urls)),
]
