# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-23 20:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Beer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('note', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('note', models.TextField()),
                ('amount', models.DecimalField(decimal_places=3, max_digits=10)),
                ('unit', models.CharField(max_length=10)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('buy_amount', models.DecimalField(decimal_places=3, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('time', models.DurationField()),
                ('start', models.DateTimeField(auto_now=True)),
                ('temperature', models.DecimalField(decimal_places=2, max_digits=5)),
                ('actual_gravity', models.DecimalField(decimal_places=3, max_digits=4)),
                ('expected_gravity', models.DecimalField(decimal_places=3, max_digits=4)),
                ('beer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beer.Beer')),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='beer.Step', verbose_name='next step')),
            ],
        ),
        migrations.AddField(
            model_name='ingredient',
            name='step',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beer.Step'),
        ),
    ]
