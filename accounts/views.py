from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, CreateView

from accounts.forms import CreateUserForm


class ProfileUpdateView(UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'registration/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user


class CreateUserView(CreateView):
    model = User
    template_name = 'registration/createuser.html'
    success_url = reverse_lazy('profile')
    form_class = CreateUserForm

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = User.objects.create_user(username=email, email=email, password=password)
        login(self.request, user, backend='accounts.auth.backends.EmailBackend')
        return HttpResponseRedirect(reverse('profile'))