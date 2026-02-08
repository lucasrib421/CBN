"""
Django settings for core project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# --- SEGURANÇA: Configurações Dinâmicas ---

# Lê do .env. Se não achar, usa a chave insegura (apenas para desenvolvimento local)
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-chave-padrao-local-apenas')

# Lê do .env. Em produção será 'False', localmente será 'True'
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Lê a lista de domínios permitidos do .env separada por vírgula
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


def _split_env_list(var_name):
    value = os.getenv(var_name, '')
    return [item.strip() for item in value.split(',') if item.strip()]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party apps
    'rest_framework',
    'django_filters',
    'corsheaders',
    'drf_spectacular',
    # Local apps
    'homeNews',
    'painelControle',
    'setup',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Arquivos estáticos
    'corsheaders.middleware.CorsMiddleware',  # CORS vem antes de tudo possível
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'  # Certifique-se que sua pasta principal se chama 'core' mesmo

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'news_local_db'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'pt-br'  # Mudei para Português
TIME_ZONE = 'America/Sao_Paulo'  # Mudei para Horário de Brasília
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media Files (Uploads de imagens)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# --- CONFIGURAÇÃO DE DOMÍNIO E CORS ---

# Se DEBUG for True (Local), libera tudo. Se for False (Prod), restringe.
CORS_ALLOW_ALL_ORIGINS = DEBUG
if not DEBUG:
    CORS_ALLOWED_ORIGINS = _split_env_list('CORS_ALLOWED_ORIGINS')

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',  # Por padrão é aberto, fechamos nas Views específicas
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

# CSRF: Permite que o painel admin funcione através do seu domínio HTTPS
CSRF_TRUSTED_ORIGINS = _split_env_list('CSRF_TRUSTED_ORIGINS')

SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'ALGORITHM': 'RS256',  # <--- MUDAMOS PARA RS256 (Padrão do Keycloak)
    # URL onde o Django vai buscar a Chave Pública do Keycloak para validar a assinatura
    'JWK_URL': os.getenv(
        'JWT_JWK_URL',
        'http://keycloak:8080/realms/cbn/protocol/openid-connect/certs',
    ),
    # Mapeamento de Usuário:
    # O Keycloak manda o login no campo 'preferred_username'.
    # O Django deve usar isso para buscar no campo 'username' do banco local.
    'USER_ID_FIELD': 'username',
    'USER_ID_CLAIM': 'preferred_username',
    'AUTH_HEADER_TYPES': ('Bearer',),
    # O Keycloak geralmente coloca 'account' no audience, mas às vezes vem vazio.
    # Se der erro de "Audience", deixe como None por enquanto.
    'AUDIENCE': 'account',
    'ISSUER': os.getenv(
        'JWT_ISSUER'
    ),  # Ignora validação estrita de URL (evita erro Docker vs Localhost)
}
