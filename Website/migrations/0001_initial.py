# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Beer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('start', models.DateTimeField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('unit', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='MeasuredTemperature',
            fields=[
                ('datetime', models.DateTimeField(verbose_name='Date time', primary_key=True, unique=True, serialize=False, default=django.utils.timezone.now)),
                ('temperature', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='PreferredTemperature',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('average', models.DecimalField(decimal_places=2, max_digits=5)),
                ('minimum', models.DecimalField(decimal_places=2, max_digits=5)),
                ('maximum', models.DecimalField(decimal_places=2, max_digits=5)),
                ('deviation', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('duration', models.DurationField()),
            ],
        ),
        migrations.CreateModel(
            name='RecipeStep',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('explanation', models.TextField(blank=True)),
                ('offset', models.DurationField()),
                ('preferred_temperature', models.ForeignKey(null=True, blank=True, to='Website.PreferredTemperature')),
                ('recipe', models.ForeignKey(related_name='steps', to='Website.Recipe')),
            ],
            options={
                'ordering': ['offset'],
            },
        ),
        migrations.CreateModel(
            name='MeasuredIngredient',
            fields=[
                ('ingredient_ptr', models.OneToOneField(parent_link=True, auto_created=True, serialize=False, primary_key=True, to='Website.Ingredient')),
                ('amount', models.DecimalField(decimal_places=3, max_digits=8)),
                ('recipe_step', models.ForeignKey(related_name='ingredients', to='Website.RecipeStep')),
            ],
            bases=('Website.ingredient',),
        ),
        migrations.AddField(
            model_name='beer',
            name='recipe',
            field=models.ForeignKey(related_name='beers', to='Website.Recipe'),
        ),
        migrations.AddField(
            model_name='beer',
            name='temperatures',
            field=models.ManyToManyField(related_name='beers', blank=True, to='Website.MeasuredTemperature'),
        ),
    ]
