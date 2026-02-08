from django.contrib import admin

from accounts.models import Author, Role

admin.site.register(Role)
admin.site.register(Author)
