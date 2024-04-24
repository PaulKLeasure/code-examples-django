from django.db import models
from django.utils import timezone
#today = timezone.now().date()
from django.utils import timezone

class TagBotModes(models.Model):

    name  = models.CharField(
        max_length=16,
        db_column = 'name'
    )

    description = models.CharField(
        max_length=128,
        blank = 1,
        null = 1
    )

    # This makes the Admin List show
    # a specified string rather than
    # `object_2()`
    def __str__(self):
        return '{}'.format('('+ str(self.id) +') '+self.name )

    def as_json(self):
        return dict(id=self.id, name=self.name, descriptione=self.description)


class TagBotMapping(models.Model):

    mode = models.ForeignKey(TagBotModes, on_delete=models.CASCADE)

    nomenclature  = models.CharField(
        max_length=128,
        db_column = 'nomenclature'
    )

    optionIds  = models.CharField(
        max_length=128,
        db_column = 'option_ids',
        default='',
        blank = 1
    )

    logic = models.CharField(
    	max_length=256,
        blank = 1,
        default='EMPTY'
    )

    # This makes the Admin List show
    # a specified string rather than
    # `object_2()`
    def __str__(self):
        return '{}'.format( self.nomenclature + ' [' + str(self.optionIds) + '] '  )

    def as_json(self):
        return dict(id=self.id, code=self.nomenclature, mode=self.mode, optionIdsArray=self.optionIds)
