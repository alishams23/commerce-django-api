from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(
        blank=True, null=True, default=None, editable=False
    )
    objects = SoftDeleteManager()  # only non-deleted records
    all_objects = models.Manager()  # all records, even deleted

    class Meta:
        abstract = True

    def delete(self, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def delete_hard(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)
