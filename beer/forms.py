from django import forms
from django.forms import formset_factory, modelformset_factory, inlineformset_factory
from django.http import QueryDict

from beer.models import Beer, Step, Ingredient, IngredientBoughtIngredient


class BeerForm(forms.ModelForm):
    class Meta:
        model = Beer
        fields = ('name', 'note', 'sell_price', 'brewer')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Name'}),
        }


class BrewerStepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ('beer', 'parent', 'name', 'description', 'duration', 'expected_temperature', 'expected_gravity')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Name'}),
            'duration': forms.TextInput(attrs={'placeholder': 'hh:mm:ss'})
        }


class BrewingStepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ('actual_temperature', 'actual_gravity')


IngredientStepFormSet = inlineformset_factory(Step, Ingredient, fields=('name', 'amount', 'unit'), extra=1)
# IngredientStepFormSet = modelformset_factory(Ingredient, fields=('name', 'amount', 'unit'), extra=1)

IngredientBoughtIngredientFormSet = inlineformset_factory(Ingredient, IngredientBoughtIngredient, fields=('bought_ingredient', 'amount'), extra=1)

