# Generated by Django 2.2 on 2019-04-18 02:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kehubu', '0011_groupchat'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='cover',
            field=models.ImageField(blank=True, upload_to='uploads/kehubu.Group.cover/%Y/%m/%d/'),
        ),
    ]
