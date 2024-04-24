from django.db import models
from django.utils import timezone
from core.models  import Option as CoreOption
date_time = models.DateTimeField(auto_now_add=True)
# https://pypi.org/project/django-admin-searchable-dropdown/

class FilterGroupItem(models.Model):

    Name  = models.CharField(
        max_length=128,
        db_column = 'name',
    )

    Description = models.CharField(
        max_length=128,
        db_column = 'descr',
        null=True, 
        blank=True,
    )

    Sort = models.SmallIntegerField(
        db_column = 'sort',
        default = 0,
    )
    
    # The group this item belongs in
    parentGroup = models.ForeignKey('FilterGroup', null=True, blank=True, on_delete=models.PROTECT)
    
    # The original option item from the iVault core
    coreOption = models.ForeignKey(CoreOption, on_delete=models.PROTECT)
    #CoreOptions = models.ManyToManyField(CoreOption)

    # This makes the Admin List show
    # a specified string rather than
    # `object_2()`
    def __str__(self):
        return '{}'.format('('+ str(self.id) +') '+self.Name + ':' + self.Description)

    def as_json(self):
        return dict(
            id = self.id, 
            name = self.Name, 
            parentGroup = self.parentGroup, 
            coreOption = self.coreOption, 
            description = self.Description, 
            sort = self.Sort
            )

class FilterGroup(models.Model):

    Name  = models.CharField(
        max_length=128,
        db_column = 'name',
    )

    Description = models.CharField(
        max_length=128,
        db_column = 'descr',
        null=True, 
        blank=True,
    )

    Sort = models.SmallIntegerField(
        db_column = 'sort',
        default = 0,
    )

    selectionElement = models.CharField(
        max_length=32,
        default="checkbox"
    )

    #filterGroupItems = models.ManyToManyField(FilterGroupItem)

    parentFilter = models.ForeignKey('Filter', null=True, blank=True, on_delete=models.PROTECT)

    # This makes the Admin List show
    # a specified string rather than
    # `object_2()`
    def __str__(self):
        return '{}'.format('('+ str(self.id) +') '+self.Name + ':' + self.Description)

    def as_json(self):
        return dict(
            id=self.id, 
            name=self.Name, 
            parentFilter=self.parentFilter, 
            description=self.Description, 
            sort=self.Sort)



class Filter(models.Model):

    Name  = models.CharField(
        max_length=128,
        db_column = 'name',
    )

    mach_name  = models.CharField(
        max_length=128,
        db_column = 'mach_name',
    )

    LocationPath  = models.CharField(
        max_length=256,
        db_column = 'loc_path',
    )

    Description = models.CharField(
        max_length=128,
        db_column = 'descr',
        null=True, 
        blank=True,
    )

    Sort = models.SmallIntegerField(
        db_column = 'sort',
        default = 0,
    )

    Enabled = models.BooleanField(
        db_column = 'enabled',
        default=True
    )

   # timestamp  = models.DateTimeField(
   #     db_column = 'timestamp',
   #     #default=timezone.now,
   #     default=date_time,
   #     editable=False,
   # )

    #filterGroups = models.ManyToManyField(FilterGroup)

    #location = models.ForeignKey(Location, on_delete=models.CASCADE)

    # This makes the Admin List show
    # a specified string rather than
    # `object_2()`
    def __str__(self):
        return '{}'.format('('+ str(self.id) +') '+self.Name + ':' + self.Description)

    def as_json(self):
        return dict(
            id=self.id, 
            name=self.Name, 
            #filterGroups=self.filterGroups,
            locationPath=self.LocationPath,
            description=self.Description,
            enabled=self.Enabled,
            sort=self.Sort,
        )
