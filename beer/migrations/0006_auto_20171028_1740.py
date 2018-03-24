# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-28 15:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beer', '0005_auto_20171028_1639'),
    ]

    operations = [
        migrations.RenameField(
            model_name='step',
            old_name='temperature',
            new_name='expected_temperature',
        ),
        migrations.AddField(
            model_name='step',
            name='actual_temperature',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='step',
            name='start',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
