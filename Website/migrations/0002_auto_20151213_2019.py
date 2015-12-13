# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Website', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='measuredingredient',
            name='ingredient_ptr',
        ),
        migrations.RemoveField(
            model_name='measuredingredient',
            name='recipe_step',
        ),
        migrations.DeleteModel(
            name='MeasuredIngredient',
        ),
    ]
