from django.contrib import admin
from .models import (
    Media, Status, Category, Tag, Role, Author, Post, 
    HomeSection, HomeSectionItem, Menu, MenuItem, Redirect, HomeConfig
)

# Configuração básica para mostrar tudo no painel
admin.site.register(Media)
admin.site.register(Status)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Role)
admin.site.register(Author)
admin.site.register(Post)
admin.site.register(HomeSection)
admin.site.register(HomeSectionItem)
admin.site.register(Menu)
admin.site.register(MenuItem)
admin.site.register(Redirect)
admin.site.register(HomeConfig)