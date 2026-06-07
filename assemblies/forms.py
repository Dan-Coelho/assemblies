from django import forms

from .models import Assembly, Convocation, Credential, Proxy
from organizations.models import Organization


class AssemblyForm(forms.ModelForm):
    """Formulário para criação e edição de assembleias."""

    class Meta:
        model = Assembly
        fields = [
            'organization',
            'title',
            'description',
            'status',
            'mode',
            'scheduled_at',
            'quorum_required',
            'location',
            'meeting_url',
        ]
        labels = {
            'organization': 'Organização',
            'title': 'Título',
            'description': 'Descrição',
            'status': 'Status',
            'mode': 'Modalidade',
            'scheduled_at': 'Data e hora agendada',
            'quorum_required': 'Quórum necessário (%)',
            'location': 'Local',
            'meeting_url': 'URL da reunião',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'scheduled_at': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Format the initial value for the datetime-local input
        if self.instance and self.instance.scheduled_at:
            self.initial['scheduled_at'] = self.instance.scheduled_at.strftime('%Y-%m-%dT%H:%M')
        # Ensure empty label is set for the organization select
        self.fields['organization'].empty_label = 'Selecione a organização'
        self.fields['organization'].queryset = Organization.objects.order_by('name')


class ConvocationForm(forms.ModelForm):
    """Formulário para registro de uma convocação de assembleia."""

    class Meta:
        model = Convocation
        fields = ['channel', 'is_second_call', 'sent_at', 'notes']
        labels = {
            'channel': 'Canal de envio',
            'is_second_call': 'Segunda convocação',
            'sent_at': 'Data/hora de envio',
            'notes': 'Observações',
        }
        widgets = {
            'sent_at': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.sent_at:
            self.initial['sent_at'] = self.instance.sent_at.strftime('%Y-%m-%dT%H:%M')


class ProxyForm(forms.ModelForm):
    """Formulário para registro de procuração (proxy) em uma assembleia."""

    class Meta:
        model = Proxy
        fields = ['grantor', 'proxy_member', 'document_url', 'is_active']
        labels = {
            'grantor': 'Outorgante',
            'proxy_member': 'Procurador',
            'document_url': 'URL do documento',
            'is_active': 'Procuração ativa',
        }
        widgets = {
            'document_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
        }

    def __init__(self, *args, assembly=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if assembly is not None:
            from organizations.models import Member

            org_members = Member.objects.filter(organization=assembly.organization).order_by('name')
            self.fields['grantor'].queryset = org_members
            self.fields['proxy_member'].queryset = org_members
        self.fields['grantor'].empty_label = 'Selecione o outorgante'
        self.fields['proxy_member'].empty_label = 'Selecione o procurador'


class CredentialForm(forms.ModelForm):
    """Formulário para registro de credenciamento (check-in) em uma assembleia."""

    class Meta:
        model = Credential
        fields = ['member', 'channel', 'checked_in_at']
        labels = {
            'member': 'Membro',
            'channel': 'Canal de check-in',
            'checked_in_at': 'Data/hora do check-in',
        }
        widgets = {
            'checked_in_at': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
        }

    def __init__(self, *args, assembly=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if assembly is not None:
            from organizations.models import Member, MemberStatus

            # Exclui inadimplentes do select; model.clean() reforça essa regra
            self.fields['member'].queryset = (
                Member.objects.filter(organization=assembly.organization)
                .exclude(status=MemberStatus.INADIMPLENTE)
                .order_by('name')
            )
        self.fields['member'].empty_label = 'Selecione o membro'
        self.fields['checked_in_at'].required = False

