from django.contrib import admin
from .models import Downloads, Events, Gates, FeaturedGates, Users, SearchSuggestions, TelegramBotUser

class DownloadsAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'gate_app')

class EventsAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'user_id','event_name')

class GatesAdmin(admin.ModelAdmin):
    list_display = ('number_of_entries', 'id', 'title', 'description', 'url')

class FeaturedGatesAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'url', 'icon')

class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'name', 'email', 'country', 'city')

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
