# Generated by Django 4.2 on 2023-04-21 18:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0012_remove_news_region_content_code_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Regions_content',
        ),
        migrations.DeleteModel(
            name='Regions_source',
        ),
    ]
