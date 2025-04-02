from django.urls import path

from . import views

app_name = "monitor"

urlpatterns = [
    path("", views.index, name="index"),
    path("kill_log", views.kill_log, name="kill_log"),
    path("kill_log/kill", views.kill, name="kill"),
    path("snapshots", views.snapshot_list, name="snapshot_list"),
    path("snapshots/create", views.snapshot, name="snapshot"),
    path("snapshots/<int:pk>", views.snapshot_detail, name="snapshot_detail"),
    path("snapshots/<int:pk>/export", views.export_snapshot, name="snapshot_export"),
]
