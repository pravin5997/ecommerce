# Generated by Django 3.0.8 on 2020-09-04 10:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0024_auto_20200904_1221'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='email',
        ),
    ]