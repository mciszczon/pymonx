from django.urls import path

from . import views

app_name = "monitor"

urlpatterns = [
    path("", views.index, name="index"),
    path("/kill", views.kill, name="kill"),
    path("/kill_log", views.kill_log, name="kill_log"),
]
