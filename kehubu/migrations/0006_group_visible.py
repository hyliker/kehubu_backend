# Generated by Django 2.2 on 2019-04-08 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kehubu', '0005_auto_20190326_0610'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='visible',
            field=models.PositiveSmallIntegerField(choices=[(0, 'public'), (1, 'private')], default=0, verbose_name='visible'),
        ),
    ]