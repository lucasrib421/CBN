from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Protocol


class PlainTextExtractor(Protocol):
    def extract(self, html: str) -> str:
        ...


class _PlainTextHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._chunks: list[str] = []

    def handle_data(self, data: str) -> None:
        if data:
            self._chunks.append(data)

    def get_text(self) -> str:
        combined = ' '.join(self._chunks)
        return re.sub(r'\s+', ' ', combined).strip()


class HtmlPlainTextExtractor:
    def extract(self, html: str) -> str:
        parser = _PlainTextHtmlParser()
        parser.feed(html or '')
        parser.close()
        return parser.get_text()

