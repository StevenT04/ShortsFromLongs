# Generated by Django 5.0.1 on 2024-02-07 21:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trans_parse_process', '0003_remove_transcript_structured_transcript_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shortclip',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clips', to='trans_parse_process.video'),
        ),
        migrations.CreateModel(
            name='Chunk',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chunks', to='trans_parse_process.video')),
            ],
        ),
        migrations.DeleteModel(
            name='Transcript',
        ),
    ]
