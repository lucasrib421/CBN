from django.contrib import admin

from content.models import Category, Post, Status, Tag

admin.site.register(Status)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Post)
