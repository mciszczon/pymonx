from dataclasses import dataclass

from django.conf import settings
from django.db import models


@dataclass(frozen=True)
class ProcessData:
    pid: int
    name: str
    user: str
    status: str
    start_time: float
    cpu: float | None
    memory: str | None


class KillRequest(models.Model):
    pid = models.IntegerField()
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
