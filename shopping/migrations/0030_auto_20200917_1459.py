# Generated by Django 3.0.8 on 2020-09-17 09:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0029_auto_20200917_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='cart',
            field=models.ForeignKey(default=5, on_delete=django.db.models.deletion.CASCADE, related_name='order_cart', to='shopping.Cart'),
        ),
    ]