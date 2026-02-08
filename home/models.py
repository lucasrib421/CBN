from django.db import models


class HomeSection(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False)
    section_type = models.CharField(max_length=50, null=False, blank=False)
    order = models.IntegerField(null=False, blank=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        db_table = 'home_section'

    def __str__(self):
        return self.title


class HomeSectionItem(models.Model):
    section = models.ForeignKey('home.HomeSection', on_delete=models.CASCADE, null=False, blank=False)
    post = models.ForeignKey('content.Post', on_delete=models.CASCADE, null=False, blank=False)
    order = models.IntegerField(null=False, blank=False)

    class Meta:
        ordering = ['order']
        db_table = 'home_section_item'

    def __str__(self):
        return f'{self.section.title} - {self.post.title}'
