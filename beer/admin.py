from django.contrib import admin

from beer.models import Beer, Step, Ingredient, BoughtIngredient, IngredientBoughtIngredient

# Register your models here.

admin.site.register(Beer)
admin.site.register(Step)
admin.site.register(Ingredient)
admin.site.register(BoughtIngredient)
admin.site.register(IngredientBoughtIngredient)
