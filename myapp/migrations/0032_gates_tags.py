# Generated by Django 4.2.3 on 2023-07-17 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0031_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='gates',
            name='tags',
            field=models.TextField(blank=True, null=True),
        ),
    ]
