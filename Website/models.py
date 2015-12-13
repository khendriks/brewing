from django.db import models
from django.utils import timezone


class MeasuredTemperature(models.Model):
    datetime = models.DateTimeField(verbose_name='Date time', default=timezone.now, unique=True, primary_key=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2)  # 111.11


class PreferredTemperature(models.Model):
    average = models.DecimalField(max_digits=5, decimal_places=2)
    minimum = models.DecimalField(max_digits=5, decimal_places=2)
    maximum = models.DecimalField(max_digits=5, decimal_places=2)
    deviation = models.FloatField()


class Ingredient(models.Model):
    name = models.CharField(max_length=255, unique=True)
    unit = models.CharField(max_length=255)


class MeasuredIngredient(Ingredient):
    amount = models.DecimalField(max_digits=8, decimal_places=3)  # 11111.111
    recipe_step = models.ForeignKey('RecipeStep', related_name='ingredients')


class RecipeStep(models.Model):
    recipe = models.ForeignKey('Recipe', related_name='steps')
    explanation = models.TextField(blank=True)
    preferred_temperature = models.ForeignKey(PreferredTemperature, null=True, blank=True)
    offset = models.DurationField()

    def get_number(self):
        steps = self.recipe.steps.all()
        return list(steps).index(self) + 1

    def __str__(self):
        return self.recipe.name + ' ' + str(self.get_number())

    class Meta:
        ordering = ['offset']


class Recipe(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.DurationField()

    def __str__(self):
        return self.name


class Beer(models.Model):
    temperatures = models.ManyToManyField(MeasuredTemperature, related_name='beers', blank=True)
    recipe = models.ForeignKey(Recipe, related_name='beers')
    start = models.DateTimeField(null=True, blank=True)

    def finished(self):
        return self.start + self.recipe.duration

    def is_brewing(self):
        finish = self.finished()
        if self.start < timezone.now() < finish:
            return True
        return False

    def is_active(self):  # TODO change to only return True if in stock
        return self.is_brewing()

    def progress(self):
        now = timezone.now()
        if now <= self.start:
            return 0  # not started yet
        if now >= self.finished():
            return 100  # finished
        duration = (self.finished() - self.start).total_seconds()
        progress = (now - self.start).total_seconds()
        return int((progress/duration)*100)

    def __str__(self):
        return self.recipe.name + ' ' + str(self.finished().year)

    def __unicode__(self):
        return self.__str__()
