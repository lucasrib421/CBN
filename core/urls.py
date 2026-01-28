from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 1. Rota do Painel Administrativo (Django Admin)
    path('admin/', admin.site.urls),
    
    # 2. Rota PRINCIPAL da API (Tudo do homeNews entra aqui)
    # Ex: localhost:8000/api/posts/
    path('api/', include('homeNews.urls')),

    # 3. Rota do App Setup (Se você for usar algo de lá, senão é opcional)
    path('setup-rotas/', include('setup.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)