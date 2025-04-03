from django.contrib import admin
from .models import KillRequest, Snapshot

admin.site.register(KillRequest)
admin.site.register(Snapshot)
