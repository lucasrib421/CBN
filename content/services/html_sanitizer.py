from __future__ import annotations

import re
from typing import Protocol

import bleach

from content.services.html_policy import (
    DEFAULT_HTML_SANITIZATION_POLICY,
    HtmlSanitizationPolicy,
)


class HtmlSanitizer(Protocol):
    def sanitize(self, raw_html: str) -> str:
        ...


class BleachHtmlSanitizer:
    def __init__(self, policy: HtmlSanitizationPolicy = DEFAULT_HTML_SANITIZATION_POLICY) -> None:
        self._policy = policy

    def sanitize(self, raw_html: str) -> str:
        content_without_blocked_tags = re.sub(
            r'<(script|style)\b[^<]*(?:(?!<\/\1>)<[^<]*)*<\/\1>',
            '',
            raw_html or '',
            flags=re.IGNORECASE | re.DOTALL,
        )
        return bleach.clean(
            content_without_blocked_tags,
            tags=list(self._policy.allowed_tags),
            attributes={tag: list(attrs) for tag, attrs in self._policy.allowed_attributes.items()},
            protocols=list(self._policy.allowed_protocols),
            strip=True,
            strip_comments=True,
        )
