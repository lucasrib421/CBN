from django.contrib import admin

from home.models import HomeSection, HomeSectionItem


class HomeSectionItemInline(admin.TabularInline):
    model = HomeSectionItem
    extra = 1


@admin.register(HomeSection)
class HomeSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'section_type', 'order', 'is_active')
    list_filter = ('section_type', 'is_active')
    search_fields = ('title',)
    inlines = [HomeSectionItemInline]


@admin.register(HomeSectionItem)
class HomeSectionItemAdmin(admin.ModelAdmin):
    list_display = ('section', 'post', 'order')
    list_filter = ('section',)
