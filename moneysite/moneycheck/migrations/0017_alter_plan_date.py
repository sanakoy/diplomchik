# Generated by Django 5.0.2 on 2024-03-15 12:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moneycheck', '0016_alter_plan_date_alter_plan_is_global'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plan',
            name='date',
            field=models.DateField(default=datetime.datetime(2024, 3, 15, 12, 18, 16, 836035, tzinfo=datetime.timezone.utc)),
        ),
    ]
