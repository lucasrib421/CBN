from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # 1. Rota do Painel Administrativo (Django Admin)
    path('admin/', admin.site.urls),
    # 2. Compatibilidade da API legada
    path('api/', include('homeNews.urls')),

    # 2.1 API versionada (v1)
    path('api/v1/', include(('homeNews.urls', 'homeNews'), namespace='v1')),

    # 2.2 Rotas legadas do painel
    path('api/painel/', include('painelControle.urls')),

    # 2.3 API versionada do painel
    path('api/v1/painel/', include(('painelControle.urls', 'painelControle'), namespace='painel-v1')),
    # 3. Rota do App Setup (Se você for usar algo de lá, senão é opcional)
    path('setup-rotas/', include('setup.urls')),
    # 4. Documentação da API (drf-spectacular)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'
    ),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
