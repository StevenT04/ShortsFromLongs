# Generated by Django 5.0.1 on 2024-02-14 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trans_parse_process', '0008_rename_title_shortclip_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shortclip',
            name='clip_file',
            field=models.FileField(null=True, upload_to='clips/'),
        ),
    ]
