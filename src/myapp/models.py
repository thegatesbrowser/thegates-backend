from django.db import models
from django.utils import timezone


class Downloads(models.Model):
    date = models.DateTimeField(default=timezone.now)
    gate_app = models.CharField(max_length=50)
    # данные пользователя
    ip_address = models.CharField(max_length=50,null=True,blank=True)
    user_agent = models.TextField(null=True,blank=True)
    #От контента вплоть до города
    continent = models.CharField(max_length=50, null=True, blank=True)
    continentCode = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True,blank=True)
    countryCode = models.CharField(max_length=50, null=True,blank=True)
    region = models.CharField(max_length=50, null=True,blank=True)
    regionName = models.CharField(max_length=50, null=True,blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    # Координаты
    lat = models.FloatField(null=True,blank=True)
    lon= models.FloatField(null=True,blank=True)
    # Временная зона
    timezone = models.CharField(max_length=50, null=True,blank=True)
    # Информация про организацию
    isp = models.TextField(null=True,blank=True)
    as_info = models.TextField(null=True,blank=True)
    asname = models.TextField(null=True,blank=True)
    reverse = models.TextField(null=True,blank=True)
    org = models.TextField(null=True,blank=True)
    # Является ли мобильной связью, прокси сервером или хостинговым сервером
    mobile = models.BooleanField(null=True,blank=True)
    proxy= models.BooleanField(null=True,blank=True)
    hosting= models.BooleanField(null=True,blank=True)
    #В случае ошибки
    error_msg = models.TextField(null=True,blank=True)
    # Является ли игрой
    if_game = models.BooleanField(null=True, blank=True)


class Events(models.Model):
    user_id = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now)
    event_name = models.CharField(max_length=50)
    json_data = models.TextField(null=True,blank=True)

    # данные пользователя
    ip_address = models.CharField(max_length=50,null=True,blank=True)
    user_agent = models.TextField(null=True,blank=True)
    #От контента вплоть до города
    continent = models.CharField(max_length=50, null=True, blank=True)
    continentCode = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True,blank=True)
    countryCode = models.CharField(max_length=50, null=True,blank=True)
    region = models.CharField(max_length=50, null=True,blank=True)
    regionName = models.CharField(max_length=50, null=True,blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    # Координаты
    lat = models.FloatField(null=True,blank=True)
    lon= models.FloatField(null=True,blank=True)
    # Временная зона
    timezone = models.CharField(max_length=50, null=True,blank=True)
    # Информация про организацию
    isp = models.TextField(null=True,blank=True)
    as_info = models.TextField(null=True,blank=True)
    asname = models.TextField(null=True,blank=True)
    reverse = models.TextField(null=True,blank=True)
    org = models.TextField(null=True,blank=True)
    # Является ли мобильной связью, прокси сервером или хостинговым сервером
    mobile = models.BooleanField(null=True,blank=True)
    proxy= models.BooleanField(null=True,blank=True)
    hosting= models.BooleanField(null=True,blank=True)
    #В случае ошибки
    error_msg = models.TextField(null=True,blank=True)


class Gates(models.Model):
    url = models.TextField(null=True,blank=True)
    title = models.TextField(null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    icon = models.TextField(null=True,blank=True)
    image = models.TextField(null=True,blank=True)
    resource_pack = models.TextField(null=True, blank=True)
    number_of_entries = models.IntegerField(null=True, blank=True)
    # libraries = models.ArrayField(null=True,blank=True)


class FeaturedGates(models.Model):
    url = models.TextField(null=True,blank=True)
    title = models.TextField(null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    icon = models.TextField(null=True,blank=True)
    is_special = models.BooleanField(default=False)


class Users(models.Model):
    name = models.TextField(null=True,blank=True)
    email = models.TextField(null=True,blank=True)
    user_id = models.TextField(null=True,blank=True)
    country = models.TextField(null=True,blank=True)
    city = models.TextField(null=True,blank=True)


class SearchSuggestions(models.Model):
    query = models.TextField(null=True,blank=True)


class TelegramBotUser(models.Model):
    user_id = models.TextField(null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    is_ignore = models.BooleanField(null=True,blank=True)
