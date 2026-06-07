import secrets

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.models import TenantModel


class Minutes(TenantModel):
    """
    Represents the official minutes (ata) of a general assembly.

    The minutes document records the proceedings of a closed assembly,
    including attendance, agenda items discussed, votes cast, and final
    deliberations. Once approved, the document becomes immutable — any
    attempt to edit an approved ``Minutes`` instance raises a
    ``ValidationError``.

    Lifecycle:
        draft → approved

    Fields:
        assembly: One-to-one link to the related :class:`assemblies.Assembly`.
        content: Full text content of the minutes.
        status: Current state of the minutes (``draft`` or ``approved``).
        document_url: Optional URL to the stored document file (PDF, etc.).
        generated_at: Timestamp when the minutes were automatically generated.
        approved_at: Timestamp when the minutes were formally approved.
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Rascunho'
        APPROVED = 'approved', 'Aprovada'

    assembly: models.OneToOneField = models.OneToOneField(
        'assemblies.Assembly',
        on_delete=models.CASCADE,
        related_name='minutes',
        verbose_name='Assembleia',
        help_text='Assembleia à qual esta ata pertence.',
    )
    content: models.TextField = models.TextField(
        blank=True,
        verbose_name='Conteúdo',
        help_text='Texto completo da ata gerado automaticamente ou editado manualmente.',
    )
    status: models.CharField = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name='Status',
        help_text='Estado atual da ata. Após aprovação, o documento não pode ser alterado.',
    )
    document_url: models.URLField = models.URLField(
        blank=True,
        verbose_name='URL do documento',
        help_text='Link para o arquivo gerado da ata (ex.: PDF armazenado em object storage).',
    )
    generated_at: models.DateTimeField = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Gerada em',
        help_text='Data/hora em que a ata foi gerada automaticamente pelo sistema.',
    )
    approved_at: models.DateTimeField = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Aprovada em',
        help_text='Data/hora em que a ata foi formalmente aprovada pelos participantes.',
    )

    class Meta:
        verbose_name = 'Ata'
        verbose_name_plural = 'Atas'
        ordering = ['-generated_at']

    def __str__(self) -> str:
        return f'Ata — {self.assembly} [{self.get_status_display()}]'

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, *args, **kwargs) -> None:  # type: ignore[override]
        """
        Persist the ``Minutes`` instance, blocking edits after approval.

        If the instance already exists in the database and its status is
        ``approved``, any further save attempt will raise a
        :class:`~django.core.exceptions.ValidationError` to preserve the
        integrity of the official record.

        When transitioning to ``approved`` for the first time,
        ``approved_at`` is automatically set to the current timestamp.

        Raises:
            ValidationError: if an attempt is made to edit an already-approved
                minutes document.
        """
        if self.pk:
            # Fetch the persisted status without triggering a full model load
            persisted_status: str | None = (
                Minutes.objects.filter(pk=self.pk)
                .values_list('status', flat=True)
                .first()
            )
            if persisted_status == self.Status.APPROVED:
                raise ValidationError(
                    'Atas aprovadas não podem ser editadas. '
                    'O documento oficial é imutável após a aprovação.'
                )

        # Auto-populate approved_at when status changes to approved
        if self.status == self.Status.APPROVED and not self.approved_at:
            self.approved_at = timezone.now()

        super().save(*args, **kwargs)


class MinuteSignature(TenantModel):
    """
    Represents the digital signature of a member on the official minutes (ata).

    Each signature links a member to the minutes of a specific assembly,
    recording their role at the time of signing, a cryptographically secure
    token that uniquely identifies the signature event, and the exact timestamp
    when the signature was registered.

    The ``signature_token`` is generated automatically on the first ``save()``
    using :func:`secrets.token_urlsafe`, ensuring uniqueness and tamper-evidence
    without exposing predictable sequences.

    A member may only sign a given set of minutes once
    (enforced by ``UniqueConstraint``).

    Fields:
        minutes: FK to the :class:`Minutes` instance being signed.
        member: FK to the :class:`organizations.Member` who is signing.
        role: The role/capacity in which the member signs (e.g. secretary, chair).
        signature_token: URL-safe cryptographic token auto-generated at signing time.
        signed_at: Timestamp of when the signature was registered.
    """

    # Default token length: 48 bytes → 64 URL-safe base64 characters
    _TOKEN_BYTES: int = 48

    minutes: models.ForeignKey = models.ForeignKey(
        Minutes,
        on_delete=models.CASCADE,
        related_name='signatures',
        verbose_name='Ata',
        help_text='Ata à qual esta assinatura pertence.',
    )
    member: models.ForeignKey = models.ForeignKey(
        'organizations.Member',
        on_delete=models.CASCADE,
        related_name='minute_signatures',
        verbose_name='Membro',
        help_text='Membro que está assinando a ata.',
    )
    role: models.CharField = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Papel/Função',
        help_text='Cargo ou função do membro no momento da assinatura (ex.: Secretário, Presidente).',
    )
    signature_token: models.CharField = models.CharField(
        max_length=128,
        unique=True,
        editable=False,
        verbose_name='Token de assinatura',
        help_text='Token criptográfico único gerado automaticamente ao registrar a assinatura.',
    )
    signed_at: models.DateTimeField = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Assinado em',
        help_text='Data/hora em que a assinatura foi registrada.',
    )

    class Meta:
        verbose_name = 'Assinatura de Ata'
        verbose_name_plural = 'Assinaturas de Ata'
        ordering = ['signed_at']
        constraints = [
            models.UniqueConstraint(
                fields=['minutes', 'member'],
                name='unique_signature_per_member_per_minutes',
                violation_error_message='Este membro já assinou esta ata.',
            )
        ]

    def __str__(self) -> str:
        signed: str = (
            self.signed_at.strftime('%d/%m/%Y %H:%M') if self.signed_at else 'pendente'
        )
        return f'Assinatura: {self.member} — {self.minutes} [{signed}]'

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, *args, **kwargs) -> None:  # type: ignore[override]
        """
        Persist the ``MinuteSignature`` instance, auto-generating the token.

        On the very first save (``pk`` is ``None``), a cryptographically secure
        URL-safe token is generated via :func:`secrets.token_urlsafe` and stored
        in ``signature_token``. If ``signed_at`` is not yet set, it is also
        populated with the current UTC timestamp.

        Token generation is intentionally skipped on subsequent saves so that
        the token remains stable and can be used as a verifiable reference.
        """
        if not self.pk:
            # Generate token only on creation
            self.signature_token = secrets.token_urlsafe(self._TOKEN_BYTES)

            # Auto-populate signed_at on first save if not explicitly provided
            if not self.signed_at:
                self.signed_at = timezone.now()

        super().save(*args, **kwargs)
