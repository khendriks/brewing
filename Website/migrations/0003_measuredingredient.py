# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Website', '0002_auto_20151213_2019'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeasuredIngredient',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('amount', models.DecimalField(max_digits=8, decimal_places=3)),
                ('ingredient', models.ForeignKey(to='Website.Ingredient')),
                ('recipe_step', models.ForeignKey(to='Website.RecipeStep', related_name='ingredients')),
            ],
        ),
    ]
