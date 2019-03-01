from django.db import models

# Create your models here.

class Log(models.Model):
    log = models.CharField(max_length=100000)
    agent_name = models.CharField(max_length=100, blank=True)
    user_key = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.log