# Generated by Django 3.2.9 on 2021-11-19 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video_collection', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='video_id',
            field=models.CharField(default=1, max_length=40, unique=True),
            preserve_default=False,
        ),
    ]
