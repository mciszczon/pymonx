from django.urls import path

from . import views

app_name = "landing"

urlpatterns = [
    path("", views.Login.as_view(), name="index"),
    path("logout/", views.Logout.as_view(), name="logout"),
]
