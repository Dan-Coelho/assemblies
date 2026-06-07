from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from .models import Assembly, Convocation, Credential, Proxy
from .forms import AssemblyForm, ConvocationForm, CredentialForm, ProxyForm


class AssemblyListView(LoginRequiredMixin, ListView):
    """Lista assembleias com suporte a filtro por status."""

    model = Assembly
    template_name = 'assemblies/list.html'
    context_object_name = 'assemblies'

    def get_queryset(self):
        """Filtra assembleias pelo status passado via query string (?status=open)."""
        qs = Assembly.objects.select_related('organization')
        status = self.request.GET.get('status')
        if status and status in Assembly.Status.values:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs) -> dict:
        """Injeta os choices de status e o filtro ativo no contexto."""
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Assembly.Status.choices
        context['current_status'] = self.request.GET.get('status', '')
        return context


class AssemblyCreateView(LoginRequiredMixin, CreateView):
    """Formulário de criação de nova assembleia."""

    model = Assembly
    form_class = AssemblyForm
    template_name = 'assemblies/form.html'
    success_url = reverse_lazy('assembly_list')

    def form_valid(self, form):
        """Salva a assembleia com a organização já definida pelo formulário."""
        return super().form_valid(form)


class AssemblyDetailView(LoginRequiredMixin, DetailView):
    """Exibe os detalhes de uma assembleia com abas: pauta, credenciados e convocações."""

    model = Assembly
    template_name = 'assemblies/detail.html'
    context_object_name = 'assembly'

    def get_context_data(self, **kwargs) -> dict:
        """Injeta convocações, credenciais, procurações, membros e itens de pauta no contexto."""
        context = super().get_context_data(**kwargs)
        assembly = self.object
        context['convocations'] = assembly.convocations.order_by('-sent_at')
        context['credentials'] = assembly.credentials.select_related('member').order_by('-checked_in_at')
        context['proxies'] = assembly.proxies.select_related('grantor', 'proxy_member').order_by('-created_at')
        context['active_tab'] = self.request.GET.get('tab', 'pauta')

        from organizations.models import Member, MemberStatus
        org_members = Member.objects.filter(organization=assembly.organization).order_by('name')
        context['proxy_members'] = org_members
        context['credential_members'] = org_members.exclude(status=MemberStatus.INADIMPLENTE)

        # Itens de pauta com suas opções de voto pré-carregadas
        from votings.models import AgendaItem
        from votings.forms import AgendaItemForm, VoteOptionFormSet
        context['agenda_items'] = (
            assembly.agenda_items.prefetch_related('vote_options').order_by('order_index')
        )
        context['agenda_item_form'] = AgendaItemForm()
        context['vote_option_formset'] = VoteOptionFormSet()
        return context



class AssemblyUpdateView(LoginRequiredMixin, UpdateView):
    """Formulário de edição de uma assembleia existente."""

    model = Assembly
    form_class = AssemblyForm
    template_name = 'assemblies/form.html'

    def get_success_url(self) -> str:
        """Redireciona para a página de detalhe após a edição."""
        return reverse('assembly_detail', kwargs={'pk': self.object.pk})


# ── State Transition Views ────────────────────────────────────────────────────


class AssemblyStartView(LoginRequiredMixin, View):
    """
    Transitions an assembly from ``convoked`` to ``open`` (Em andamento).

    Validation: only assemblies with status ``convoked`` can be started.
    Records ``started_at`` with the current timestamp.
    """

    http_method_names = ['post']

    def post(self, request, pk):
        """Handle the start action, validate status and persist the transition."""
        assembly: Assembly = get_object_or_404(Assembly, pk=pk)

        if assembly.status != Assembly.Status.CONVOKED:
            messages.error(
                request,
                f'Não é possível iniciar a assembleia "{assembly.title}". '
                f'Apenas assembleias com status "Convocada" podem ser iniciadas '
                f'(status atual: {assembly.get_status_display()}).'
            )
            return HttpResponseRedirect(reverse('assembly_detail', kwargs={'pk': pk}))

        assembly.status = Assembly.Status.OPEN
        assembly.started_at = timezone.now()
        assembly.save(update_fields=['status', 'started_at', 'updated_at'])

        messages.success(
            request,
            f'Assembleia "{assembly.title}" iniciada com sucesso. Boa assembleia!'
        )
        return HttpResponseRedirect(reverse('assembly_detail', kwargs={'pk': pk}))


class AssemblyCloseView(LoginRequiredMixin, View):
    """
    Transitions an assembly from ``open`` to ``closed`` (Encerrada).

    Validation: only assemblies with status ``open`` can be closed.
    Records ``ended_at`` with the current timestamp.

    After persisting the status change, automatically generates a draft
    :class:`minutes.models.Minutes` document via
    :func:`minutes.utils.generate_minutes_content` if one does not yet
    exist for this assembly.
    """

    http_method_names = ['post']

    def post(self, request, pk):
        """Handle the close action, validate status, persist the transition and generate minutes."""
        assembly: Assembly = get_object_or_404(Assembly, pk=pk)

        if assembly.status != Assembly.Status.OPEN:
            messages.error(
                request,
                f'Não é possível encerrar a assembleia "{assembly.title}". '
                f'Apenas assembleias "Em andamento" podem ser encerradas '
                f'(status atual: {assembly.get_status_display()}).'
            )
            return HttpResponseRedirect(reverse('assembly_detail', kwargs={'pk': pk}))

        assembly.status = Assembly.Status.CLOSED
        assembly.ended_at = timezone.now()
        assembly.save(update_fields=['status', 'ended_at', 'updated_at'])

        # ── Auto-generate minutes draft (task 34.3) ───────────────────────────
        self._generate_minutes(assembly)

        messages.success(
            request,
            f'Assembleia "{assembly.title}" encerrada com sucesso. '
            f'A ata foi gerada automaticamente em rascunho.'
        )
        return HttpResponseRedirect(reverse('assembly_detail', kwargs={'pk': pk}))

    @staticmethod
    def _generate_minutes(assembly: Assembly) -> None:
        """
        Create a draft :class:`minutes.models.Minutes` for the given assembly.

        Calls :func:`minutes.utils.generate_minutes_content` to build the text
        content, then persists a new ``Minutes`` record (status ``draft``) with
        ``generated_at`` set to the current timestamp.

        If a ``Minutes`` record already exists for this assembly (e.g. the
        view is retried after a partial failure), the call is silently skipped
        to avoid ``IntegrityError`` from the ``OneToOneField``.

        Args:
            assembly: The assembly whose minutes should be generated.
        """
        from minutes.models import Minutes
        from minutes.utils import generate_minutes_content

        # Guard: skip if minutes already exist for this assembly
        if Minutes.objects.filter(assembly=assembly).exists():
            return

        content: str = generate_minutes_content(assembly)
        Minutes.objects.create(
            assembly=assembly,
            organization=assembly.organization,
            content=content,
            status=Minutes.Status.DRAFT,
            generated_at=timezone.now(),
        )


# ── Convocation Views ──────────────────────────────────────────────────────


class ConvocationCreateView(LoginRequiredMixin, View):
    """
    Registers a new convocation (convocação) for a specific assembly.

    Expects a POST request with the convocation form data. After saving,
    redirects back to the assembly detail page on the ``convocacoes`` tab.
    """

    http_method_names = ['post']

    def post(self, request, pk):
        """Validate and save the convocation, then redirect to the assembly detail."""
        assembly: Assembly = get_object_or_404(Assembly, pk=pk)
        form = ConvocationForm(request.POST)

        if form.is_valid():
            convocation: Convocation = form.save(commit=False)
            convocation.assembly = assembly
            convocation.organization = assembly.organization
            convocation.save()
            messages.success(
                request,
                f'Convocação via {convocation.get_channel_display()} registrada com sucesso.'
            )
        else:
            # Collect all field errors into a single readable message
            error_list = '; '.join(
                f'{field}: {", ".join(errs)}'
                for field, errs in form.errors.items()
            )
            messages.error(request, f'Erro ao registrar a convocação: {error_list}')

        return HttpResponseRedirect(
            reverse('assembly_detail', kwargs={'pk': pk}) + '?tab=convocacoes'
        )


# ── Proxy Views ────────────────────────────────────────────────────────────


class ProxyCreateView(LoginRequiredMixin, View):
    """
    Registers a new proxy authorization (procuração) for a specific assembly.

    Expects a POST request with the proxy form data. Calls ``full_clean()``
    to trigger model-level validations (grantor ≠ proxy_member, UniqueConstraint).
    After saving, redirects back to the assembly detail page on the ``procuracoes`` tab.
    """

    http_method_names = ['post']

    def post(self, request, pk):
        """Validate and save the proxy, then redirect to the assembly detail."""
        assembly: Assembly = get_object_or_404(Assembly, pk=pk)
        form = ProxyForm(request.POST, assembly=assembly)

        if form.is_valid():
            proxy: Proxy = form.save(commit=False)
            proxy.assembly = assembly
            proxy.organization = assembly.organization
            try:
                proxy.full_clean()
                proxy.save()
                messages.success(
                    request,
                    f'Procuração de {proxy.grantor} para {proxy.proxy_member} registrada com sucesso.'
                )
            except Exception as exc:
                error_msg = '; '.join(
                    str(v) for errors in getattr(exc, 'message_dict', {}).values() for v in errors
                ) or str(exc)
                messages.error(request, f'Erro ao registrar a procuração: {error_msg}')
        else:
            error_list = '; '.join(
                f'{field}: {", ".join(errs)}'
                for field, errs in form.errors.items()
            )
            messages.error(request, f'Erro ao registrar a procuração: {error_list}')

        return HttpResponseRedirect(
            reverse('assembly_detail', kwargs={'pk': pk}) + '?tab=procuracoes'
        )


# ── Credential Views ─────────────────────────────────────────────────────


class CredentialCreateView(LoginRequiredMixin, View):
    """
    Registers a new credential (credenciamento / check-in) for a member in an assembly.

    Business rules enforced:
    - Members with status ``inadimplente`` are blocked (RF-07.3) via ``full_clean()``.
    - Each member can have at most one credential per assembly (UniqueConstraint).
    - ``checked_in_at`` defaults to the current server time when not supplied.
    - The requester\'s IP address is captured automatically from the HTTP request.

    Redirects to the assembly detail page on the ``credenciados`` tab.
    """

    http_method_names = ['post']

    def post(self, request, pk):
        """Validate and save the credential, then redirect to the assembly detail."""
        assembly: Assembly = get_object_or_404(Assembly, pk=pk)
        form = CredentialForm(request.POST, assembly=assembly)

        if form.is_valid():
            credential: Credential = form.save(commit=False)
            credential.assembly = assembly
            credential.organization = assembly.organization

            # Default checked_in_at to now if not provided
            if not credential.checked_in_at:
                credential.checked_in_at = timezone.now()

            # Capture requester IP for online check-ins
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                credential.ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                credential.ip_address = request.META.get('REMOTE_ADDR')

            try:
                credential.full_clean()
                credential.save()
                messages.success(
                    request,
                    f'Membro {credential.member.name} credenciado com sucesso.'
                )
            except Exception as exc:
                error_msg = '; '.join(
                    str(v)
                    for errors in getattr(exc, 'message_dict', {}).values()
                    for v in errors
                ) or str(exc)
                messages.error(request, f'Erro ao credenciar membro: {error_msg}')
        else:
            error_list = '; '.join(
                f'{field}: {", ".join(errs)}'
                for field, errs in form.errors.items()
            )
            messages.error(request, f'Erro ao credenciar membro: {error_list}')

        return HttpResponseRedirect(
            reverse('assembly_detail', kwargs={'pk': pk}) + '?tab=credenciados'
        )
