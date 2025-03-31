from django.contrib.auth.views import LoginView, LogoutView
from django.urls.base import reverse_lazy


class Login(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True
    next_page = reverse_lazy("monitor:index")


class Logout(LogoutView):
    http_method_names = ["post", "get", "options"]
    next_page = reverse_lazy("landing:index")

    def get(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
