from django.conf.urls import url

from beer.views import BeerDetailView, StepDetailView, HomeView, StepWithoutBeerView, BeerDeleteView, StepDeleteView, \
    BeerListView, IngredientCreateView, IngredientUpdateView, IngredientDeleteView, BoughtIngredientCreateView, \
    BoughtIngredientUpdateView, BoughtIngredientDeleteView, BoughtIngredientListView, BrewingStepStartView, \
    IngredientBoughtIngredientView, IngredientLinkView, BeerCopyView

urlpatterns = [
    url(r'^brewer/beer/new/$', BeerDetailView.as_view(template_name="brewer_beer.html", brewer=True), name='brewer-beer-new'),
    url(r'^brewer/beer/delete/(?P<pk>[0-9]+)/$', BeerDeleteView.as_view(), name='brewer-beer-delete'),
    url(r'^brewer/beer/(?P<pk>[0-9]+)/$', BeerDetailView.as_view(template_name="brewer_beer.html", brewer=True), name='brewer-beer'),
    url(r'^brewer/beer/copy/(?P<pk>[0-9]+)/$', BeerCopyView.as_view(), name='brewer-beer-copy'),
    url(r'^brewer/step/new/nobeer/$', StepWithoutBeerView.as_view(), name='brewer-step-new'),
    url(r'^brewer/step/new/(?P<beer_pk>[0-9]+)/$', StepDetailView.as_view(template_name="brewer_step.html", brewer=True), name='brewer-step-new'),
    url(r'^brewer/step/(?P<pk>[0-9]+)/$', StepDetailView.as_view(template_name="brewer_step.html", brewer=True), name='brewer-step'),
    url(r'^brewer/step/delete/(?P<pk>[0-9]+)/$', StepDeleteView.as_view(), name='brewer-step-delete'),
    url(r'^brewer/ingredient/new/$', IngredientCreateView.as_view(), name='brewer-ingredient-new'),
    url(r'^brewer/ingredient/(?P<pk>[0-9]+)/$', IngredientUpdateView.as_view(), name='brewer-ingredient'),
    url(r'^brewer/ingredient/delete/(?P<pk>[0-9]+)/$', IngredientDeleteView.as_view(), name='brewer-ingredient-delete'),
    url(r'^brewer/bought_ingredient/new/$', BoughtIngredientCreateView.as_view(), name='brewer-bought-ingredient-new'),
    url(r'^brewer/bought_ingredient/(?P<pk>[0-9]+)/$', BoughtIngredientUpdateView.as_view(), name='brewer-bought-ingredient'),
    url(r'^brewer/bought_ingredient/delete/(?P<pk>[0-9]+)/$', BoughtIngredientDeleteView.as_view(), name='brewer-bought-ingredient-delete'),
    url(r'^brewer/bought_ingredient$', BoughtIngredientListView.as_view(), name='brewer-bought-ingredient-list'),
    url(r'^brewer/ingredient_bought_ingredient/(?P<pk>[0-9]+)/$', IngredientBoughtIngredientView.as_view(), name='brewer-ingredient-bought-ingredient'),
    url(r'^brewer/ingredient_link/(?P<ingredient_pk>[0-9]+)/$', IngredientLinkView.as_view(), name='brewer-ingredient-link'),
    url(r'^brewer', BeerListView.as_view(template_name="brewer_beer_list.html"), name='brewer-beer-list'),
    url(r'^brewing/beer/(?P<pk>[0-9]+)/$', BeerDetailView.as_view(template_name="brewing_beer.html", brewer=True, brewing=True), name='brewing-beer'),
    url(r'^brewing/step/(?P<pk>[0-9]+)/$', StepDetailView.as_view(template_name='brewing_step.html', brewer=True, brewing=True), name='brewing-step'),
    url(r'^brewing/step/start/(?P<pk>[0-9]+)/$', BrewingStepStartView.as_view() ,name='brewing-step-start'),
    url(r'^brewing', BeerListView.as_view(template_name='brewing_beer_list.html'), name='brewing-beer-list'),
    url(r'^beer/(?P<pk>[0-9]+)/$', BeerDetailView.as_view(), name='beer'),
    url(r'^step/(?P<pk>[0-9]+)/$', StepDetailView.as_view(), name='beer-step'),
    url(r'^', BeerListView.as_view(), name='beer-list'),
    url(r'^$', HomeView.as_view(), name='home')
]