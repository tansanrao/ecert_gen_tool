from django.db import models


# Create your models here.
class CsvFile(models.Model):
    id = models.AutoField(primary_key=True)
    filename = models.CharField(max_length=100)
    filepath = models.CharField(max_length=100)
