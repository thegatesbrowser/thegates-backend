from django.contrib import admin
from django.db import models
from .models import (
    Downloads,
    Events,
    Gates,
    FeaturedGates,
    PublishingProject,
    SearchSuggestions,
    TelegramBotUser,
    Users,
)

class DownloadsAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'gate_app')

class EventsAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'user_id','event_name')

class GatesAdmin(admin.ModelAdmin):
    list_display = ('number_of_entries', 'id', 'title', 'description', 'url')
    actions = ['copy_to_featured']

    def copy_to_featured(self, request, queryset):
        created_count = 0
        updated_count = 0

        # place new items at the end by default
        max_order = FeaturedGates.objects.aggregate(models.Max('sort_order'))['sort_order__max'] or 0
        next_order = max_order + 1

        for gate in queryset:
            featured, created = FeaturedGates.objects.get_or_create(
                url=gate.url,
                defaults={
                    'title': gate.title,
                    'description': gate.description,
                    'icon': gate.icon,
                    'is_special': False,
                    'sort_order': next_order,
                },
            )

            if created:
                created_count += 1
                next_order += 1
            else:
                # if it already exists, update fields but keep its ordering
                featured.title = gate.title
                featured.description = gate.description
                featured.icon = gate.icon
                featured.save(update_fields=['title', 'description', 'icon'])
                updated_count += 1

        self.message_user(
            request,
            f"Copied {created_count} gate(s) and updated {updated_count} existing featured gate(s).",
        )

    copy_to_featured.short_description = 'Copy to Featured gates'

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


class PublishingProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'project_id', 'token', 'published_url', 'updated_at')
    search_fields = ('project_id', 'token', 'published_url')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)

admin.site.register(Downloads, DownloadsAdmin)
admin.site.register(Events, EventsAdmin)
admin.site.register(Gates, GatesAdmin)
admin.site.register(FeaturedGates, FeaturedGatesAdmin)
admin.site.register(Users, UsersAdmin)
admin.site.register(SearchSuggestions, SearchSuggestionsAdmin)
admin.site.register(TelegramBotUser, TelegramBotUserAdmin)
admin.site.register(PublishingProject, PublishingProjectAdmin)
