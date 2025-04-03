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
    cpu: float | None  # percentage value as float, i.e. 0.0–100.0
    memory: str | None  # FIXME: Change to int and store in bytes


class KillRequest(models.Model):
    pid = models.IntegerField()
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)

    def __str__(self):
        return f"{'✅' if self.success else '❌'} {self.name} (PID: {self.pid}) by {self.user} on {self.created_at.strftime('%Y-%m-%d at %H:%M:%S')}"


class Snapshot(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    data = models.JSONField(default=list)  # List of ProcessData-interface dicts
    cpu_usage = models.FloatField()  # Percentage value of total CPU usage
    memory_usage = models.FloatField()  # Percentage value of total memory usage

    def __str__(self):
        return f"by {self.user} on {self.created_at.strftime('%Y-%m-%d at %H:%M:%S')}"
