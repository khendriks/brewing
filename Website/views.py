import hashlib
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render
import time as python_time

# Create your views here.
from django.utils.datetime_safe import datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.timezone import utc
from django.views.generic import View, ListView, TemplateView
from Website.models import MeasuredTemperature, Beer

SECRET = 'UVgxCasmGraXCe2rwU9xCaKDc6mhmhaV7j5Ncpp5KXMhpDsxIVQxsNr9bSjX'


class NavbarMixin(object):

    navbar = 'home'

    def get_context_data(self, **kwargs):
        context = super(NavbarMixin, self).get_context_data(**kwargs)
        context['navbar'] = self.navbar
        return context



@csrf_exempt
@require_http_methods(["POST", "GET"])  # TODO delete GET
def temperature(request):

    if request.method == 'GET':
        return HttpResponse('<html><head></head><body><form action="" method="post">'
                            '<input type="text" name="time" value="%s">'
                            '<input type="text" name="temperature" value="24.4">'
                            '<input type="text" name="hash" value="codeing">'
                            '<input type="submit" value="Submit">'
                            '</form></body></html>' % str(int(python_time.time())))  # TODO delete GET

    # check if there are active beers
    for beer in Beer.objects.all():
        if beer.is_brewing():
            break
    else:  # non of the beers is brewing, we do not save, but still respond to be nice ;)
        return HttpResponse('OK, not brewing though')

    received = request.POST['hash']
    temperature = request.POST['temperature']
    time = request.POST['time']
    correct = 'time=%s&temperature=%s&secret=%s' % (time, temperature, SECRET)
    correct = hashlib.md5(correct.encode()).hexdigest()
    if not received == correct:
        return HttpResponseForbidden()
    time = datetime.fromtimestamp(int(time), tz=utc)
    temp = MeasuredTemperature.objects.create(datetime=time, temperature=temperature)
    for beer in Beer.objects.all():
        if beer.is_brewing():
            beer.temperatures.add(temp)
    return HttpResponse('OK!')


class HomeView(NavbarMixin, ListView):
    template_name = 'Website/index.html'
    model = Beer


class BrewerView(NavbarMixin, ListView):
    template_name = "Website/brewer.html"
    model = Beer
    navbar = 'brewer'
