from django.contrib import admin

# Register your models here.
from Website.models import Beer, Recipe, RecipeStep, MeasuredIngredient, Ingredient, MeasuredTemperature, \
    PreferredTemperature

admin.site.register(Beer, admin.ModelAdmin)
admin.site.register(Recipe, admin.ModelAdmin)
admin.site.register(RecipeStep, admin.ModelAdmin)
admin.site.register(MeasuredIngredient, admin.ModelAdmin)
admin.site.register(Ingredient, admin.ModelAdmin)
admin.site.register(MeasuredTemperature, admin.ModelAdmin)
admin.site.register(PreferredTemperature, admin.ModelAdmin)
