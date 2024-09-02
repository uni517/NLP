from django.db import models


class personality(models.Model):
    en_persona = models.CharField(max_length=100, null=False)
    num_persona = models.CharField(max_length=100, null=False)