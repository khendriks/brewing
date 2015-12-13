from django.conf.urls import url, patterns
from Website.views import temperature, HomeView, BrewerView

__author__ = 'kees'

urlpatterns = patterns(
    '',
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^temperature/$', temperature, name='temperature'),
    url(r'^brewer/$', BrewerView.as_view(), name='brewer'),
)
