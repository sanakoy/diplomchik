# Generated by Django 5.0.2 on 2024-03-16 12:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('moneycheck', '0021_alter_plan_date'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Spending',
            new_name='Operation',
        ),
    ]
