from django.db import models

class Chore(models.Model):
    name = models.CharField(max_length=256)
    assignee = models.IntegerField()
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
