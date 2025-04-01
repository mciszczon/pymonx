from django.conf import settings
from django.db import models


class KillRequest(models.Model):
    pid = models.IntegerField()
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
