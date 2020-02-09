# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Chores(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    completed =  models.BooleanField(Default=False)
    completed_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)