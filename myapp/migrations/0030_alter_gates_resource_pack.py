# Generated by Django 4.2 on 2023-06-21 23:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0029_alter_gates_resource_pack'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gates',
            name='resource_pack',
            field=models.TextField(blank=True, null=True),
        ),
    ]
