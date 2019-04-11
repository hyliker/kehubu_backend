# Generated by Django 2.2 on 2019-04-11 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kehubu', '0008_auto_20190411_0348'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='notice',
            field=models.TextField(blank=True, verbose_name='notice'),
        ),
        migrations.AddField(
            model_name='group',
            name='notice_enabled',
            field=models.BooleanField(default=False, verbose_name='notice enabled'),
        ),
        migrations.AddField(
            model_name='group',
            name='notice_updated',
            field=models.DateTimeField(editable=False, null=True, verbose_name='notice updated'),
        ),
    ]
