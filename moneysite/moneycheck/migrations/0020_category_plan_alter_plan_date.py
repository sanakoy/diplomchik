# Generated by Django 5.0.2 on 2024-03-15 15:41

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moneycheck', '0019_remove_plan_kod_cat_alter_plan_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='plan',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='moneycheck.plan'),
        ),
        migrations.AlterField(
            model_name='plan',
            name='date',
            field=models.DateField(default=datetime.datetime(2024, 3, 15, 15, 41, 3, 675142, tzinfo=datetime.timezone.utc)),
        ),
    ]