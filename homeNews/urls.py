from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "homeNews"

router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')
router.register(r'categories', views.CategoryViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'home', views.HomeViewSet, basename='home')
router.register(r'menus', views.MenuViewSet, basename='menu')
router.register(r'redirects', views.RedirectViewSet, basename='redirect')

urlpatterns = [
    path('', include(router.urls)),
]
