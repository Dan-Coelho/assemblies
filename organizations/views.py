from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.shortcuts import get_object_or_404
from .models import Organization, Member
from .forms import OrganizationForm, MemberForm


class OrganizationListView(LoginRequiredMixin, ListView):
    """Lista todas as organizações cadastradas na plataforma."""

    model = Organization
    template_name = 'organizations/list.html'
    context_object_name = 'organizations'


class OrganizationCreateView(LoginRequiredMixin, CreateView):
    """Formulário de criação de nova organização."""

    model = Organization
    form_class = OrganizationForm
    template_name = 'organizations/form.html'
    success_url = reverse_lazy('organization_list')


class OrganizationDetailView(LoginRequiredMixin, DetailView):
    """Exibe os detalhes de uma organização específica."""

    model = Organization
    template_name = 'organizations/detail.html'
    context_object_name = 'organization'


class OrganizationUpdateView(LoginRequiredMixin, UpdateView):
    """Formulário de edição de uma organização existente."""

    model = Organization
    form_class = OrganizationForm
    template_name = 'organizations/form.html'

    def get_success_url(self) -> str:
        """Redireciona para a página de detalhe após a edição bem-sucedida."""
        return reverse('organization_detail', kwargs={'pk': self.object.pk})


# ── Member Views ─────────────────────────────────────────────────────────────


class MemberListView(LoginRequiredMixin, ListView):
    """Lista todos os membros de uma organização específica."""

    model = Member
    template_name = 'members/list.html'
    context_object_name = 'members'

    def get_queryset(self):
        """Filtra membros pela organização informada na URL."""
        self.organization = get_object_or_404(Organization, pk=self.kwargs['org_pk'])
        return Member.objects.filter(organization=self.organization)

    def get_context_data(self, **kwargs) -> dict:
        """Injeta a organização no contexto do template."""
        context = super().get_context_data(**kwargs)
        context['organization'] = self.organization
        return context


class MemberCreateView(LoginRequiredMixin, CreateView):
    """Formulário de criação de um novo membro em uma organização."""

    model = Member
    form_class = MemberForm
    template_name = 'members/form.html'

    def get_organization(self) -> Organization:
        """Retorna a organização a partir do parâmetro da URL."""
        return get_object_or_404(Organization, pk=self.kwargs['org_pk'])

    def get_context_data(self, **kwargs) -> dict:
        """Injeta a organização no contexto do template."""
        context = super().get_context_data(**kwargs)
        context['organization'] = self.get_organization()
        return context

    def form_valid(self, form):
        """Associa o membro à organização antes de salvar."""
        form.instance.organization = self.get_organization()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """Redireciona para a lista de membros da organização."""
        return reverse('member_list', kwargs={'org_pk': self.kwargs['org_pk']})


class MemberUpdateView(LoginRequiredMixin, UpdateView):
    """Formulário de edição de um membro existente."""

    model = Member
    form_class = MemberForm
    template_name = 'members/form.html'

    def get_organization(self) -> Organization:
        """Retorna a organização a partir do parâmetro da URL."""
        return get_object_or_404(Organization, pk=self.kwargs['org_pk'])

    def get_context_data(self, **kwargs) -> dict:
        """Injeta a organização no contexto do template."""
        context = super().get_context_data(**kwargs)
        context['organization'] = self.get_organization()
        return context

    def get_success_url(self) -> str:
        """Redireciona para a lista de membros após a edição."""
        return reverse('member_list', kwargs={'org_pk': self.kwargs['org_pk']})
