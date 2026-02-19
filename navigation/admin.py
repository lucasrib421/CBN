from django.contrib import admin

from navigation.models import Menu, MenuItem, Redirect


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    fk_name = 'menu'
    extra = 1


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'slug')
    inlines = [MenuItemInline]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('label', 'menu', 'parent', 'order', 'target', 'is_active')
    list_filter = ('menu', 'is_active')
    search_fields = ('label', 'url')


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ('old_path', 'new_path', 'url_type', 'is_active')
    list_filter = ('url_type', 'is_active')
    search_fields = ('old_path', 'new_path')
