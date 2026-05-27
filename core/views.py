from django.views.generic import TemplateView, CreateView
from django.contrib.auth import login
from django.contrib.auth.views import LoginView as AuthLoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from core.forms import UserRegistrationForm, EmailAuthenticationForm
from organizations.models import Organization, Member


class LandingView(TemplateView):
    template_name = 'landing.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


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


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard principal com métricas reais de organizações e membros."""

    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs) -> dict:
        """Injeta contagens reais de organizações e membros no contexto do template."""
        context = super().get_context_data(**kwargs)
        context['total_organizations'] = Organization.objects.count()
        context['total_members'] = Member.objects.count()
        return context
