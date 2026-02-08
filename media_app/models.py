from django.db import models


class Media(models.Model):
    file = models.FileField(upload_to='media/')
    title = models.CharField(max_length=200, null=False, blank=False)
    alt_text = models.CharField(max_length=150, null=True, blank=True)
    image_type = models.CharField(max_length=50, null=False, blank=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        db_table = 'media'

    def __str__(self):
        return self.title
