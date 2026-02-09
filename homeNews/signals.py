from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from content.models import Category, Post
from home.models import HomeSection, HomeSectionItem
from navigation.models import Menu, MenuItem

from homeNews.cache_utils import invalidate_prefixes


@receiver([post_save, post_delete], sender=Post)
def invalidate_post_related_cache(**kwargs):
    invalidate_prefixes(['posts-list', 'post-detail', 'home'])


@receiver([post_save, post_delete], sender=Category)
def invalidate_category_cache(**kwargs):
    invalidate_prefixes(['categories'])


@receiver([post_save, post_delete], sender=HomeSection)
@receiver([post_save, post_delete], sender=HomeSectionItem)
def invalidate_home_cache(**kwargs):
    invalidate_prefixes(['home'])


@receiver([post_save, post_delete], sender=Menu)
@receiver([post_save, post_delete], sender=MenuItem)
def invalidate_menu_cache(**kwargs):
    invalidate_prefixes(['menus'])
