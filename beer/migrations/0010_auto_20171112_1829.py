# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-12 17:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('beer', '0009_auto_20171112_1816'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='unit',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='bought_ingredient',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='beer.BoughtIngredient'),
        ),
    ]
