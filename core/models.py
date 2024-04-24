from django.db import models
from django.utils import timezone


class Option(models.Model):

    groupName  = models.CharField(
        max_length=128,
        db_column = 'grp',
    )

    definition = models.CharField(
        max_length=128,
        db_column = 'def1',
    )

    groupSort = models.SmallIntegerField(
        db_column = 'grp_srt',
        blank=True,
        null=True
    )

    # This makes the Admin List show
    # a specified string rather than
    # `object_2()`
    def __str__(self):
        return '{}'.format('('+ str(self.id) +') '+self.groupName + ':' + self.definition)

    def as_json(self):
        return dict(id=self.id, groupName=self.groupName, definition=self.definition)

class Category(models.Model):

    name  = models.CharField(
        max_length=64,
        db_column = 'name',
        default = 'Needs category name',
    )

    description = models.CharField(
        max_length=128,
        db_column = 'descr',
        null = 1,
    )

    # This makes the Admin List show
    # a specified string rather than
    # `object_2()`
    def __str__(self):
        return '{}'.format(self.name)


class Asset(models.Model):

    class Meta:
        ordering = ['id']

    # This makes the Admin List show
    # a specified string rather than
    # `object_2()`
    def __str__(self):
        return '{}'.format(self.fileName)

    fileName = models.FileField(
        upload_to='iVault2/media/',
        max_length=128,
        db_column = 'f_name',
    )

    search_string  = models.CharField(
        max_length=256,
        db_column = 's_string',
        default = 'Empty search string.',
    )

    timestamp  = models.DateTimeField(
        #db_column = 'ts',
        default=timezone.now,
        editable=False,
        null=True
    )

    effectDate = models.DateTimeField(
        #db_column = 'effect_date',
        default=timezone.now,
        editable = 0,
        blank=True,
        null=True
    )

    options = models.ManyToManyField(Option)

    #categories = models.ManyToManyField(Category)


"""
 For backwards compatability with Curator
"""
class ivault_t_search(models.Model):

    class Meta:
        ordering = ['id']
        db_table = "ivault_t_search"

    # This makes the Admin List show
    # a specified string rather than
    # `object_2()`
    def __str__(self):
        return '{}'.format('('+ str(self.id) +') '+ self.fileName )

    fileName = models.CharField(
        max_length=128,
        db_column = 'f_name',
    )

    search_string  = models.CharField(
        max_length=512,
        db_column = 's_string',
        default = 'Empty search string.',
    )

    timestamp  = models.DateTimeField(
        #db_column = 'ts',
        default=timezone.now,
        editable=False,
        null=True
    )

    effectDate = models.DateTimeField(
        #db_column = 'effect_date',
        default=timezone.now,
        editable = 0,
        blank=True,
        null=True
    )

"""
 For backwards compatability with Curator
"""
class ivault_t_options(models.Model):

    class Meta:
        ordering = ['id']
        db_table = "ivault_t_options"

    groupName  = models.CharField(
        max_length=128,
        db_column = 'grp',
    )

    definition = models.CharField(
        max_length=128,
        db_column = 'def1',
    )

    groupSort = models.SmallIntegerField(
        db_column = 'grp_srt',
        blank = 1,
        null = 1,
    )

    # This makes the Admin List show
    # a specified string rather than
    # `object_2()`
    def __str__(self):
        return '{}'.format('('+ str(self.id) +') '+self.option_group+'::'+self.option_text)



"""
 For backwards compatability with Curator
"""
class ivault_t_vals(models.Model):

    class Meta:
        ordering = ['id']
        db_table = "ivault_t_vals"

    # This makes the Admin List show
    # a specified string rather than
    # `object_2()`
    def __str__(self):
        return '{}'.format(self.fileName+'::'+self.option_group+'::'+self.option_text)

    fileName = models.CharField(
        max_length=128,
        db_column = 'f_name',
    )

    optId = models.PositiveIntegerField(
        db_column = 'opt_id',
        blank=True,
        null=True
    )

    selected  = models.CharField(
        max_length=10,
        db_column = 'selected',
        default = 'Empty search string.',
    )

    option_group  = models.CharField(
        max_length=256,
        db_column = 'option_group',
        default = 'Empty search string.',
    )

    option_text  = models.CharField(
        max_length=256,
        db_column = 'option_text',
        default = 'Empty search string.',
    )

    resolution  = models.CharField(
        max_length=100,
        db_column = 'resolution',
        default = 'Empty search string.',
    )

    effectDate = models.DateField(
        db_column = 'effect_date',
        editable = 0,
        default=timezone.now,
        blank=True,
        null=True
    )

class Category(models.Model):

    name  = models.CharField(
        max_length=64,
        db_column = 'name',
        default = 'Needs category name',
    )

    description = models.CharField(
        max_length=128,
        db_column = 'descr',
        null = 1,
    )

    # This makes the Admin List show
    # a specified string rather than
    # `object_2()`
    def __str__(self):
        return '{}'.format(self.name)


class BatchTagHistory(models.Model):

    class Meta:
        ordering = ['timestamp']

     # This makes the Admin List show
     # a specified string rather than
     # `object_2()`
     #def __str__(self):
     #    return '{}'.format(self.fileName)

    assetId = models.PositiveIntegerField(
        null=False
    )

    alteredOptionId = models.PositiveIntegerField(
        null=False
    )

    actionTaken  = models.CharField(
        max_length=64,
    )

    timestamp  = models.DateTimeField(
        db_column = 'ts',
        default=timezone.now,
        editable=False,
    )
