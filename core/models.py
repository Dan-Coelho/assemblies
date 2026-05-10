import uuid

from django.db import models


class BaseModel(models.Model):
    """
    Model base abstrato para todos os modelos do sistema.

    Fornece um identificador UUID como chave primária e campos
    de auditoria de criação e atualização automáticos.
    """

    id: models.UUIDField = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID',
    )
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        verbose_name='criado em',
    )
    updated_at: models.DateTimeField = models.DateTimeField(
        auto_now=True,
        verbose_name='atualizado em',
    )

    class Meta:
        abstract = True


class TenantModel(BaseModel):
    """
    Model base abstrato para entidades que pertencem a uma organização (tenant).

    Herda de BaseModel e adiciona uma chave estrangeira obrigatória para
    Organization, garantindo o isolamento de dados por tenant.
    """

    organization: models.ForeignKey = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_set',
        verbose_name='organização',
    )

    class Meta:
        abstract = True
