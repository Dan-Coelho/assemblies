from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.models import TenantModel


class Assembly(TenantModel):
    """
    Represents a general assembly (assembleia) of an organization.

    An assembly goes through a lifecycle of states: draft → convoked → open → closed.
    It can be held in-person, online, or in a hybrid format. Quorum control is based
    on the number of credentialed members versus the required quorum percentage.
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Rascunho'
        CONVOKED = 'convoked', 'Convocada'
        OPEN = 'open', 'Em andamento'
        CLOSED = 'closed', 'Encerrada'
        CANCELLED = 'cancelled', 'Cancelada'

    class Mode(models.TextChoices):
        PRESENCIAL = 'presencial', 'Presencial'
        ONLINE = 'online', 'Online'
        HIBRIDO = 'hibrido', 'Híbrido'

    title: models.CharField = models.CharField(
        max_length=255,
        verbose_name='Título',
    )
    description: models.TextField = models.TextField(
        blank=True,
        verbose_name='Descrição',
    )
    status: models.CharField = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name='Status',
    )
    mode: models.CharField = models.CharField(
        max_length=20,
        choices=Mode.choices,
        default=Mode.PRESENCIAL,
        verbose_name='Modalidade',
    )
    scheduled_at: models.DateTimeField = models.DateTimeField(
        verbose_name='Data/hora agendada',
    )
    started_at: models.DateTimeField = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data/hora de início',
    )
    ended_at: models.DateTimeField = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data/hora de encerramento',
    )
    quorum_required: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField(
        default=50,
        verbose_name='Quórum necessário (%)',
        help_text='Percentual mínimo de membros presentes para validar a assembleia.',
    )
    location: models.CharField = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Local',
        help_text='Endereço físico para assembleias presenciais ou híbridas.',
    )
    meeting_url: models.URLField = models.URLField(
        blank=True,
        verbose_name='URL da reunião',
        help_text='Link de acesso para assembleias online ou híbridas.',
    )

    class Meta:
        verbose_name = 'Assembleia'
        verbose_name_plural = 'Assembleias'
        ordering = ['-scheduled_at']

    def __str__(self) -> str:
        return f'{self.title} — {self.get_status_display()} ({self.scheduled_at:%d/%m/%Y})'

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def clean(self) -> None:
        """
        Apply business-rule validations for the assembly lifecycle and field consistency.

        Rules enforced:
        - ``started_at`` must be after ``scheduled_at``.
        - ``ended_at`` must be after ``started_at``.
        - Presencial assemblies must have a ``location``.
        - Online assemblies must have a ``meeting_url``.
        - ``quorum_required`` must be between 1 and 100.
        - A closed or cancelled assembly cannot be re-opened.
        """
        errors: dict[str, str] = {}

        # Temporal consistency
        if self.started_at and self.started_at < self.scheduled_at:
            errors['started_at'] = (
                'A data/hora de início não pode ser anterior à data/hora agendada.'
            )

        if self.ended_at:
            if not self.started_at:
                errors['ended_at'] = (
                    'Informe a data/hora de início antes de registrar o encerramento.'
                )
            elif self.ended_at <= self.started_at:
                errors['ended_at'] = (
                    'A data/hora de encerramento deve ser posterior ao início.'
                )

        # Mode ↔ location/url consistency
        if self.mode in (self.Mode.PRESENCIAL, self.Mode.HIBRIDO) and not self.location:
            errors['location'] = (
                'Informe o local para assembleias presenciais ou híbridas.'
            )

        if self.mode in (self.Mode.ONLINE, self.Mode.HIBRIDO) and not self.meeting_url:
            errors['meeting_url'] = (
                'Informe a URL da reunião para assembleias online ou híbridas.'
            )

        # Quorum range
        if not (1 <= self.quorum_required <= 100):
            errors['quorum_required'] = 'O quórum deve estar entre 1% e 100%.'

        if errors:
            raise ValidationError(errors)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_open(self) -> bool:
        """Return ``True`` if the assembly is currently in progress."""
        return self.status == self.Status.OPEN

    @property
    def total_credentials(self) -> int:
        """Return the total number of credentialed members for this assembly."""
        return self.credentials.count()  # type: ignore[attr-defined]

    @property
    def quorum_reached(self) -> bool:
        """
        Return ``True`` if the number of credentialed members meets or exceeds the
        required quorum percentage relative to the total active members in the organization.
        """
        from organizations.models import MemberStatus

        total_members: int = (
            self.organization.organizations_member_set  # type: ignore[attr-defined]
            .filter(status=MemberStatus.ATIVO)
            .count()
        )
        if total_members == 0:
            return False
        return (self.total_credentials / total_members * 100) >= self.quorum_required


class Convocation(TenantModel):
    """
    Represents a formal convocation (convocação) sent to members for an assembly.

    A convocation records which communication channel was used, when it was sent,
    whether it is a second call, and the delivery status returned by the sending
    service (stored as JSON for flexibility across channels such as e-mail or SMS).
    """

    class Channel(models.TextChoices):
        EMAIL = 'email', 'E-mail'
        SMS = 'sms', 'SMS'
        WHATSAPP = 'whatsapp', 'WhatsApp'
        POSTAL = 'postal', 'Correio'
        EDITAL = 'edital', 'Edital'

    class DeliveryStatus(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        SENT = 'sent', 'Enviado'
        DELIVERED = 'delivered', 'Entregue'
        FAILED = 'failed', 'Falhou'

    assembly: models.ForeignKey = models.ForeignKey(
        Assembly,
        on_delete=models.CASCADE,
        related_name='convocations',
        verbose_name='Assembleia',
    )
    channel: models.CharField = models.CharField(
        max_length=20,
        choices=Channel.choices,
        default=Channel.EMAIL,
        verbose_name='Canal de envio',
    )
    sent_at: models.DateTimeField = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Enviado em',
        help_text='Data/hora em que a convocação foi efetivamente enviada.',
    )
    is_second_call: models.BooleanField = models.BooleanField(
        default=False,
        verbose_name='Segunda convocação',
        help_text='Marque se esta é uma segunda chamada da assembleia.',
    )
    delivery_status: models.JSONField = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Status de entrega',
        help_text='Payload JSON retornado pelo serviço de envio com detalhes da entrega.',
    )
    notes: models.TextField = models.TextField(
        blank=True,
        verbose_name='Observações',
        help_text='Notas internas sobre esta convocação.',
    )

    class Meta:
        verbose_name = 'Convocação'
        verbose_name_plural = 'Convocações'
        ordering = ['-sent_at']

    def __str__(self) -> str:
        call_label: str = '2ª chamada' if self.is_second_call else '1ª chamada'
        sent: str = self.sent_at.strftime('%d/%m/%Y %H:%M') if self.sent_at else 'não enviada'
        return f'Convocação ({self.get_channel_display()} — {call_label}) [{sent}]'


class Proxy(TenantModel):
    """
    Represents a proxy authorization (procuração) granted by one member to another
    for a specific assembly.

    Business rules enforced:
    - A member cannot grant a proxy to themselves (grantor ≠ proxy_member).
    - Each member may grant at most one proxy per assembly (UniqueConstraint).
    """

    assembly: models.ForeignKey = models.ForeignKey(
        Assembly,
        on_delete=models.CASCADE,
        related_name='proxies',
        verbose_name='Assembleia',
    )
    grantor: models.ForeignKey = models.ForeignKey(
        'organizations.Member',
        on_delete=models.CASCADE,
        related_name='proxies_granted',
        verbose_name='Outorgante',
        help_text='Membro que concede a procuração.',
    )
    proxy_member: models.ForeignKey = models.ForeignKey(
        'organizations.Member',
        on_delete=models.CASCADE,
        related_name='proxies_received',
        verbose_name='Procurador',
        help_text='Membro que recebe e exercerá os direitos de voto.',
    )
    document_url: models.URLField = models.URLField(
        blank=True,
        verbose_name='URL do documento',
        help_text='Link para o documento digitalizado da procuração (opcional).',
    )
    is_active: models.BooleanField = models.BooleanField(
        default=True,
        verbose_name='Ativa',
        help_text='Desmarque para revogar a procuração sem excluí-la.',
    )

    class Meta:
        verbose_name = 'Procuração'
        verbose_name_plural = 'Procurações'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['assembly', 'grantor'],
                name='unique_proxy_grantor_per_assembly',
                violation_error_message=(
                    'Este membro já possui uma procuração registrada nesta assembleia.'
                ),
            )
        ]

    def __str__(self) -> str:
        return f'Procuração: {self.grantor} → {self.proxy_member} ({self.assembly})'

    def clean(self) -> None:
        """
        Validate that the grantor is not the same member as the proxy_member.

        Raises:
            ValidationError: if grantor and proxy_member are the same person.
        """
        if self.grantor_id and self.proxy_member_id and self.grantor_id == self.proxy_member_id:
            raise ValidationError(
                {'proxy_member': 'O procurador não pode ser o mesmo membro que o outorgante.'}
            )


class Credential(TenantModel):
    """
    Records the check-in of a member for a specific assembly (credenciamento).

    Each member may check in at most once per assembly. The check-in can occur
    via different channels (presencial, online, etc.). The ``access_token`` field
    supports token-based online check-in flows and is marked used via ``token_used_at``.

    Business rules enforced:
    - A member with status ``inadimplente`` (defaulter) cannot be credentialed (RF-07.3).
    - Each member may have only one credential per assembly (UniqueConstraint).
    """

    assembly: models.ForeignKey = models.ForeignKey(
        Assembly,
        on_delete=models.CASCADE,
        related_name='credentials',
        verbose_name='Assembleia',
    )
    member: models.ForeignKey = models.ForeignKey(
        'organizations.Member',
        on_delete=models.CASCADE,
        related_name='credentials',
        verbose_name='Membro',
    )
    channel: models.CharField = models.CharField(
        max_length=20,
        choices=Convocation.Channel.choices,
        default=Convocation.Channel.EMAIL,
        verbose_name='Canal de check-in',
        help_text='Meio pelo qual o membro realizou o credenciamento.',
    )
    checked_in_at: models.DateTimeField = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data/hora do check-in',
    )
    ip_address: models.GenericIPAddressField = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Endereço IP',
        help_text='IP registrado no momento do credenciamento online.',
    )
    device_info: models.CharField = models.CharField(
        max_length=512,
        blank=True,
        verbose_name='Informações do dispositivo',
        help_text='User-agent ou descrição do dispositivo usado no check-in online.',
    )
    access_token: models.CharField = models.CharField(
        max_length=128,
        blank=True,
        unique=True,
        verbose_name='Token de acesso',
        help_text='Token único enviado ao membro para autenticação no check-in online.',
    )
    token_used_at: models.DateTimeField = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Token utilizado em',
        help_text='Data/hora em que o token de acesso foi consumido.',
    )

    class Meta:
        verbose_name = 'Credencial'
        verbose_name_plural = 'Credenciais'
        ordering = ['-checked_in_at']
        constraints = [
            models.UniqueConstraint(
                fields=['assembly', 'member'],
                name='unique_credential_per_member_per_assembly',
                violation_error_message=(
                    'Este membro já possui credencial registrada nesta assembleia.'
                ),
            )
        ]

    def __str__(self) -> str:
        checked: str = (
            self.checked_in_at.strftime('%d/%m/%Y %H:%M')
            if self.checked_in_at
            else 'pendente'
        )
        return f'Credencial: {self.member} — {self.assembly} [{checked}]'

    def clean(self) -> None:
        """
        Block check-in for members with ``inadimplente`` status (RF-07.3).

        Raises:
            ValidationError: if the member is a defaulter.
        """
        from organizations.models import MemberStatus

        if self.member_id:
            # Avoid an extra query if member object is already loaded
            member = getattr(self, '_member_cache', None) or self.member
            if member.status == MemberStatus.INADIMPLENTE:
                raise ValidationError(
                    {
                        'member': (
                            'Membros inadimplentes não podem ser credenciados. '
                            'Regularize a situação antes de prosseguir.'
                        )
                    }
                )

