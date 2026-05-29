from __future__ import annotations

from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import AgendaItem, Vote, VoteRecord


class AgendaItemForm(forms.ModelForm):
    """
    Formulário para criação e edição de itens de pauta de uma assembleia.

    Expõe os campos necessários para configurar o item: título, descrição,
    ordem, modo de votação, tipo de quórum e percentual mínimo de quórum.
    O campo ``assembly`` é preenchido pela view através de ``commit=False``.
    """

    class Meta:
        model = AgendaItem
        fields = [
            'title',
            'description',
            'order_index',
            'vote_mode',
            'quorum_type',
            'quorum_required',
        ]
        labels = {
            'title': 'Título',
            'description': 'Descrição',
            'order_index': 'Número de ordem',
            'vote_mode': 'Modo de votação',
            'quorum_type': 'Tipo de quórum',
            'quorum_required': 'Quórum mínimo (%)',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'order_index': forms.NumberInput(attrs={'min': 1}),
            'quorum_required': forms.NumberInput(attrs={'min': 1, 'max': 100}),
        }
        help_texts = {
            'order_index': 'Posição do item na pauta (deve ser único por assembleia).',
            'quorum_required': 'Percentual mínimo de votos para aprovação (1–100%).',
        }


class VoteOptionForm(forms.ModelForm):
    """Formulário para uma única opção de voto (rótulo)."""

    class Meta:
        model = Vote
        fields = ['label']
        labels = {'label': 'Rótulo da opção'}
        widgets = {
            'label': forms.TextInput(
                attrs={'placeholder': 'Ex.: Sim, Não, Abstenção'}
            )
        }


class BaseVoteOptionFormSet(BaseInlineFormSet):
    """
    FormSet base para opções de voto ligadas a um AgendaItem.

    Garante que ao menos uma opção de voto seja fornecida quando o formset
    é submetido com dados — caso contrário levanta ValidationError.
    """

    def clean(self) -> None:
        """Valida que pelo menos uma opção de voto foi preenchida."""
        if any(self.errors):
            return
        filled: int = sum(
            1
            for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False)
        )
        if filled < 1:
            raise forms.ValidationError(
                'Adicione pelo menos uma opção de voto (ex.: "Sim" e "Não").'
            )


# FormSet inline: cada AgendaItem pode ter N opções de Vote
VoteOptionFormSet = inlineformset_factory(
    parent_model=AgendaItem,
    model=Vote,
    form=VoteOptionForm,
    formset=BaseVoteOptionFormSet,
    fields=['label'],
    extra=2,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class VoteForm(forms.ModelForm):
    """
    Formulário para registrar o voto de um membro em um item de pauta.

    O campo ``vote`` é renderizado como um widget de radio buttons para que
    o membro selecione exatamente uma opção. As opções disponíveis são
    filtradas dinamicamente no ``__init__`` para exibir apenas as opções
    vinculadas ao ``AgendaItem`` correto.

    Campos não expostos pelo formulário (preenchidos pela view):
    - ``agenda_item`` — definido pela URL.
    - ``member`` — derivado do membro credenciado informado na view.
    - ``channel`` — inferido pelo canal de credenciamento do membro.
    - ``ip_address`` — capturado do ``request.META``.
    """

    class Meta:
        model = VoteRecord
        fields = ['vote', 'member']
        labels = {
            'vote': 'Sua escolha',
            'member': 'Membro votante',
        }
        widgets = {
            # Renderiza as opções como radio buttons sem a label padrão
            'vote': forms.RadioSelect(),
        }

    def __init__(self, *args, agenda_item: AgendaItem | None = None, **kwargs) -> None:
        """
        Inicializa o formulário filtrando as opções de voto pelo item de pauta.

        Args:
            agenda_item: O ``AgendaItem`` ativo cujas opções de voto serão exibidas.
        """
        super().__init__(*args, **kwargs)
        if agenda_item is not None:
            self.fields['vote'].queryset = Vote.objects.filter(
                agenda_item=agenda_item
            ).order_by('label')
            self.fields['vote'].empty_label = None  # sem opção em branco
        # Membro: select com membros credenciados — populado pela view
        self.fields['member'].required = True
        self.fields['member'].empty_label = 'Selecione o membro'
