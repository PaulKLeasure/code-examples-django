from django.db import models
from django.utils import timezone

class AltTextTemplate(models.Model):

    class Meta:
        ordering = ['id']

    # This makes the Admin List show
    # a specified string rather than
    # `object_2()`
    def __str__(self):
        return '{}'.format(self.id)

    path  = models.CharField(
        max_length=256,
        db_column = 'path',
        default = 'Empty path string.',
    )

    requiredIds = models.JSONField(
        db_column='required_ids',
    )

    grpHeader = models.CharField(
        max_length=128,
        db_column = 'grp_header',
        default = 'none',
    )

    isRecursive = models.BooleanField(
        db_column='recursive',
        default=False
    )

    template  = models.CharField(
        max_length=500,
        db_column = 'template',
        default = 'Empty template data.',
    )

    timestamp  = models.DateTimeField(
        default=timezone.now,
        editable=False,
        null=True
    )

    def as_json(self):
        return dict(
            id=self.id, 
            path=self.path, 
            requiredIds=self.requiredIds, 
            grpHeader=self.grpHeader, 
            isRecursive=self.isRecursive,
            template=self.template,
            timestamp=self.timestamp
        )



class AltTextCache(models.Model):

    class Meta:
        ordering = ['id']

    # This makes the Admin List show
    # a specified string rather than
    # `object_2()`
    def __str__(self):
        return '{}'.format(self.id)

    assetId = models.PositiveIntegerField()

    templateId = models.PositiveIntegerField(
        default = 999
    )

    fileName  = models.CharField(
        max_length=128,
        default = 'Empty fileName.',
    )

    path  = models.CharField(
        max_length=256,
        default = 'Empty path string.',
    )

    altText  = models.CharField(
        max_length=500,
        default = 'Empty altText.',
    )

    timestamp  = models.DateTimeField(
        default=timezone.now,
        editable=False,
        null=True
    )