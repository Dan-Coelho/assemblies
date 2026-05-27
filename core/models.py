import uuid
from django.db import models


class BaseModel(models.Model):
    """Abstract base model that provides UUID primary key and audit timestamps for all entities."""

    id: models.UUIDField = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TenantModel(BaseModel):
    """Abstract model that extends BaseModel with a mandatory FK to Organization, isolating data per tenant."""

    organization: models.ForeignKey = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_set',
    )

    class Meta:
        abstract = True
