# Generated by Django 3.0.8 on 2020-08-13 10:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0004_couponcode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='couponcode',
            name='discount',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5000)]),
        ),
    ]
