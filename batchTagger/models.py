from django.db import models
from django.utils import timezone


class History(models.Model):
    timestamp = models.DateTimeField(
        db_column='ts',
        default=timezone.now,
        editable=False,
    )

    # 0 = undone|redo available. #1 = applied|undo available
    state = models.IntegerField()

    asset_ids = models.JSONField(
        db_column='asset_ids',
    )

    oids_added = models.JSONField(
        db_column='oids_added',
    )

    oids_removed = models.JSONField(
        db_column='oids_removed',
    )

    username = models.CharField(
        max_length=64,
        db_column='username',
        default='',
        blank=True,
    )
