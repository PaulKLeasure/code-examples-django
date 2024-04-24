from django.db import models

class SearchTemplate(models.Model):

    name  = models.CharField(
        max_length=128,
        db_column = 'name',
    )

    descr = models.CharField(
        max_length=128,
        db_column = 'descr',
    )
    
    # Do not pass a default dictionary
    data = models.JSONField()

    sort = models.SmallIntegerField(
        db_column = 'sort',
        blank = 1,
        null = 1,
    )

    # This makes the Admin List show
    # a specified string rather than
    # `object_2()`
    def __str__(self):
        return '{}'.format('('+ str(self.id) +') '+self.name + ':' + self.descr)

    def as_json(self):
        return dict(id=self.id, name=self.name, description=self.descr)

