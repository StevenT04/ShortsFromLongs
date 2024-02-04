# Generated by Django 5.0.1 on 2024-02-04 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trans_parse_process', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shortclip',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
        migrations.AddField(
            model_name='video',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]
