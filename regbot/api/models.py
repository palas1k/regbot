from django.db import models
from django.utils import timezone


class SupportSoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    class Meta:
        abstract = True


class ReservedTime(SupportSoftDeleteModel):
    date_time = models.DateTimeField(default=None)
    reserve_at = models.DateTimeField(auto_now=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    user = models.CharField(max_length=20, blank=True, null=True)
    tg_id = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return str(self.date_time)
