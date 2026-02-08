from django.db import models


class Menu(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False)
    slug = models.SlugField(max_length=100, unique=True, null=False, blank=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']
        db_table = 'menu'

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    menu = models.ForeignKey('navigation.Menu', on_delete=models.CASCADE, null=False, blank=False)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children'
    )
    label = models.CharField(max_length=100, null=False, blank=False)
    url = models.CharField(max_length=200, null=False, blank=False)
    order = models.IntegerField(null=False, blank=False)
    target = models.CharField(max_length=20, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        db_table = 'menu_item'

    def __str__(self):
        return f'{self.menu.title} - {self.label}'


class Redirect(models.Model):
    old_path = models.CharField(max_length=200, unique=True, null=False, blank=False)
    new_path = models.CharField(max_length=200, null=False, blank=False)
    url_type = models.CharField(max_length=20, null=False, blank=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-id']
        db_table = 'redirect'

    def __str__(self):
        return self.old_path
