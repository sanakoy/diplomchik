# Generated by Django 5.0.2 on 2024-03-09 13:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('moneycheck', '0005_category_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='slug',
        ),
    ]
