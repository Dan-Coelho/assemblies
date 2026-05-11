from django.views.generic import TemplateView, CreateView
from django.contrib.auth import login
from django.contrib.auth.views import LoginView as AuthLoginView
from django.urls import reverse_lazy
from core.forms import UserRegistrationForm, EmailAuthenticationForm


class LandingView(TemplateView):
    template_name = 'landing.html'


class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'register.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class LoginView(AuthLoginView):
    form_class = EmailAuthenticationForm
    template_name = 'login.html'
