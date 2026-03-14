from django.apps import AppConfig


class ContentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'content'

    def ready(self):
        # Quando o app iniciar, os signals começam a vigiar o modelo Post
        import content.signals
