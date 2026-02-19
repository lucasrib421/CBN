from django.db import models


class MediaType(models.TextChoices):
    IMAGE = 'IMAGE', 'Imagem'
    VIDEO = 'VIDEO', 'Video'
    AUDIO = 'AUDIO', 'Audio'
    DOCUMENT = 'DOCUMENT', 'Documento'


class Media(models.Model):
    file = models.FileField(upload_to='media/')
    title = models.CharField(max_length=200, null=False, blank=False)
    alt_text = models.CharField(max_length=150, null=True, blank=True)
    image_type = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        choices=MediaType.choices,
        default=MediaType.IMAGE,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        db_table = 'media'
        verbose_name_plural = 'Mídias'

    def __str__(self):
        return self.title
