# Generated by Django 2.1.7 on 2019-03-26 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kehubu', '0002_auto_20190325_0621'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='member_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
