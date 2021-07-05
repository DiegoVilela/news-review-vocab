from django.contrib import admin

from .models import Entry, Episode


class EntryInLine(admin.TabularInline):
    model = Entry
    extra = 3
    max_num = 3
    fields = ('term', 'meaning')


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('term',)}


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'headline', 'video', 'date')
    list_filter = ('date',)
    prepopulated_fields = {'slug': ('headline',)}
    inlines = (EntryInLine,)
