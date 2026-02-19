from django.apps import AppConfig


class HomenewsConfig(AppConfig):
    name = 'homeNews'

    def ready(self):
        import homeNews.signals  # noqa: F401
