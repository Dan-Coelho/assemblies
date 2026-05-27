from django.db import models
from core.models import BaseModel, TenantModel


class Organization(BaseModel):
    """Represents a tenant organization such as a condominium, union, or association."""

    class OrgType(models.TextChoices):
        CONDOMINIO = 'condominio', 'Condomínio'
        SINDICATO = 'sindicato', 'Sindicato'
        ASSOCIACAO = 'associacao', 'Associação'

    name: models.CharField = models.CharField(max_length=255)
    type: models.CharField = models.CharField(
        max_length=20,
        choices=OrgType.choices,
        default=OrgType.CONDOMINIO,
    )
    cnpj: models.CharField = models.CharField(max_length=18, blank=True)
    plan: models.CharField = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = 'Organização'
        verbose_name_plural = 'Organizações'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class MemberRole(models.TextChoices):
    SINDICO = 'sindico', 'Síndico/Presidente'
    SECRETARIO = 'secretario', 'Secretário'
    CONSELHEIRO = 'conselheiro', 'Conselheiro'
    MEMBRO = 'membro', 'Membro'

class MemberStatus(models.TextChoices):
    ATIVO = 'ativo', 'Ativo'
    INATIVO = 'inativo', 'Inativo'
    INADIMPLENTE = 'inadimplente', 'Inadimplente'

class Member(TenantModel):
    """
    Representa um membro da organização (condomínio, sindicato, associação).
    Pode ser vinculado a um usuário do sistema, mas não é obrigatório.
    """
    user: models.ForeignKey = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='members'
    )
    name: models.CharField = models.CharField(max_length=255)
    email: models.EmailField = models.EmailField(max_length=255)
    cpf: models.CharField = models.CharField(max_length=14)
    role: models.CharField = models.CharField(
        max_length=20,
        choices=MemberRole.choices,
        default=MemberRole.MEMBRO,
    )
    status: models.CharField = models.CharField(
        max_length=20,
        choices=MemberStatus.choices,
        default=MemberStatus.ATIVO,
    )
    is_defaulter: models.BooleanField = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Membro'
        verbose_name_plural = 'Membros'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'cpf'], name='unique_member_cpf_per_org')
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_role_display()})"

