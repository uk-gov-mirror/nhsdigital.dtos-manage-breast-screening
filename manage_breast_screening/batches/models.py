import uuid

from django.db import models

from ..core.models import BaseModel


class Batch(BaseModel):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    bso_batch_id = models.CharField(max_length=255, null=False, unique=True)
    title = models.CharField(max_length=255, null=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Batches"
