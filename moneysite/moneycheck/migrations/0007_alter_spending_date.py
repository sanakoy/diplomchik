# Generated by Django 5.0.2 on 2024-03-09 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moneycheck', '0006_remove_category_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spending',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]