"""
Views for the ``minutes`` application.

Provides display, approval and signature registration for the official
minutes (ata) of a general assembly.
"""

from __future__ import annotations

import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView

from .models import Minutes, MinuteSignature

logger = logging.getLogger(__name__)


class MinutesDetailView(LoginRequiredMixin, DetailView):
    """
    Display the full content of the official minutes for an assembly.

    Fetches the ``Minutes`` instance by primary key and renders the
    ``minutes/detail.html`` template.  Also injects into context:

    - ``signatures``: queryset of :class:`MinuteSignature` records for
      this minutes document, ordered by ``signed_at``.
    - ``assembly``: the parent :class:`assemblies.Assembly` instance for
      breadcrumb and navigation.
    - ``members``: all active members of the organisation, used to
      populate the sign form select.
    - ``already_signed_ids``: set of member UUIDs who have already signed,
      used to disable the sign button for members who have already signed.
    """

    model = Minutes
    template_name = 'minutes/detail.html'
    context_object_name = 'minutes'

    def get_context_data(self, **kwargs) -> dict:
        """Inject signatures, assembly and member data into the template context."""
        context = super().get_context_data(**kwargs)
        minutes: Minutes = self.object
        signatures = minutes.signatures.select_related('member').order_by('signed_at')
        context['signatures'] = signatures
        context['assembly'] = minutes.assembly
        context['already_signed_ids'] = set(
            signatures.values_list('member_id', flat=True)
        )

        from organizations.models import Member, MemberStatus
        context['members'] = Member.objects.filter(
            organization=minutes.organization,
            status=MemberStatus.ATIVO,
        ).order_by('name')

        return context


class MinutesApproveView(LoginRequiredMixin, View):
    """
    Transition the minutes status from ``draft`` to ``approved``.

    Only minutes in ``draft`` status can be approved.  Once approved,
    the document becomes immutable (enforced at the model layer via
    :meth:`minutes.models.Minutes.save`).

    Redirects back to :class:`MinutesDetailView` after the action.
    """

    http_method_names = ['post']

    def post(self, request, pk) -> HttpResponseRedirect:
        """Validate the current status, approve the minutes and redirect."""
        minutes: Minutes = get_object_or_404(Minutes, pk=pk)

        if minutes.status != Minutes.Status.DRAFT:
            messages.error(
                request,
                f'A ata já está "{minutes.get_status_display()}" e não pode ser aprovada novamente.',
            )
            return HttpResponseRedirect(reverse('minutes_detail', kwargs={'pk': pk}))

        minutes.status = Minutes.Status.APPROVED
        minutes.save()

        logger.info(
            'minutes.approved: pk=%s assembly=%s user=%s',
            minutes.pk,
            minutes.assembly_id,
            request.user.pk,
        )
        messages.success(
            request,
            'Ata aprovada com sucesso. O documento está agora bloqueado para edição.',
        )
        return HttpResponseRedirect(reverse('minutes_detail', kwargs={'pk': pk}))


class MinutesSignView(LoginRequiredMixin, View):
    """
    Register a member's signature on a set of minutes.

    Expects a POST with ``member_id`` and an optional ``role`` field.
    Creates a :class:`MinuteSignature` record, which auto-generates the
    ``signature_token`` and populates ``signed_at`` via the model's
    :meth:`~minutes.models.MinuteSignature.save` method.

    Business rules:
    - The minutes must not be in ``approved`` status for new signatures
      to be accepted (approved minutes are immutable).
    - A member may only sign once (enforced by ``UniqueConstraint``).

    Redirects back to :class:`MinutesDetailView` after the action.
    """

    http_method_names = ['post']

    def post(self, request, pk) -> HttpResponseRedirect:
        """Validate inputs, create the signature record and redirect."""
        minutes: Minutes = get_object_or_404(Minutes, pk=pk)
        member_id: str = request.POST.get('member_id', '').strip()
        role: str = request.POST.get('role', '').strip()

        if not member_id:
            messages.error(request, 'Selecione um membro para assinar a ata.')
            return HttpResponseRedirect(reverse('minutes_detail', kwargs={'pk': pk}))

        from organizations.models import Member
        member: Member = get_object_or_404(
            Member, pk=member_id, organization=minutes.organization
        )

        # Check if already signed
        if MinuteSignature.objects.filter(minutes=minutes, member=member).exists():
            messages.error(
                request,
                f'{member.name} já assinou esta ata.',
            )
            return HttpResponseRedirect(reverse('minutes_detail', kwargs={'pk': pk}))

        try:
            MinuteSignature.objects.create(
                minutes=minutes,
                member=member,
                organization=minutes.organization,
                role=role or member.get_role_display(),
            )
            logger.info(
                'minutes.signed: minutes_pk=%s member=%s user=%s',
                minutes.pk,
                member.pk,
                request.user.pk,
            )
            messages.success(
                request,
                f'Assinatura de {member.name} registrada com sucesso.',
            )
        except Exception as exc:
            logger.exception('minutes.sign.error: %s', exc)
            messages.error(request, f'Erro ao registrar a assinatura: {exc}')

        return HttpResponseRedirect(reverse('minutes_detail', kwargs={'pk': pk}))
