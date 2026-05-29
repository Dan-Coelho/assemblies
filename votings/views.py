from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, UpdateView

from assemblies.models import Assembly
from .forms import AgendaItemForm, VoteOptionFormSet, VoteForm
from .models import AgendaItem, VoteRecord


# ── AgendaItem Create ─────────────────────────────────────────────────────────


class AgendaItemCreateView(LoginRequiredMixin, View):
    """
    Cria um novo item de pauta (AgendaItem) para uma assembleia específica.

    Processa um formulário POST com ``AgendaItemForm`` e ``VoteOptionFormSet``
    para persistir o item e suas opções de voto de forma atômica.
    Redireciona de volta à aba de pauta do detalhe da assembleia.

    Validações:
    - A assembleia não pode ter status ``closed`` ou ``cancelled``.
    - O item herda ``assembly`` e ``organization`` da assembleia pai.
    - O formset exige ao menos uma opção de voto.
    """

    http_method_names = ['post']

    def post(self, request, assembly_pk: str) -> HttpResponseRedirect:
        """Valida e persiste o item de pauta junto com as opções de voto."""
        assembly: Assembly = get_object_or_404(Assembly, pk=assembly_pk)

        if assembly.status in (Assembly.Status.CLOSED, Assembly.Status.CANCELLED):
            messages.error(
                request,
                'Não é possível adicionar itens de pauta a uma assembleia encerrada ou cancelada.',
            )
            return HttpResponseRedirect(
                reverse('assembly_detail', kwargs={'pk': assembly_pk}) + '?tab=pauta'
            )

        form = AgendaItemForm(request.POST)
        formset = VoteOptionFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            item: AgendaItem = form.save(commit=False)
            item.assembly = assembly
            item.organization = assembly.organization
            try:
                item.full_clean()
                item.save()
                # Vincular as opções de voto ao item salvo
                formset.instance = item
                formset.save()
                messages.success(
                    request,
                    f'Item de pauta "{item.title}" adicionado com sucesso.',
                )
            except Exception as exc:
                error_msg = '; '.join(
                    str(v)
                    for errors in getattr(exc, 'message_dict', {}).values()
                    for v in errors
                ) or str(exc)
                messages.error(request, f'Erro ao adicionar item de pauta: {error_msg}')
        else:
            all_errors: list[str] = []
            for field, errs in form.errors.items():
                all_errors.append(f'{field}: {", ".join(errs)}')
            for fe in formset.errors:
                for field, errs in fe.items():
                    all_errors.append(f'{field}: {", ".join(errs)}')
            if formset.non_form_errors():
                all_errors.extend(formset.non_form_errors())
            messages.error(
                request,
                'Erro ao adicionar item de pauta: ' + '; '.join(all_errors),
            )

        return HttpResponseRedirect(
            reverse('assembly_detail', kwargs={'pk': assembly_pk}) + '?tab=pauta'
        )


# ── AgendaItem Update ─────────────────────────────────────────────────────────


class AgendaItemUpdateView(LoginRequiredMixin, View):
    """
    Atualiza título, descrição, ordem e configurações de um item de pauta existente.

    Só é permitido editar itens com status ``pending``. Itens ``open`` ou
    ``closed`` não podem ser editados (retorna mensagem de erro).
    Redireciona de volta à aba de pauta.
    """

    http_method_names = ['post']

    def post(self, request, assembly_pk: str, pk: str) -> HttpResponseRedirect:
        """Valida e atualiza o item de pauta."""
        assembly: Assembly = get_object_or_404(Assembly, pk=assembly_pk)
        item: AgendaItem = get_object_or_404(AgendaItem, pk=pk, assembly=assembly)

        if item.status != AgendaItem.Status.PENDING:
            messages.error(
                request,
                f'O item "{item.title}" não pode ser editado pois está com status '
                f'"{item.get_status_display()}". Apenas itens pendentes podem ser editados.',
            )
            return HttpResponseRedirect(
                reverse('assembly_detail', kwargs={'pk': assembly_pk}) + '?tab=pauta'
            )

        form = AgendaItemForm(request.POST, instance=item)
        formset = VoteOptionFormSet(request.POST, instance=item)

        if form.is_valid() and formset.is_valid():
            try:
                updated_item: AgendaItem = form.save(commit=False)
                updated_item.full_clean()
                updated_item.save()
                formset.save()
                messages.success(
                    request,
                    f'Item de pauta "{updated_item.title}" atualizado com sucesso.',
                )
            except Exception as exc:
                error_msg = '; '.join(
                    str(v)
                    for errors in getattr(exc, 'message_dict', {}).values()
                    for v in errors
                ) or str(exc)
                messages.error(request, f'Erro ao atualizar item de pauta: {error_msg}')
        else:
            all_errors: list[str] = []
            for field, errs in form.errors.items():
                all_errors.append(f'{field}: {", ".join(errs)}')
            for fe in formset.errors:
                for field, errs in fe.items():
                    all_errors.append(f'{field}: {", ".join(errs)}')
            if formset.non_form_errors():
                all_errors.extend(formset.non_form_errors())
            messages.error(
                request,
                'Erro ao atualizar item de pauta: ' + '; '.join(all_errors),
            )

        return HttpResponseRedirect(
            reverse('assembly_detail', kwargs={'pk': assembly_pk}) + '?tab=pauta'
        )


# ── AgendaItem Open (pending → open) ─────────────────────────────────────────


class AgendaItemOpenView(LoginRequiredMixin, View):
    """
    Abre a votação de um item de pauta (muda status de ``pending`` para ``open``).

    Validações:
    - A assembleia deve estar com status ``open`` (em andamento).
    - O item deve estar com status ``pending``.
    - Registra ``opened_at`` com o timestamp atual.

    Redireciona para a aba de pauta da assembleia.
    """

    http_method_names = ['post']

    def post(self, request, assembly_pk: str, pk: str) -> HttpResponseRedirect:
        """Transiciona o item de ``pending`` para ``open``."""
        assembly: Assembly = get_object_or_404(Assembly, pk=assembly_pk)
        item: AgendaItem = get_object_or_404(AgendaItem, pk=pk, assembly=assembly)

        if assembly.status != Assembly.Status.OPEN:
            messages.error(
                request,
                'Só é possível iniciar uma votação durante uma assembleia em andamento.',
            )
            return HttpResponseRedirect(
                reverse('assembly_detail', kwargs={'pk': assembly_pk}) + '?tab=pauta'
            )

        if item.status != AgendaItem.Status.PENDING:
            messages.error(
                request,
                f'O item "{item.title}" não pode ser aberto pois está com status '
                f'"{item.get_status_display()}". Apenas itens pendentes podem ser iniciados.',
            )
            return HttpResponseRedirect(
                reverse('assembly_detail', kwargs={'pk': assembly_pk}) + '?tab=pauta'
            )

        item.status = AgendaItem.Status.OPEN
        item.opened_at = timezone.now()
        item.save(update_fields=['status', 'opened_at', 'updated_at'])

        messages.success(
            request,
            f'Votação do item "{item.title}" iniciada. Os membros já podem votar.',
        )
        return HttpResponseRedirect(
            reverse('assembly_detail', kwargs={'pk': assembly_pk}) + '?tab=pauta'
        )


# ── AgendaItem Close (open → closed) ─────────────────────────────────────────


class AgendaItemCloseView(LoginRequiredMixin, View):
    """
    Encerra a votação de um item de pauta (muda status de ``open`` para ``closed``).

    Validações:
    - O item deve estar com status ``open``.
    - Registra ``closed_at`` com o timestamp atual.

    Após encerrar, o resultado parcial/final fica disponível via
    ``item.get_result()`` e é exibido em tempo real na aba de pauta.

    Redireciona para a aba de pauta da assembleia.
    """

    http_method_names = ['post']

    def post(self, request, assembly_pk: str, pk: str) -> HttpResponseRedirect:
        """Transiciona o item de ``open`` para ``closed`` e registra o horário de encerramento."""
        assembly: Assembly = get_object_or_404(Assembly, pk=assembly_pk)
        item: AgendaItem = get_object_or_404(AgendaItem, pk=pk, assembly=assembly)

        if item.status != AgendaItem.Status.OPEN:
            messages.error(
                request,
                f'O item "{item.title}" não pode ser encerrado pois está com status '
                f'"{item.get_status_display()}". Apenas itens em votação podem ser encerrados.',
            )
            return HttpResponseRedirect(
                reverse('assembly_detail', kwargs={'pk': assembly_pk}) + '?tab=pauta'
            )

        item.status = AgendaItem.Status.CLOSED
        item.closed_at = timezone.now()
        item.save(update_fields=['status', 'closed_at', 'updated_at'])

        # Resumo do resultado para a mensagem de feedback
        result: list[dict] = item.get_result()
        if result:
            winner = result[0]
            summary = (
                f'Resultado: "{winner["label"]}" venceu com {winner["count"]} '
                f'voto(s) ({winner["percentage"]}%).'
            )
        else:
            summary = 'Nenhum voto registrado neste item.'

        messages.success(
            request,
            f'Votação do item "{item.title}" encerrada. {summary}',
        )
        return HttpResponseRedirect(
            reverse('assembly_detail', kwargs={'pk': assembly_pk}) + '?tab=pauta'
        )


# ── Cast Vote ─────────────────────────────────────────────────────────────────


class CastVoteView(LoginRequiredMixin, View):
    """
    Exibe a tela de votação (GET) e registra o voto de um membro (POST).

    Fluxo GET:
    - Exibe o ``AgendaItem`` com suas opções de voto como radio buttons.
    - Lista os membros credenciados na assembleia para seleção.
    - Exibe o placar parcial (apenas contagens, sem percentuais) enquanto a
      votação estiver em aberto, conforme RF-08.

    Fluxo POST (31.3 — chama ``full_clean()`` antes do ``save()``):
    - Valida o formulário ``VoteForm``.
    - Constrói o ``VoteRecord`` com ``commit=False`` e preenche os campos
      automáticos (``agenda_item``, ``channel``, ``ip_address``).
    - Chama ``full_clean()`` para acionar todas as validações do model
      (inadimplência, credencial, duplo voto, item aberto, etc.).
    - Chama ``save()`` que grava o registro de forma imutável e chama
      ``Vote.increment()`` atomicamente.
    - Exibe mensagem de confirmação (31.5) e redireciona para a tela de
      votação, que já mostra o placar parcial atualizado (31.6).

    Regras de negócio delegadas ao model ``VoteRecord.clean()``:
    - Item deve estar com status ``open``.
    - Membro deve ter credencial para a assembleia.
    - Membro inadimplente é bloqueado.
    - Duplo voto é impedido (modo aberto e secreto).
    - Opção de voto deve pertencer ao item.
    """

    template_name = 'votings/cast_vote.html'

    def _get_objects(self, assembly_pk: str, item_pk: str):
        """Atalho para buscar a assembleia e o item de pauta."""
        assembly: Assembly = get_object_or_404(Assembly, pk=assembly_pk)
        item: AgendaItem = get_object_or_404(AgendaItem, pk=item_pk, assembly=assembly)
        return assembly, item

    def _build_context(self, assembly: Assembly, item: AgendaItem, form: VoteForm) -> dict:
        """Monta o contexto comum para o template de votação."""
        from assemblies.models import Credential

        # Membros credenciados nesta assembleia (para o select de membro)
        credentials = (
            Credential.objects
            .filter(assembly=assembly)
            .select_related('member')
            .order_by('member__name')
        )
        credentialed_members = [c.member for c in credentials]

        # Placar parcial: contagens sem percentual (RF-08 — placar durante votação aberta)
        partial_scores: list[dict] = []
        for option in item.vote_options.order_by('label'):
            partial_scores.append({
                'label': option.label,
                'count': option.total_count,
                'pk': option.pk,
            })

        return {
            'assembly': assembly,
            'item': item,
            'form': form,
            'credentialed_members': credentialed_members,
            'partial_scores': partial_scores,
            'total_votes': item.total_votes,
        }

    def get(self, request, assembly_pk: str, item_pk: str):
        """Renderiza a tela de votação com as opções e o placar parcial."""
        assembly, item = self._get_objects(assembly_pk, item_pk)

        if item.status != AgendaItem.Status.OPEN:
            messages.error(
                request,
                f'O item "{item.title}" não está em votação '
                f'(status: {item.get_status_display()}).',
            )
            return HttpResponseRedirect(
                reverse('assembly_detail', kwargs={'pk': assembly_pk}) + '?tab=pauta'
            )

        form = VoteForm(agenda_item=item)
        context = self._build_context(assembly, item, form)
        return render(request, self.template_name, context)

    def post(self, request, assembly_pk: str, item_pk: str):
        """
        Registra o voto do membro.

        Validações:
        1. O item deve estar com status ``open``.
        2. Chama ``VoteRecord.full_clean()`` para acionar todas as regras de negócio.
        3. Somente então chama ``save()`` (imutável, dispara ``Vote.increment()``).
        """
        assembly, item = self._get_objects(assembly_pk, item_pk)

        if item.status != AgendaItem.Status.OPEN:
            messages.error(
                request,
                f'O item "{item.title}" não está em votação.',
            )
            return HttpResponseRedirect(
                reverse('assembly_detail', kwargs={'pk': assembly_pk}) + '?tab=pauta'
            )

        form = VoteForm(request.POST, agenda_item=item)

        # Filtrar membros credenciados para o select do formulário
        from assemblies.models import Credential
        from organizations.models import Member

        credentials_qs = Credential.objects.filter(assembly=assembly).select_related('member')
        credentialed_member_ids = list(credentials_qs.values_list('member_id', flat=True))
        form.fields['member'].queryset = Member.objects.filter(pk__in=credentialed_member_ids)

        if form.is_valid():
            record: VoteRecord = form.save(commit=False)
            record.agenda_item = item

            # Inferir o canal a partir do credenciamento do membro
            member = record.member
            credential = credentials_qs.filter(member=member).first()
            record.channel = credential.channel if credential else 'presencial'

            # Capturar IP do requisitante
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                record.ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                record.ip_address = request.META.get('REMOTE_ADDR')

            try:
                # 31.3 — Chama full_clean() antes do save() para acionar clean()
                record.full_clean()
                record.save()

                # 31.5 — Confirmação de voto registrado
                if item.is_secret:
                    confirmation_msg = (
                        f'✓ Voto registrado com sucesso para o item "{item.title}". '
                        f'O modo de votação é secreto — sua identidade não é armazenada.'
                    )
                else:
                    confirmation_msg = (
                        f'✓ Voto de {member.name} registrado com sucesso '
                        f'para o item "{item.title}".'
                    )
                messages.success(request, confirmation_msg)

                # Redirecionar de volta para a tela de votação (que exibirá o placar atualizado)
                return HttpResponseRedirect(
                    reverse('cast_vote', kwargs={'assembly_pk': assembly_pk, 'item_pk': item_pk})
                )

            except Exception as exc:
                error_msg = '; '.join(
                    str(v)
                    for errors in getattr(exc, 'message_dict', {}).values()
                    for v in errors
                ) or str(exc)
                messages.error(request, f'Não foi possível registrar o voto: {error_msg}')
        else:
            error_list = '; '.join(
                f'{field}: {", ".join(errs)}'
                for field, errs in form.errors.items()
            )
            messages.error(request, f'Formulário inválido: {error_list}')

        context = self._build_context(assembly, item, form)
        return render(request, self.template_name, context)
