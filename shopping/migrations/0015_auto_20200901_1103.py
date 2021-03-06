# Generated by Django 3.0.8 on 2020-09-01 05:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0014_auto_20200821_1721'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ordered',
            name='product',
        ),
        migrations.AddField(
            model_name='address',
            name='first_name',
            field=models.CharField(default='', max_length=250),
        ),
        migrations.AddField(
            model_name='address',
            name='last_name',
            field=models.CharField(default='', max_length=250),
        ),
        migrations.AddField(
            model_name='address',
            name='mobile',
            field=models.CharField(default='', max_length=15),
        ),
        migrations.AddField(
            model_name='ordered',
            name='cart_item',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='shopping.CartItem'),
        ),
    ]
