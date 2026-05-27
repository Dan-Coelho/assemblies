from django import forms
from .models import Organization, Member


class OrganizationForm(forms.ModelForm):
    """Formulário para criação e edição de organizações."""

    class Meta:
        model = Organization
        fields = ['name', 'type', 'cnpj', 'plan']


class MemberForm(forms.ModelForm):
    """Formulário para criação e edição de membros de uma organização."""

    class Meta:
        model = Member
        fields = ['name', 'email', 'cpf', 'role', 'status', 'is_defaulter', 'user']
        labels = {
            'name': 'Nome completo',
            'email': 'E-mail',
            'cpf': 'CPF',
            'role': 'Papel',
            'status': 'Status',
            'is_defaulter': 'Inadimplente',
            'user': 'Usuário do sistema (opcional)',
        }
