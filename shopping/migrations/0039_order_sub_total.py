# Generated by Django 3.0.8 on 2020-09-24 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0038_auto_20200917_1752'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='sub_total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
