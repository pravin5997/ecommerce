# Generated by Django 3.0.8 on 2020-09-17 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0035_orderitem_order_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='order_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
