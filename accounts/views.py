from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import UpdateView


class ProfileUpdateView(UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'registration\profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user