from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from content.services.html_sanitizer import BleachHtmlSanitizer, HtmlSanitizer
from content.services.plain_text_extractor import HtmlPlainTextExtractor, PlainTextExtractor
from content.services.reading_time_calculator import (
    ReadingTimeCalculator,
    WordCountReadingTimeCalculator,
)


@dataclass(frozen=True)
class ProcessedPostContent:
    sanitized_html: str
    plain_text: str
    reading_time: int | None


class PostContentPipeline:
    def __init__(
        self,
        sanitizer: HtmlSanitizer,
        plain_text_extractor: PlainTextExtractor,
        reading_time_calculator: ReadingTimeCalculator,
    ) -> None:
        self._sanitizer = sanitizer
        self._plain_text_extractor = plain_text_extractor
        self._reading_time_calculator = reading_time_calculator

    def process(self, raw_html: str) -> ProcessedPostContent:
        sanitized_html = self._sanitizer.sanitize(raw_html or '')
        plain_text = self._plain_text_extractor.extract(sanitized_html)
        reading_time = self._reading_time_calculator.calculate_minutes(plain_text)
        return ProcessedPostContent(
            sanitized_html=sanitized_html,
            plain_text=plain_text,
            reading_time=reading_time,
        )


@lru_cache(maxsize=1)
def get_default_post_content_pipeline() -> PostContentPipeline:
    return PostContentPipeline(
        sanitizer=BleachHtmlSanitizer(),
        plain_text_extractor=HtmlPlainTextExtractor(),
        reading_time_calculator=WordCountReadingTimeCalculator(),
    )

