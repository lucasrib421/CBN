from __future__ import annotations

import hashlib
import json

from django.core.cache import cache


CACHE_TTLS = {
    'posts_list': 60,
    'post_detail': 300,
    'categories': 3600,
    'tags': 3600,
    'home': 120,
    'menus': 3600,
    'redirects': 3600,
}


def build_cache_key(prefix: str, full_path: str) -> str:
    digest = hashlib.md5(full_path.encode('utf-8')).hexdigest()
    return f'api-cache:{prefix}:{digest}'


def set_cache_headers(response, max_age: int) -> None:
    response['Cache-Control'] = f'public, max-age={max_age}'
    # Compute ETag from response.data (dict/list) rather than rendered content,
    # because DRF Response objects may not have an accepted_renderer yet when
    # returning cached data directly via Response(cached_dict).
    data = getattr(response, 'data', b'')
    try:
        raw = json.dumps(data, sort_keys=True, default=str).encode('utf-8')
    except (TypeError, ValueError):
        raw = str(data).encode('utf-8')
    response['ETag'] = f'"{hashlib.md5(raw).hexdigest()}"'


def invalidate_prefixes(prefixes: list[str]) -> None:
    for prefix in prefixes:
        pattern = f'*api-cache:{prefix}:*'
        try:
            cache.delete_pattern(pattern)
        except Exception:
            cache.clear()
