from django.contrib import admin

from navigation.models import Menu, MenuItem, Redirect

admin.site.register(Menu)
admin.site.register(MenuItem)
admin.site.register(Redirect)
