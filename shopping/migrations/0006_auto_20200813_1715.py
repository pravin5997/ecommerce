# Generated by Django 3.0.8 on 2020-08-13 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0005_auto_20200813_1623'),
    ]

    operations = [
        migrations.AlterField(
            model_name='couponcode',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
