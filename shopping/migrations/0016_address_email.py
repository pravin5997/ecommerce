# Generated by Django 3.0.8 on 2020-09-01 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0015_auto_20200901_1103'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='email',
            field=models.EmailField(default='', max_length=254),
        ),
    ]
