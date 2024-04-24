from django.db import models
from django.utils import timezone
#today = timezone.now().date()
#from django.utils import timezone

class IvaultLog(models.Model):

    class Meta:
        ordering = ['id']

    logged_user  = models.CharField(
        max_length=64,
        db_column = 'logged_user',
        default = 'no logged_user',
        blank=True, 
    )

    filename  = models.CharField(
        max_length=128,
        db_column = 'filename',
        default = 'empty',
        blank=True, 
    )

    mode  = models.CharField(
        max_length=32,
        db_column = 'mode',
        default = 'default',
        blank=True, 
    )

    data  = models.CharField(
        max_length=1500,
        db_column = 'data',
        default = 'Empty log data.',
    )

    timestamp  = models.DateTimeField(
        db_column = 'ts',
        default=timezone.now,
        editable=False,
    )

    # This makes the Admin List show
    # a specified string rather than
    # `object_2()`
    def __str__(self):
        return '{}'.format(self.data)