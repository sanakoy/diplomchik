# Generated by Django 5.0.2 on 2024-03-15 12:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moneycheck', '0017_alter_plan_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plan',
            name='date',
            field=models.DateField(default=datetime.datetime(2024, 3, 15, 12, 40, 19, 390754, tzinfo=datetime.timezone.utc)),
        ),
    ]