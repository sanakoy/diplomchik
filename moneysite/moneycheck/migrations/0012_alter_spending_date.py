# Generated by Django 5.0.2 on 2024-03-12 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moneycheck', '0011_alter_spending_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spending',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
