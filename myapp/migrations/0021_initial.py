# Generated by Django 4.2 on 2023-05-01 10:11

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('myapp', '0020_remove_comment_news_remove_news_region_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Downloads',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('who', models.CharField(max_length=30, null=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('gate_app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='downloads', to='myapp.gate')),
            ],
        ),
    ]
