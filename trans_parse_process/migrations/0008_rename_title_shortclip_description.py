# Generated by Django 5.0.1 on 2024-02-12 20:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trans_parse_process', '0007_video_thumbnail'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shortclip',
            old_name='title',
            new_name='description',
        ),
    ]