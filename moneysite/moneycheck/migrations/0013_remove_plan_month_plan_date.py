# Generated by Django 5.0.2 on 2024-03-15 11:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moneycheck', '0012_alter_spending_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plan',
            name='month',
        ),
        migrations.AddField(
            model_name='plan',
            name='date',
            field=models.DateField(default=datetime.datetime(2024, 3, 15, 11, 48, 3, 703330, tzinfo=datetime.timezone.utc)),
        ),
    ]
