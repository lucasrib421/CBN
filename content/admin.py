from django.contrib import admin

from content.models import Category, Post, PostStatusTransition, Tag


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'published_at', 'created_at')
    list_filter = ('status', 'categories')
    search_fields = ('title', 'subtitle', 'content')
    readonly_fields = ('created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('categories', 'tags')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(PostStatusTransition)
class PostStatusTransitionAdmin(admin.ModelAdmin):
    list_display = ('post', 'from_status', 'to_status', 'changed_by', 'actor_role', 'changed_at')
    list_filter = ('from_status', 'to_status', 'actor_role')
    search_fields = ('post__title', 'changed_by__username')
    readonly_fields = (
        'post',
        'from_status',
        'to_status',
        'changed_by',
        'actor_role',
        'changed_at',
        'published_at_snapshot',
    )
