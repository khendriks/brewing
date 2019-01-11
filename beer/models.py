import re
import warnings
from collections import OrderedDict
from datetime import datetime, timedelta

import pytz
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
# from django.utils.datetime_safe import datetime
from django.db.models import Sum
from django.utils import timezone
from django.utils.functional import cached_property


LITER = "L"
GRAM = "g"
UNITS = ((GRAM, 'gram'), (LITER, 'Liter'))


class Beer(models.Model):
    name = models.CharField(max_length=100, help_text='help')
    note = models.TextField(blank=True)

    brewer = models.ForeignKey(User, models.SET_NULL, null=True, blank=True)

    sell_price = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    bottles = models.PositiveIntegerField(null=True, blank=True)
    sold_bottles = models.PositiveIntegerField(default=0)

    @cached_property
    def start(self):
        earliest = None
        for step in self.steps.all():
            if step.start and earliest:
                earliest = min(earliest, step.start)
            elif step.start:
                earliest = step.start
        return earliest

    @cached_property
    def finish(self):
        latest = datetime(1900, 1, 1, tzinfo=pytz.UTC)
        for step in self.steps.all():
            if step.finish and latest:
                latest = max(latest, step.finish)
            elif step.finish:
                latest = step.finish
            else:
                # return none this is the latest
                return None
        return latest

    @cached_property
    def duration(self):
        longest = None
        for step in self.steps.all():
            if longest:
                longest = max(longest, step.duration_to_top)
            else:
                longest = step.duration_to_top
        return longest

    @cached_property
    def actual_duration(self):
        if self.start and self.finish:
            return self.finish - self.start

    @cached_property
    def expected_finish(self):
        if self.start and self.duration:
            return self.start + self.duration

    @cached_property
    def done(self):
        for step in self.steps.all():
            if not step.done:
                return False
        return True

    @property
    def in_progress(self):
        return self.start and not self.done

    @cached_property
    def price(self):
        total = 0
        for step in self.steps.all():
            total += step.price
        return total

    @cached_property
    def real_price(self):
        total = 0
        for step in self.steps.all():
            total += step.real_price
        return total

    @cached_property
    def profit(self):
        return self.sold_bottles * self.sell_price - self.real_price

    @property
    def linked(self):
        for step in self.steps.all():
            if not step.linked:
                return False
        return True

    @property
    def unlinked_steps(self):
        unlinked = []
        for step in self.steps.all():
            if not step.linked:
                unlinked.append(step)
        return unlinked

    @property
    def top_child(self):
        return self.steps.get(parent=None)

    @cached_property
    def first_step(self):
        longest_steps = []
        for step in self.steps.all():
            # it needs to be a leaf
            if step.is_leaf:
                # if we did not found one yet, set this one
                if not longest_steps:
                    longest_steps = [step]
                    continue

                # if the time is equal add it to the list of steps
                if longest_steps[0].duration_to_top == step.duration_to_top:
                    longest_steps.append(step)
                    continue

                # if the time is smaller, this step is deepest remove others
                if longest_steps[0].duration_to_top < step.duration_to_top:
                    longest_steps = [step]

        # longest steps now consists of all the steps which are the deepest leafs
        if not longest_steps:
            return None

        deepest = longest_steps[0]
        for step in longest_steps:
            if deepest.depth < step.depth:
                deepest = step

        return deepest

    @property
    def ingredients(self):
        queryset = Ingredient.objects.filter(step__beer=self)

        ingredients = OrderedDict()
        for ingredient in queryset:
            if ingredient.name + ingredient.unit in ingredients :
                if ingredients[ingredient.name + ingredient.unit].unit == ingredient.unit:
                    ingredients[ingredient.name + ingredient.unit].amount += ingredient.amount
            else:
                ingredients[ingredient.name + ingredient.unit] = ingredient

        return ingredients.values()


    def copy(self):
        pattern = re.compile(r'(.*?)-(\d+)$')
        if pattern.match(self.name):
            name = pattern.match(self.name).group(1)
            number = int(pattern.match(self.name).group(2))
            max_number = number + 1
        else:
            name = self.name
            max_number = 2

        similar = Beer.objects.filter(name__startswith=name)
        for beer in similar:
            if pattern.match(beer.name):
                number = int(pattern.match(beer.name).group(2))
                max_number = max(max_number, number + 1)

        copy_name = "{name}-{number}".format(name=name, number=max_number)

        copy = Beer(name=copy_name, note=self.note)
        copy.save()

        self.top_child.copy(copy)
        return copy

    def __str__(self):
        return self.name


class Step(models.Model):
    beer = models.ForeignKey(Beer, models.CASCADE, related_name='steps')
    parent = models.ForeignKey('self', models.SET_NULL, verbose_name='next step', null=True, blank=True)

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # start and finish are the actual times, duration is the planned time
    start = models.DateTimeField(null=True, blank=True)
    finish = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)

    actual_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    expected_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    actual_gravity = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True)
    expected_gravity = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True)

    @cached_property
    def price(self):
        total = 0
        for ingredient in self.ingredients.all():
            total += ingredient.price
        return total

    @cached_property
    def real_price(self):
        total = 0
        for ingredient in self.ingredients.all():
            total += ingredient.real_price
        return total

    @cached_property
    def done(self):
        return self.finish is not None

    @cached_property
    def in_progress(self):
        if self.start is None:
            return False
        return not self.done

    @cached_property
    def lacking(self):
        if self.parent is None:
            return False

        return not self.done and (self.parent.done or self.parent.lacking)

    @cached_property
    def actual_duration(self):
        if self.start and self.finish:
            return self.finish - self.start

    @cached_property
    def expected_finish(self):
        if self.start and self.duration:
            return self.start + self.duration

    @cached_property
    def duration_to_top(self):
        if self.parent is None:
            if self.duration:
                return self.duration
            return timedelta()
        if self.duration:
            return self.parent.duration_to_top + self.duration
        return self.parent.duration_to_top

    @cached_property
    def children(self):
        return Step.objects.filter(parent=self)

    def get_children(self):
        return self.children

    @cached_property
    def is_leaf(self):
        return not self.get_children()

    @cached_property
    def width(self):
        if self.is_leaf:
            width = 1
        else:
            width = 0
            for child in self.get_children():
                width += child.get_width()
        return width

    def get_width(self):
        warnings.warn("deprecated, use .width instead.", DeprecationWarning)
        return self.width

    @cached_property
    def depth(self):
        if self.parent is None:
            return 0
        return self.parent.depth + 1

    def get_depth(self):
        warnings.warn("deprecated, use .depth instead.", DeprecationWarning)
        return self.depth

    @cached_property
    def max_child_depth(self):
        if self.is_leaf:
            return self.depth
        else:
            deepest = 0
            for child in self.children:
                deepest = max(deepest, child.max_child_depth)
            return deepest

    @cached_property
    def deepest_child(self):
        steps = Step.objects.filter(beer=self.beer)
        for step in steps:
            if step.depth == self.max_child_depth:
                return step

    @property
    def brewer(self):
        return self.beer.brewer

    @property
    def linked(self):
        for ingredient in self.ingredients.all():
            if not ingredient.linked:
                return False
        return True

    def clean(self):
        super(Step, self).clean()

        # make sure there is no loop
        parent = self.parent
        while parent is not None:
            if parent == self:
                raise ValidationError('There is a loop detected')
            parent = parent.parent

    def save(self, *args, **kwargs):
        super(Step, self).save(*args, **kwargs)

        # make sure there is only one root
        if self.parent is None:
            old_parents = Step.objects.filter(beer=self.beer, parent=None).exclude(pk=self.pk)
            for old_parent in old_parents:
                if old_parent != self:
                    old_parent.parent = self
                    old_parent.save()

    def copy(self, beer, parent=None):
        # copy step
        copy = Step(beer=beer, parent=parent, name=self.name, description=self.description, duration=self.duration,
                    expected_temperature=self.expected_temperature, expected_gravity=self.expected_gravity)
        copy.save()

        # copy ingredients
        for ingredient in self.ingredients.all():
            ingredient.copy(copy)

        # copy children
        for child in self.children:
            child.copy(beer, copy)

    def __str__(self):
        return self.name


class BoughtIngredient(models.Model):
    name = models.CharField(max_length=100)
    note = models.TextField(blank=True)

    brewer = models.ForeignKey(User, models.SET_NULL, null=True, blank=True)

    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    unit = models.CharField(max_length=10, blank=True, null=True, choices=UNITS)

    done = models.BooleanField(default=False)

    @cached_property
    def used_amount(self):
        total = 0
        for ingredient in self.ingredient_bought_ingredients.all():
            total += ingredient.amount
        return total

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    step = models.ForeignKey(Step, models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=100)
    bought_ingredients = models.ManyToManyField(BoughtIngredient, related_name='usages', through='IngredientBoughtIngredient')

    amount = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    unit = models.CharField(max_length=10, blank=True, null=True, choices=UNITS)

    @cached_property
    def price(self):
        total = 0
        for part in self.ingredient_bought_ingredients.all():
            total += part.price
        return total

    @cached_property
    def real_price(self):
        total = 0
        for part in self.ingredient_bought_ingredients.all():
            total += part.real_price
        return total

    @property
    def filled_amount(self):
        total = 0
        for part in self.ingredient_bought_ingredients.all():
            total += part.amount
        return total

    @property
    def linked(self):
        return self.amount == self.filled_amount

    @property
    def brewer(self):
        return self.step.brewer

    def copy(self, step):
        copy = Ingredient(step=step, name=self.name, amount=self.amount, unit=self.unit)
        return copy.save()

    def __str__(self):
        return self.name


class IngredientBoughtIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, models.CASCADE, related_name='ingredient_bought_ingredients')
    bought_ingredient = models.ForeignKey(BoughtIngredient, models.CASCADE, related_name='ingredient_bought_ingredients')
    amount = models.DecimalField(max_digits=10, decimal_places=3)

    @cached_property
    def price(self):
        if self.bought_ingredient.amount == 0:
            return 0
        unit_price = self.bought_ingredient.price / self.bought_ingredient.amount
        return unit_price * self.amount

    @cached_property
    def real_price(self):
        if self.bought_ingredient.used_amount == 0:
            return 0
        unit_price = self.bought_ingredient.price / self.bought_ingredient.used_amount
        return unit_price * self.amount

    @property
    def brewer(self):
        return self.ingredient.brewer

    def __str__(self):
        return self.ingredient.name + '-' + self.bought_ingredient.name
