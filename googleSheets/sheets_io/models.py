from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Log(models.Model):
    from_sheet = models.CharField(max_length=100)
    to_sheet = models.CharField(max_length=100)
    from_tab = models.CharField(max_length=100)
    to_tab = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)
    updated_row = models.CharField(max_length=10)
    updated_col = models.CharField(max_length=10)
    updated_range = models.CharField(max_length=100)

    def __str__(self):
        return "{}!{} -> {}!{}: {}".format(self.from_sheet,self.from_tab,self.to_sheet,self.to_tab,str(self.updated_at))