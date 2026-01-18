from django.db import models

# Create your models here.

class Media(models.Model):
    file = models.FileField(upload_to='media/')
    title = models.CharField(max_length=200, null=False, blank=False)
    alt_text = models.CharField(max_length=150, null=True, blank=True)
    image_type = models.CharField(max_length=50, null=False, blank=False)  # Ex: "image", "video", etc.
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        db_table = "media"

    def __str__(self):
        return self.title

class Status(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)

    class Meta:
        ordering = ['name']
        db_table = "status"

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    slug = models.SlugField(max_length=100, unique=True, null=False, blank=False)
    color = models.CharField(max_length=7, null=True)  # Hex color code
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        db_table = "category"

    def __str__(self):
        return self.name
    
class Tag(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    slug = models.SlugField(max_length=100, unique=True, null=False, blank=False)

    class Meta:
        ordering = ['name']
        db_table = "tag"

    def __str__(self):
        return self.name

# 1. Nova Tabela de Cargos
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Ex: "Editor Chefe"
    slug = models.SlugField(unique=True)                 # Ex: "editor-chefe" (usado para checagem no código)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "role"
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"

    def __str__(self):
        return self.name

class Author(models.Model):
    # Usamos o user_uuid como chave primária se a ideia for usar EXATAMENTE o ID do Keycloak aqui.
    # Se for isso, lembre-se: você precisará fornecer esse ID na hora de salvar, o Django não vai gerar.
    id = models.UUIDField(
        primary_key=True, 
        editable=False, 
        null=False, 
        blank=False
        )

    # Campo para vincular ao Keycloak (separado do ID interno é mais seguro, mas pode usar o ID se preferir)
    keycloak_id = models.UUIDField(unique=True, null=True, blank=True)

    name = models.CharField(max_length=150, null=False, blank=False)
    bio = models.TextField(null=True, blank=True)
    avatar = models.ForeignKey(
        Media, 
        on_delete=models.SET_NULL, # Se apagar a mídia, o post fica sem foto (não é excluído)
        null=True, 
        blank=True,
        related_name='author_avatars' # Permite saber quais posts usam essa imagem
    )

    role = models.ForeignKey(Role, 
        on_delete=models.PROTECT, 
        null=True, blank=True
        )

    managed_categories = models.ManyToManyField(Category, blank=True)

    class Meta:
        ordering = ['name']
        db_table = "author"

    def __str__(self):
        return self.name
    
class Post(models.Model):
    title = models.CharField(max_length=200, null=False, blank=False)
    subtitle = models.CharField(max_length=300, null=True, blank=True)
    slug = models.SlugField(max_length=100, unique=True, null=False, blank=False) 
    content = models.TextField(null=False, blank=False)

    cover_image = models.ForeignKey(
        Media, 
        on_delete=models.SET_NULL, # Se apagar a mídia, o post fica sem foto (não é excluído)
        null=True, 
        blank=True,
        related_name='posts_using_image' # Permite saber quais posts usam essa imagem
    )

    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=False, blank=False)
    categories = models.ManyToManyField(Category, blank=False)
    tags = models.ManyToManyField(Tag, blank=True)

    status = models.ForeignKey(Status, on_delete=models.PROTECT, null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']
        db_table = "post"

    def __str__(self):
        return self.title
    
class HomeSection(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False)
    section_type = models.CharField(max_length=50, null=False, blank=False)  # Ex: "carrossel", "destaques", etc.
    order = models.IntegerField(null=False, blank=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        db_table = "home_section"

    def __str__(self):
        return self.title

class HomeSectionItem(models.Model):
    section = models.ForeignKey(HomeSection, on_delete=models.CASCADE, null=False, blank=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=False, blank=False)
    order = models.IntegerField(null=False, blank=False)

    class Meta:
        ordering = ['order']
        db_table = "home_section_item"

    def __str__(self):
        return f"{self.section.title} - {self.post.title}"

class Menu(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False)
    slug = models.SlugField(max_length=100, unique=True, null=False, blank=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']
        db_table = "menu"

    def __str__(self):
        return self.title

class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=False, blank=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    label = models.CharField(max_length=100, null=False, blank=False)
    url = models.CharField(max_length=200, null=False, blank=False)
    order = models.IntegerField(null=False, blank=False)
    target = models.CharField(max_length=20, null=True, blank=True)  # Ex: "_blank", "_self"
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        db_table = "menu_item"

    def __str__(self):
        return f"{self.menu.title} - {self.label}"

class Redirect(models.Model):
    old_path = models.CharField(max_length=200, unique=True, null=False, blank=False)
    new_path = models.CharField(max_length=200, null=False, blank=False)
    url_type = models.CharField(max_length=20, null=False, blank=False)  # Ex: "permanent", "temporary"
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-id']
        db_table = "redirect"

    def __str__(self):
        return self.old_path