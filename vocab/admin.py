from django.contrib import admin

from .models import Entry, Episode


class EntryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('term',)}


class EpisodeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('headline',)}


admin.site.register(Entry, EntryAdmin)
admin.site.register(Episode, EpisodeAdmin)
