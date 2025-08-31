from django.contrib import admin
from .models import Downloads, Events, Gates, FeaturedGates, Users, SearchSuggestions, TelegramBotUser

class DownloadsAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'gate_app')

class EventsAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'user_id','event_name')

class GatesAdmin(admin.ModelAdmin):
    list_display = ('number_of_entries', 'id', 'title', 'description', 'url')

class FeaturedGatesAdmin(admin.ModelAdmin):
    list_display = ('sort_order', 'id', 'title', 'description', 'url', 'icon', 'is_special')
    list_editable = ('sort_order',)
    list_display_links = ('id', 'title')
    ordering = ('sort_order', 'id')

class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'device_id', 'name', 'email', 'country', 'city')
    search_fields = ('user_id', 'device_id')

class SearchSuggestionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'query')

class TelegramBotUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'description', 'is_ignore')

admin.site.register(Downloads, DownloadsAdmin)
admin.site.register(Events, EventsAdmin)
admin.site.register(Gates, GatesAdmin)
admin.site.register(FeaturedGates, FeaturedGatesAdmin)
admin.site.register(Users, UsersAdmin)
admin.site.register(SearchSuggestions, SearchSuggestionsAdmin)
admin.site.register(TelegramBotUser, TelegramBotUserAdmin)
