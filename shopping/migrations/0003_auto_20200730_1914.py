# Generated by Django 3.0.8 on 2020-07-30 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0002_auto_20200730_1710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='status',
            field=models.BooleanField(default=True),
        ),
    ]
