# Generated by Django 4.2 on 2023-04-22 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0017_remove_news_regions_news_region_delete_newsregion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='region',
            name='description',
            field=models.TextField(null=True),
        ),
    ]
