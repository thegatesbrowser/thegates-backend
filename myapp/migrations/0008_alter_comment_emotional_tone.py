# Generated by Django 4.2 on 2023-04-11 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_remove_comment_source_alter_comment_emotional_tone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='emotional_tone',
            field=models.CharField(choices=[('pos', 'положительно'), ('neg', 'негативно'), ('neu', 'нейтрально'), ('skip', 'Skip')], default='skip', max_length=4),
        ),
    ]
