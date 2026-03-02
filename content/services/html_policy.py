from dataclasses import dataclass


@dataclass(frozen=True)
class HtmlSanitizationPolicy:
    allowed_tags: tuple[str, ...]
    allowed_attributes: dict[str, tuple[str, ...]]
    allowed_protocols: tuple[str, ...]


DEFAULT_HTML_SANITIZATION_POLICY = HtmlSanitizationPolicy(
    allowed_tags=(
        'p',
        'h2',
        'h3',
        'strong',
        'em',
        'ul',
        'ol',
        'li',
        'blockquote',
        'a',
        'hr',
        'figure',
        'img',
        'figcaption',
        'br',
    ),
    allowed_attributes={
        'a': ('href', 'target', 'rel'),
        'img': ('src', 'alt'),
    },
    allowed_protocols=('http', 'https', 'mailto'),
)

