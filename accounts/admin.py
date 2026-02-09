from django.contrib import admin

from accounts.models import Author, Role


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'user')
    list_filter = ('role',)
    search_fields = ('name', 'bio')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
