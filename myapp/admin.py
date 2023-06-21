from django.contrib import admin
from .models import Downloads, Events, Gates

class DownloadsAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'gate_app')

class EventsAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'user_id','event_name')

class GatesAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'title')

admin.site.register(Downloads, DownloadsAdmin)
admin.site.register(Events, EventsAdmin)
admin.site.register(Gates, GatesAdmin)



