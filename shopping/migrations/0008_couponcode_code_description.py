# Generated by Django 3.0.8 on 2020-08-14 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0007_auto_20200814_1836'),
    ]

    operations = [
        migrations.AddField(
            model_name='couponcode',
            name='code_description',
            field=models.TextField(default='', max_length=100),
        ),
    ]
