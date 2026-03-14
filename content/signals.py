import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import Post, PostStatus

logger = logging.getLogger(__name__)

def get_retry_session():
    """Configura uma sessão HTTP com política de retry automático e backoff."""
    session = requests.Session()
    
    # Configuração do Retry:
    # total=2: Tenta a original + 2 retries (Total de 3 tentativas)
    # backoff_factor=0.3: Espera 0s (1ª), 0.3s (2ª) e 0.6s (3ª tentativa) para não travar o admin
    # status_forcelist: Só repete se o Next.js estiver fora do ar ou engasgado (erros 5xx)
    retry_strategy = Retry(
        total=2,
        backoff_factor=0.3,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["POST"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def revalidate_nextjs_cache(slug):
    """Envia um POST para o webhook do Next.js usando uma sessão com Retry."""
    if not getattr(settings, 'REVALIDATION_SECRET', None) or not getattr(settings, 'NEXTJS_URL', None):
        logger.warning(f"Credenciais do Next.js ausentes. Cache não revalidado para: {slug}")
        return

    url = f"{settings.NEXTJS_URL}/api/revalidate"
    headers = {"x-reval-secret": settings.REVALIDATION_SECRET}
    payload = {"tags": [f"post-{slug}"]}

    # Criamos a sessão blindada com as nossas regras de Retry
    session = get_retry_session()

    try:
        # Timeout de 2.0s se aplica a CADA tentativa. 
        # No pior cenário (3 falhas seguidas), o admin do Django demora no máximo uns 6s.
        response = session.post(url, json=payload, headers=headers, timeout=2.0)
        response.raise_for_status()
        logger.info(f"Cache revalidado com sucesso no Next.js para o post: {slug}")
        
    except requests.exceptions.RequestException as e:
        # Se esgotar todos os retries ou der erro de conexão persistente, falha silenciosamente
        logger.error(f"Falha definitiva ao revalidar cache do Next.js para {slug} após tentativas: {str(e)}")


@receiver(post_save, sender=Post)
def trigger_revalidation_on_save(sender, instance, created, **kwargs):
    if created and instance.status == PostStatus.DRAFT:
        return
    revalidate_nextjs_cache(instance.slug)


@receiver(post_delete, sender=Post)
def trigger_revalidation_on_delete(sender, instance, **kwargs):
    revalidate_nextjs_cache(instance.slug)