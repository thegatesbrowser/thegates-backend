# Generated by Django 5.1.7 on 2025-03-24 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0037_telegrambotuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegrambotuser',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
