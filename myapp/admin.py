from django.contrib import admin
from .models import Downloads

class DownloadsAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'gate_app')

admin.site.register(Downloads, DownloadsAdmin)



