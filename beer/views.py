from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView, RedirectView
from django.views.generic.edit import FormMixin, DeleteView, FormView, CreateView, UpdateView, BaseCreateView

from beer.forms import BeerForm, BrewerStepForm, BrewingStepForm, IngredientStepFormSet, \
    IngredientBoughtIngredientFormSet
from beer.models import Beer, Step, Ingredient, BoughtIngredient, IngredientBoughtIngredient
from beer.utils import TreeTable, is_staff

# Create your views here.


class BeerListView(ListView):
    brewer = False
    brewing = False
    model = Beer
    template_name = 'viewer_beer_list.html'
    context_object_name = 'beers'

    def get_queryset(self):
        if self.brewer or self.brewing:
            if self.request.user.pk is None:
                return Beer.objects.none()
            return Beer.objects.filter(brewer__pk=self.request.user.pk)
        return Beer.objects.all()


class BeerDetailView(UserPassesTestMixin, ListView, FormMixin):
    brewer = False
    brewing = False
    model = Step
    template_name = 'viewer_beer.html'
    raise_exception = True

    def test_func(self):
        if not self.brewer and not self.brewing:
            return True

        user = self.request.user
        pk = self.kwargs.get('pk')
        if not pk:
            # new beer is only for logged in users
            self.raise_exception = False
            return user.pk is not None

        brewer = get_object_or_404(Beer, pk=pk).brewer
        if brewer:
            return brewer.pk == user.pk

        return is_staff(user)

    def get_queryset(self):
        pk = self.kwargs.get('pk')

        if pk:
            queryset = Step.objects.filter(beer=pk)
        else:
            queryset = Step.objects.none()

        return queryset

    def get_context_data(self, **kwargs):

        top = None
        if self.object_list.count() != 0:
            top = self.object_list.get(parent=None)
        # add the children depth first, so the steps are in the correct order
        tree_table = TreeTable(top)
        steps = tree_table.get_rows()

        beer = None
        beer_pk = self.kwargs.get('pk')
        if beer_pk:
            beer = Beer.objects.get(pk=beer_pk)

        form = None
        if self.brewer:
            if beer:
                form = BeerForm(instance=beer)
            else:
                form = BeerForm()

        return super(BeerDetailView, self).get_context_data(steps=steps, beer=beer, form=form, **kwargs)

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')

        beer = None
        if pk:
            beer = Beer.objects.get(pk=pk)

        form = BeerForm(request.POST, instance=beer)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        if self.kwargs.get('pk'):
            beer = form.save()
        else:
            beer = form.save(commit=False)
            beer.brewer = self.request.user
            beer.save()
            self.add_default_steps(beer)

        self.kwargs['pk'] = beer.pk
        self.kwargs['beer'] = beer
        self.kwargs['submit_type'] = form.data['action']
        return super(BeerDetailView, self).form_valid(form)

    def add_default_steps(self, beer):
        bottle = Step(name='bottle', beer=beer)
        bottle.save()
        lager = Step(name='lager', beer=beer, parent=bottle)
        lager.save()
        ferment = Step(name='ferment', beer=beer, parent=lager)
        ferment.save()
        pitch_yeast = Step(name='pitch yeast', beer=beer, parent=ferment)
        pitch_yeast.save()
        pitch_starter = Step(name='yeast starter', beer=beer, parent=pitch_yeast)
        pitch_starter.save()
        cooling = Step(name='cooling', beer=beer, parent=pitch_yeast)
        cooling.save()
        cooking = Step(name='cook', beer=beer, parent=cooling)
        cooking.save()
        malt = Step(name='malt', beer=beer, parent=cooking)
        malt.save()

    def get_success_url(self):
        if self.kwargs['submit_type'] == 'Start':
            return reverse('brewing-beer', kwargs={'pk': self.kwargs.get('pk')})

        return reverse('brewer-beer', kwargs={'pk': self.kwargs.get('pk')})


class BeerDeleteView(UserPassesTestMixin, DeleteView):
    model = Beer
    success_url = reverse_lazy('brewer-beer-list')
    template_name = 'confirm_delete.html'
    raise_exception = True

    def test_func(self):
        brewer = self.get_object().brewer
        user = self.request.user

        if brewer:
            return brewer.pk == user.pk

        # this is an orphan beer
        return is_staff(user)

    def delete(self, request, *args, **kwargs):
        # also delete all steps of this beer
        pk = self.kwargs.get('pk')
        steps = Step.objects.filter(beer=pk)
        steps.delete()

        return super(BeerDeleteView, self).delete(request, *args, **kwargs)


class StepDetailView(UserPassesTestMixin, ListView, FormMixin):
    brewer = False
    brewing = False
    model = Step
    template_name = 'viewer_step.html'
    form_class = BrewerStepForm
    raise_exception = True

    def test_func(self):
        if not self.brewer and not self.brewing:
            return True

        user = self.request.user

        brewer = None
        pk = self.kwargs.get('pk')
        if pk:
            brewer = get_object_or_404(Step, pk=self.kwargs.get('pk')).brewer
        else:
            brewer = get_object_or_404(Beer, pk=self.kwargs.get('beer_pk')).brewer

        if brewer:
            return brewer.pk == user.pk

        return is_staff(user)

    def get_queryset(self):
        pk = self.kwargs.get('pk')

        if pk:
            step = Step.objects.get(pk=pk)
            steps = Step.objects.filter(beer=step.beer)
        else:
            beer_pk = self.kwargs.get('beer_pk')
            beer = Beer.objects.get(pk=beer_pk)
            steps = Step.objects.filter(beer=beer)

        return steps

    def get_context_data(self, form=None, **kwargs):

        ingredients = None
        ingredient_form_set = None
        top = None
        if self.object_list.count() != 0:
            top = self.object_list.get(parent=None)
        tree_table = TreeTable(top)
        steps = tree_table.get_rows()

        pk = self.kwargs.get('pk')
        if pk:
            step = Step.objects.get(pk=pk)
            parents = steps[:step.depth + 1]
        else:
            beer_pk = self.kwargs.get('beer_pk')
            beer = Beer.objects.get(pk=beer_pk)
            step = Step()
            step.beer = beer
            if top:
                step.parent = top.deepest_child

            parents = steps

        if self.brewer and not form:
            if not self.brewing:
                form = BrewerStepForm(instance=step)
                ingredients = Ingredient.objects.filter(step=step)
                if 'ingredient_form_set' not in kwargs:
                    kwargs['ingredient_form_set'] = IngredientStepFormSet(instance=step)
            else:
                form = BrewingStepForm(instance=step)

        if self.brewing:
            min_steps = max(step.depth - 1, 0)
            max_steps = min(step.depth + 1, step.max_child_depth)
            steps = steps[min_steps:max_steps + 1]

        return super(StepDetailView, self).get_context_data(form=form, step=step, steps=steps, parents=parents, ingredients=ingredients, **kwargs)

    def get_step(self):
        try:
            return Step.objects.get(pk=self.kwargs.get('pk'))
        except Step.DoesNotExist:
            return None

    def get_ingredient_queryset(self):
        return Ingredient.objects.filter(step__pk=self.kwargs.pk)

    def get_ingredient_formset(self, data=None):
        return IngredientStepFormSet(data=data, instance=self.get_step())

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')

        step=None
        if pk:
            step = Step.objects.get(pk=pk)

        if not self.brewing:
            form = BrewerStepForm(request.POST, instance=step)
        else:
            form = BrewingStepForm(request.POST, instance=step)

        ingredient_form_set = self.get_ingredient_formset(request.POST)
        if form.is_valid() and ingredient_form_set.is_valid():
            return self.form_valid(form, ingredient_form_set=ingredient_form_set)
        else:
            return self.form_invalid(form, ingredient_form_set=ingredient_form_set)

    def form_valid(self, form, **subforms):
        step = form.save()
        for subform in subforms.values():
            subform.save()
        self.kwargs['step'] = step
        self.kwargs['pk'] = step.pk
        self.kwargs['submit_type'] = form.data['action']
        return super(StepDetailView, self).form_valid(form)

    def form_invalid(self, form, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form, **kwargs)
        return self.render_to_response(context)

    def get_success_url(self):
        if self.brewing:
            if self.kwargs['submit_type'] == 'save':
                return reverse('brewing-step', kwargs={'pk': self.kwargs.get('pk')})

            if self.kwargs['submit_type'] == 'finish':
                self.finish_step()

                step = self.kwargs.get('step')
                if step.parent:
                    return reverse('brewing-step', kwargs={'pk': step.parent.pk})
                return reverse('brewing-beer', kwargs={'pk': step.beer.pk})

        if self.kwargs['submit_type'] == 'Finish':
            return reverse('brewer-beer', kwargs={'pk': self.kwargs.get('step').beer.pk})

        if self.kwargs['submit_type'] == 'Add another':
            return reverse('brewer-step-new', kwargs={'beer_pk': self.kwargs.get('step').beer.pk})

        return reverse('brewer-step', kwargs={'pk': self.kwargs.get('pk')})

    def finish_step(self):
        step = self.kwargs.get('step')
        now = timezone.now()

        step_changed = False
        parent_changed = False
        if step.finish is None:
            step.finish = now
            step_changed = True
        if step.start is None:
            step.start = step.finish
            step_changed = True
        if step.parent:
            if step.parent.start is None:
                step.parent.start = now
                parent_changed = True

        if step_changed:
            step.save()
        if parent_changed:
            step.parent.save()


class StepDeleteView(UserPassesTestMixin, DeleteView):
    model = Step
    template_name = 'confirm_delete.html'
    raise_exception = True

    def test_func(self):
        brewer = self.get_object().brewer
        user = self.request.user

        if brewer:
            return brewer.pk == user.pk

        # this is an orphan beer
        return is_staff(user)

    def get_success_url(self):
        beer_pk = self.object.beer.pk
        return reverse('brewer-beer', kwargs={'pk': beer_pk})


class StepWithoutBeerView(RedirectView):
    pattern_name = 'brewer-step-new'
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        # Create an empty beer and redirect it to this beer
        beer = Beer.objects.create(name='Untitled')
        return super(StepWithoutBeerView, self).get_redirect_url(beer_pk=beer.pk, *args, **kwargs)


class BrewingStepStartView(RedirectView):
    pattern_name = 'brewing-step'
    permanent = True
    raise_exception = True

    def test_func(self):
        step = get_object_or_404(Step, pk=self.kwargs.get('pk'))

        brewer = step.brewer
        user = self.request.user

        if brewer:
            return brewer.pk == user.pk

        # this is an orphan beer
        return is_staff(user)

    def get_redirect_url(self, *args, **kwargs):
        # Start the step if not started
        step = get_object_or_404(Step, pk=self.kwargs.get('pk'))
        if not step.start:
            step.start = timezone.now()
            step.save()
        return super(BrewingStepStartView, self).get_redirect_url(*args, **kwargs)


class BeerCopyView(UserPassesTestMixin, RedirectView):
    pattern_name = 'brewer-beer'
    raise_exception = True

    def test_func(self):
        beer = get_object_or_404(Beer, pk=self.kwargs.get('pk'))

        brewer = beer.brewer
        user = self.request.user

        if brewer:
            return brewer.pk == user.pk

        # this is an orphan beer
        return is_staff(user)

    def get_redirect_url(self, *args, **kwargs):
        original = Beer.objects.get(pk=self.kwargs.get('pk'))
        copy = original.copy()

        return reverse('brewer-beer', kwargs={'pk': copy.pk})



class BoughtIngredientCreateView(LoginRequiredMixin, CreateView):
    model = BoughtIngredient
    template_name = 'brewer_ingredient.html'
    fields = ['name', 'note', 'price', 'amount', 'unit']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.brewer = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('brewer-bought-ingredient', kwargs={'pk': self.object.pk})

class BoughtIngredientUpdateView(UserPassesTestMixin, UpdateView):
    model = BoughtIngredient
    template_name = 'brewer_ingredient.html'
    fields = ['name', 'note', 'price', 'amount', 'unit']
    raise_exception = True

    def test_func(self):
        bought_ingredient = get_object_or_404(BoughtIngredient, pk=self.kwargs.get('pk'))

        brewer = bought_ingredient.brewer
        user = self.request.user

        if brewer:
            return brewer.pk == user.pk

        # this is an orphan beer
        return is_staff(user)

    def get_success_url(self):
        return reverse('brewer-bought-ingredient', kwargs={'pk': self.object.pk})


class BoughtIngredientDeleteView(UserPassesTestMixin, DeleteView):
    model = BoughtIngredient
    template_name = 'confirm_delete.html'
    raise_exception = True

    def test_func(self):
        bought_ingredient = get_object_or_404(BoughtIngredient, pk=self.kwargs.get('pk'))

        brewer = bought_ingredient.brewer
        user = self.request.user

        if brewer:
            return brewer.pk == user.pk

        # this is an orphan beer
        return is_staff(user)

    def get_success_url(self):
        step_pk = self.object.step.pk
        return reverse('brewer-step', kwargs={'pk': step_pk})


class BoughtIngredientListView(LoginRequiredMixin, ListView):
    queryset = BoughtIngredient.objects.filter(done=False)
    template_name = 'brewer_bought_ingredient_list.html'
    context_object_name = 'ingredients'

    def get_queryset(self):
        user = self.request.user
        if user.pk is None:
            return  BoughtIngredient.objects.none()

        return BoughtIngredient.objects.filter(done=False).filter(brewer__pk=user.pk)


class IngredientLinkView(UserPassesTestMixin, FormView):
    template_name = 'brewer_ingredient_link.html'
    raise_exception = True

    def test_func(self):
        ingredient = get_object_or_404(Ingredient, pk=self.kwargs.get('ingredient_pk'))

        brewer = ingredient.brewer
        user = self.request.user

        if brewer:
            return brewer.pk == user.pk

        # this is an orphan beer
        return is_staff(user)

    def get_form(self, form_class=None):
        ingredient = Ingredient.objects.get(pk=self.kwargs.get('ingredient_pk'))

        return IngredientBoughtIngredientFormSet(instance=ingredient, **self.get_form_kwargs())

    def form_valid(self, form):
        form.save()
        return super(IngredientLinkView, self).form_valid(form)

    def get_success_url(self):
        ingredient = Ingredient.objects.get(pk=self.kwargs.get('ingredient_pk'))
        return reverse('brewer-step', kwargs={'pk': ingredient.step.pk})
