from django.conf.urls import url, include

from accounts.views import ProfileUpdateView

urlpatterns = [
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^profile', ProfileUpdateView.as_view(), name='profile')
]