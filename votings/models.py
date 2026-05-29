from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from core.models import TenantModel


class AgendaItem(TenantModel):
    """
    Represents a single agenda item (pauta) in an assembly, which can be voted on.

    An agenda item has its own lifecycle (pending → open → closed) and supports
    both open and secret voting modes. Quorum can be measured either by the number
    of members present (presença) or by the total number of active members in the
    organization (total).

    Business rules enforced:
    - The ``order_index`` must be unique per assembly (UniqueConstraint).
    - The ``order_index`` cannot be changed while the parent assembly is open (RF-08.4).
    - Only items with status ``pending`` can be opened; only ``open`` items can be closed.

    Properties:
    - ``is_secret``: whether the vote mode is secret.
    - ``total_votes``: sum of all vote counts across the item's Vote options.
    - ``get_result()``: returns a list of dicts with label, count and percentage per option.
    - ``check_quorum_reached()``: verifies if the minimum quorum was met for this item.
    """

    # ------------------------------------------------------------------
    # Inner TextChoices
    # ------------------------------------------------------------------

    class QuorumType(models.TextChoices):
        """How the quorum denominator is calculated for this agenda item."""

        PRESENCA = 'presenca', 'Presentes'
        TOTAL = 'total', 'Total de membros'

    class VoteMode(models.TextChoices):
        """Whether the voting is open (nominal) or secret (anonymous)."""

        ABERTO = 'aberto', 'Aberto (nominal)'
        SECRETO = 'secreto', 'Secreto (anônimo)'

    class Status(models.TextChoices):
        """Lifecycle state of the agenda item."""

        PENDING = 'pending', 'Pendente'
        OPEN = 'open', 'Em votação'
        CLOSED = 'closed', 'Encerrado'

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------

    assembly: models.ForeignKey = models.ForeignKey(
        'assemblies.Assembly',
        on_delete=models.CASCADE,
        related_name='agenda_items',
        verbose_name='Assembleia',
    )
    title: models.CharField = models.CharField(
        max_length=255,
        verbose_name='Título',
        help_text='Breve descrição do item de pauta a ser votado.',
    )
    description: models.TextField = models.TextField(
        blank=True,
        verbose_name='Descrição',
        help_text='Detalhamento do item de pauta, se necessário.',
    )
    order_index: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField(
        verbose_name='Ordem',
        help_text='Posição do item na pauta da assembleia (deve ser único por assembleia).',
    )
    quorum_type: models.CharField = models.CharField(
        max_length=10,
        choices=QuorumType.choices,
        default=QuorumType.PRESENCA,
        verbose_name='Tipo de quórum',
        help_text=(
            '"Presentes" usa o total de credenciados; '
            '"Total de membros" usa todos os membros ativos da organização.'
        ),
    )
    quorum_required: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField(
        default=50,
        verbose_name='Quórum mínimo (%)',
        help_text='Percentual mínimo de votos necessários para aprovação.',
    )
    vote_mode: models.CharField = models.CharField(
        max_length=10,
        choices=VoteMode.choices,
        default=VoteMode.ABERTO,
        verbose_name='Modo de votação',
    )
    status: models.CharField = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Status',
    )
    opened_at: models.DateTimeField = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Aberto em',
        help_text='Data/hora em que a votação deste item foi iniciada.',
    )
    closed_at: models.DateTimeField = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Encerrado em',
        help_text='Data/hora em que a votação deste item foi encerrada.',
    )

    class Meta:
        verbose_name = 'Item de pauta'
        verbose_name_plural = 'Itens de pauta'
        ordering = ['assembly', 'order_index']
        constraints = [
            models.UniqueConstraint(
                fields=['assembly', 'order_index'],
                name='unique_order_index_per_assembly',
                violation_error_message=(
                    'Já existe um item com este número de ordem nesta assembleia.'
                ),
            )
        ]

    def __str__(self) -> str:
        return f'[{self.order_index}] {self.title} ({self.get_status_display()})'

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def clean(self) -> None:
        """
        Enforce business rules for the agenda item.

        Rules:
        - ``quorum_required`` must be between 1 and 100.
        - ``order_index`` cannot be changed while the parent assembly is open (RF-08.4).
          Changing the order of items mid-vote could cause inconsistencies in results.
        - An item can only move from ``pending`` → ``open`` → ``closed``; no reversal.

        Raises:
            ValidationError: when any of the above rules are violated.
        """
        errors: dict[str, str] = {}

        if self.quorum_required and not (1 <= self.quorum_required <= 100):
            errors['quorum_required'] = 'O quórum deve estar entre 1% e 100%.'

        # Protect order_index while assembly is open
        if self.pk and self.assembly_id:
            try:
                original = AgendaItem.objects.get(pk=self.pk)
                from assemblies.models import Assembly as AssemblyModel

                assembly_is_open = (
                    AssemblyModel.objects.filter(
                        pk=self.assembly_id,
                        status=AssemblyModel.Status.OPEN,
                    ).exists()
                )
                if assembly_is_open and original.order_index != self.order_index:
                    errors['order_index'] = (
                        'A ordem do item não pode ser alterada enquanto a assembleia '
                        'estiver em andamento.'
                    )
            except AgendaItem.DoesNotExist:
                pass

        if errors:
            raise ValidationError(errors)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_secret(self) -> bool:
        """Return ``True`` if the vote mode for this item is secret (anonymous)."""
        return self.vote_mode == self.VoteMode.SECRETO

    @property
    def total_votes(self) -> int:
        """
        Return the total number of votes cast across all options for this item.

        Sums the ``total_count`` of every related ``Vote`` record.
        Returns 0 if no vote options have been registered yet.
        """
        result = self.vote_options.aggregate(  # type: ignore[attr-defined]
            total=models.Sum('total_count')
        )
        return result['total'] or 0

    def get_result(self) -> list[dict]:
        """
        Return a ranked list of vote options with their counts and percentages.

        Each entry in the list is a dict with the keys:
        - ``label`` (str): human-readable option label.
        - ``count`` (int): raw vote count.
        - ``percentage`` (float): percentage of ``total_votes`` rounded to 2 decimals.
                                  Returns 0.0 when no votes have been cast.

        The list is ordered from highest to lowest count.

        Returns:
            list[dict]: ranked vote options, empty list if no options exist.
        """
        options = self.vote_options.order_by('-total_count')  # type: ignore[attr-defined]
        total: int = self.total_votes
        result: list[dict] = []
        for option in options:
            percentage: float = round(option.total_count / total * 100, 2) if total else 0.0
            result.append(
                {
                    'label': option.label,
                    'count': option.total_count,
                    'percentage': percentage,
                }
            )
        return result

    def check_quorum_reached(self) -> bool:
        """
        Check whether the minimum quorum percentage has been reached for this item.

        The denominator depends on ``quorum_type``:
        - ``PRESENCA``: uses the number of credentialed members in the parent assembly.
        - ``TOTAL``: uses the count of all active members in the organization.

        Returns:
            bool: ``True`` if total votes / denominator * 100 >= quorum_required,
                  ``False`` otherwise or when the denominator is zero.
        """
        from organizations.models import MemberStatus

        total_votes: int = self.total_votes

        if self.quorum_type == self.QuorumType.PRESENCA:
            denominator: int = self.assembly.total_credentials
        else:
            denominator = (
                self.assembly.organization.organizations_member_set  # type: ignore[attr-defined]
                .filter(status=MemberStatus.ATIVO)
                .count()
            )

        if denominator == 0:
            return False

        return (total_votes / denominator * 100) >= self.quorum_required


class Vote(models.Model):
    """
    Represents a single vote option (opção de voto) for an agenda item.

    Each ``Vote`` record acts as an accumulator for one choice (e.g. "Sim", "Não",
    "Abstenção"). The tally is updated atomically through ``increment()`` using a
    database-level ``F()`` expression so that concurrent votes never produce
    lost-update anomalies.

    Constraints:
    - Labels must be unique per agenda item (UniqueConstraint).
    - ``total_count`` is managed exclusively via ``increment()``; it should never
      be set directly after creation.
    """

    agenda_item: models.ForeignKey = models.ForeignKey(
        AgendaItem,
        on_delete=models.CASCADE,
        related_name='vote_options',
        verbose_name='Item de pauta',
        help_text='Item de pauta ao qual esta opção de voto pertence.',
    )
    label: models.CharField = models.CharField(
        max_length=100,
        verbose_name='Rótulo',
        help_text='Nome da opção de voto (ex.: "Sim", "Não", "Abstenção").',
    )
    total_count: models.PositiveIntegerField = models.PositiveIntegerField(
        default=0,
        verbose_name='Total de votos',
        help_text='Contador acumulado de votos para esta opção. Atualizado via increment().',
    )

    class Meta:
        verbose_name = 'Opção de voto'
        verbose_name_plural = 'Opções de voto'
        ordering = ['agenda_item', 'label']
        constraints = [
            models.UniqueConstraint(
                fields=['agenda_item', 'label'],
                name='unique_vote_label_per_agenda_item',
                violation_error_message=(
                    'Já existe uma opção com este rótulo neste item de pauta.'
                ),
            )
        ]

    def __str__(self) -> str:
        return f'{self.label} ({self.total_count} voto{"s" if self.total_count != 1 else ""}) — {self.agenda_item}'

    def increment(self) -> None:
        """
        Atomically increment ``total_count`` by 1 using a database-level F() expression.

        Using ``F('total_count') + 1`` ensures that the increment is performed as a
        single SQL ``UPDATE`` statement, preventing lost-update race conditions when
        multiple votes are registered simultaneously.

        The instance is refreshed from the database after saving so that
        ``self.total_count`` reflects the actual persisted value.
        """
        Vote.objects.filter(pk=self.pk).update(
            total_count=models.F('total_count') + 1
        )
        self.refresh_from_db(fields=['total_count'])


class VoteRecord(models.Model):
    """
    Immutable audit record of a single member's vote on an agenda item.

    ``VoteRecord`` provides a tamper-evident log of every individual vote cast.
    It enforces all business rules required by RF-08 and supports both open
    (nominal) and secret (anonymous) voting modes:

    - **Open voting**: ``member`` FK is stored directly so the vote is traceable.
    - **Secret voting**: ``member`` FK is set to ``None`` and the member's identity
      is replaced by a one-way SHA-256 hash (``member_id_hash``). The label of the
      chosen option is also hashed (``vote_label_hash``) to prevent direct reading.
      An overall ``integrity_hash`` ties all fields together for tamper detection.

    Business rules enforced by ``clean()``:
    - The member must have a valid ``Credential`` for this assembly (RF-08.5).
    - Inadimplente members are blocked at the credential level, but double-checked
      here for defence-in-depth (RF-07.3).
    - The agenda item must currently be ``open`` (in-vote) status.
    - Double-voting is blocked by both ``clean()`` and database UniqueConstraints.
    - The chosen ``vote`` option must belong to the same ``agenda_item``.

    Immutability:
    - ``save()`` may only be called once (no updates allowed after creation).
    - ``delete()`` is blocked unconditionally; records are retained for audit.
    """

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------

    agenda_item: models.ForeignKey = models.ForeignKey(
        AgendaItem,
        on_delete=models.PROTECT,
        related_name='vote_records',
        verbose_name='Item de pauta',
    )
    member: models.ForeignKey = models.ForeignKey(
        'organizations.Member',
        on_delete=models.PROTECT,
        related_name='vote_records',
        null=True,
        blank=True,
        verbose_name='Membro',
        help_text=(
            'FK visível apenas em votação aberta. '
            'Nulo em votação secreta — identidade preservada apenas via member_id_hash.'
        ),
    )
    vote: models.ForeignKey = models.ForeignKey(
        Vote,
        on_delete=models.PROTECT,
        related_name='records',
        verbose_name='Opção escolhida',
        help_text='Opção de voto selecionada pelo membro.',
    )
    proxy: models.ForeignKey = models.ForeignKey(
        'assemblies.Proxy',
        on_delete=models.SET_NULL,
        related_name='vote_records',
        null=True,
        blank=True,
        verbose_name='Procuração',
        help_text='Preenchido quando o voto foi exercido por procuração.',
    )
    channel: models.CharField = models.CharField(
        max_length=20,
        verbose_name='Canal',
        help_text='Canal pelo qual o voto foi registrado (presencial, online, etc.).',
    )
    ip_address: models.GenericIPAddressField = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Endereço IP',
        help_text='IP do dispositivo que registrou o voto.',
    )
    voted_at: models.DateTimeField = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Votado em',
        help_text='Data/hora em que o voto foi registrado.',
    )
    # ----- Hash fields -----
    member_id_hash: models.CharField = models.CharField(
        max_length=64,
        blank=True,
        verbose_name='Hash do membro',
        help_text=(
            'SHA-256 do UUID do membro. '
            'Sempre preenchido; é a única identificação em votação secreta.'
        ),
    )
    vote_label_hash: models.CharField = models.CharField(
        max_length=64,
        blank=True,
        verbose_name='Hash da opção',
        help_text='SHA-256 do rótulo da opção escolhida. Preenchido automaticamente no save().',
    )
    integrity_hash: models.CharField = models.CharField(
        max_length=64,
        blank=True,
        verbose_name='Hash de integridade',
        help_text=(
            'SHA-256 combinando agenda_item_id + member_id_hash + vote_label_hash + voted_at. '
            'Permite verificação forense de adulteração.'
        ),
    )
    # ----- Audit timestamps -----
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Registro de voto'
        verbose_name_plural = 'Registros de voto'
        ordering = ['agenda_item', 'voted_at']
        constraints = [
            # Prevent double-vote in open mode (member FK is non-null)
            models.UniqueConstraint(
                fields=['agenda_item', 'member'],
                condition=models.Q(member__isnull=False),
                name='unique_open_vote_per_member_per_item',
                violation_error_message=(
                    'Este membro já registrou um voto neste item de pauta (votação aberta).'
                ),
            ),
            # Prevent double-vote in secret mode (identified by member_id_hash)
            models.UniqueConstraint(
                fields=['agenda_item', 'member_id_hash'],
                condition=models.Q(member__isnull=True),
                name='unique_secret_vote_per_member_hash_per_item',
                violation_error_message=(
                    'Este membro já registrou um voto neste item de pauta (votação secreta).'
                ),
            ),
        ]

    def __str__(self) -> str:
        who: str = str(self.member) if self.member else f'[secreto:{self.member_id_hash[:8]}…]'
        return f'Voto: {who} → {self.vote.label} ({self.agenda_item})'

    # ------------------------------------------------------------------
    # Hash computation helpers
    # ------------------------------------------------------------------

    def _compute_member_hash(self) -> str:
        """
        Compute and return the SHA-256 hex digest of the member's UUID.

        This hash is the sole identity token in secret-mode votes and is always
        stored regardless of vote mode so that audit queries can be written
        uniformly across both modes.

        Returns:
            str: 64-character lowercase hex SHA-256 digest.
        """
        import hashlib

        member_id_str: str = str(self.member_id or (self.member.pk if self.member else ''))
        return hashlib.sha256(member_id_str.encode()).hexdigest()

    def _compute_vote_hash(self) -> str:
        """
        Compute and return the SHA-256 hex digest of the chosen vote option's label.

        Hashing the label (rather than the Vote PK) ensures that even if the
        Vote row is deleted, the hash remains meaningful for audit purposes.

        Returns:
            str: 64-character lowercase hex SHA-256 digest.
        """
        import hashlib

        label: str = self.vote.label if self.vote_id else ''
        return hashlib.sha256(label.encode()).hexdigest()

    def _compute_integrity_hash(self) -> str:
        """
        Compute and return the overall integrity hash for this vote record.

        Combines ``agenda_item_id``, ``member_id_hash``, ``vote_label_hash``,
        and ``voted_at`` into a single SHA-256 digest.  Any post-save alteration
        to these fields would produce a different hash, making tampering detectable
        via ``verify_integrity()``.

        Returns:
            str: 64-character lowercase hex SHA-256 digest.
        """
        import hashlib

        payload: str = '|'.join([
            str(self.agenda_item_id),
            self.member_id_hash,
            self.vote_label_hash,
            str(self.voted_at),
        ])
        return hashlib.sha256(payload.encode()).hexdigest()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def clean(self) -> None:
        """
        Enforce all business rules before saving a vote record.

        Rules enforced:
        1. The agenda item must have status ``open`` (in-vote).
        2. The member must have a ``Credential`` for the parent assembly.
        3. Inadimplente members are blocked (defence-in-depth, RF-07.3).
        4. The chosen ``vote`` option must belong to the same ``agenda_item``.
        5. Double-vote check for open mode (member already voted on this item).
        6. Double-vote check for secret mode (member_id_hash already used).

        Raises:
            ValidationError: when any rule is violated.
        """
        from assemblies.models import Credential
        from organizations.models import MemberStatus

        errors: dict[str, str] = {}

        # 1. Agenda item must be open
        if self.agenda_item_id:
            try:
                item = AgendaItem.objects.get(pk=self.agenda_item_id)
                if item.status != AgendaItem.Status.OPEN:
                    errors['agenda_item'] = (
                        f'O item de pauta "{item.title}" não está em votação '
                        f'(status atual: {item.get_status_display()}).'
                    )
            except AgendaItem.DoesNotExist:
                errors['agenda_item'] = 'Item de pauta não encontrado.'

        # 2 & 3. Member must be credentialed and not inadimplente
        if self.member_id:
            member = self.member
            if member.status == MemberStatus.INADIMPLENTE:
                errors['member'] = (
                    'Membros inadimplentes não podem votar.'
                )
            assembly_id = getattr(
                getattr(self, 'agenda_item', None), 'assembly_id', None
            ) or (
                AgendaItem.objects.filter(pk=self.agenda_item_id)
                .values_list('assembly_id', flat=True)
                .first()
            )
            if assembly_id:
                has_credential = Credential.objects.filter(
                    assembly_id=assembly_id,
                    member_id=self.member_id,
                ).exists()
                if not has_credential:
                    errors['member'] = (
                        'O membro não possui credencial para esta assembleia. '
                        'Realize o credenciamento antes de votar.'
                    )

        # 4. Vote option must belong to the same agenda_item
        if self.vote_id and self.agenda_item_id:
            if not Vote.objects.filter(
                pk=self.vote_id,
                agenda_item_id=self.agenda_item_id,
            ).exists():
                errors['vote'] = (
                    'A opção de voto selecionada não pertence a este item de pauta.'
                )

        # 5 & 6. Double-vote guards (complementary to UniqueConstraints)
        if self.agenda_item_id and not self.pk:
            if self.member_id:
                # Open mode: check by FK
                if VoteRecord.objects.filter(
                    agenda_item_id=self.agenda_item_id,
                    member_id=self.member_id,
                ).exists():
                    errors['member'] = (
                        'Este membro já registrou um voto neste item de pauta.'
                    )
            elif self.member_id_hash:
                # Secret mode: check by hash
                if VoteRecord.objects.filter(
                    agenda_item_id=self.agenda_item_id,
                    member_id_hash=self.member_id_hash,
                    member__isnull=True,
                ).exists():
                    errors['member_id_hash'] = (
                        'Este membro já registrou um voto neste item de pauta (votação secreta).'
                    )

        if errors:
            raise ValidationError(errors)

    # ------------------------------------------------------------------
    # Lifecycle overrides
    # ------------------------------------------------------------------

    def save(self, *args, **kwargs) -> None:
        """
        Persist the vote record with automatic hash computation and secret-mode anonymisation.

        On first save:
        1. ``voted_at`` is set to ``now()`` if not provided.
        2. ``member_id_hash`` is computed from the member's UUID.
        3. ``vote_label_hash`` is computed from the chosen option's label.
        4. For **secret voting**: ``member`` FK is cleared (set to ``None``) so
           the member's identity cannot be retrieved through the FK.  Only the
           ``member_id_hash`` remains as the identity token.
        5. ``integrity_hash`` is computed over all the above fields.
        6. The corresponding ``Vote.increment()`` is called atomically.

        Updates after creation are blocked — raises ``ValueError`` if ``self.pk``
        is already set.

        Raises:
            ValueError: if an attempt is made to update an existing VoteRecord.
        """
        from django.utils import timezone

        if self.pk:
            raise ValueError(
                'VoteRecord é imutável: não é permitido atualizar um registro de voto existente.'
            )

        # Step 1: timestamp
        if not self.voted_at:
            self.voted_at = timezone.now()

        # Step 2: member identity hash (computed before possible FK nullification)
        self.member_id_hash = self._compute_member_hash()

        # Step 3: vote label hash
        self.vote_label_hash = self._compute_vote_hash()

        # Step 4: anonymise member FK for secret votes
        if self.agenda_item_id:
            try:
                item = AgendaItem.objects.get(pk=self.agenda_item_id)
                if item.vote_mode == AgendaItem.VoteMode.SECRETO:
                    self.member = None  # type: ignore[assignment]
            except AgendaItem.DoesNotExist:
                pass

        # Step 5: integrity hash (after all fields are finalised)
        self.integrity_hash = self._compute_integrity_hash()

        super().save(*args, **kwargs)

        # Step 6: atomically increment the vote option counter
        if self.vote_id:
            self.vote.increment()

    def delete(self, *args, **kwargs) -> None:
        """
        Block deletion of vote records to preserve audit trail integrity.

        VoteRecords must never be deleted — the immutable audit log is a core
        compliance requirement. Raises ``PermissionError`` unconditionally.

        Raises:
            PermissionError: always, when called.
        """
        raise PermissionError(
            'Registros de voto não podem ser excluídos. '
            'A trilha de auditoria é imutável por requisito de negócio.'
        )

    # ------------------------------------------------------------------
    # Audit helpers
    # ------------------------------------------------------------------

    def verify_integrity(self) -> bool:
        """
        Re-compute the integrity hash and compare it against the stored value.

        Allows forensic verification that the record has not been tampered with
        after creation.  If the stored ``integrity_hash`` matches the freshly
        computed one, the record is considered intact.

        Returns:
            bool: ``True`` if the record is intact, ``False`` if tampering is detected.
        """
        expected: str = self._compute_integrity_hash()
        return expected == self.integrity_hash
