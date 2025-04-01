import psutil
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class TestIndexView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            username="testuser", password="password"
        )

    def test_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("monitor:index"))
        self.assertEqual(response.status_code, 200)


class TestKillView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            username="testuser", password="password"
        )

    def test_view_invalid_pid(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("monitor:kill"), {"pid": -1})
        self.assertEqual(response.status_code, 500)

    def test_view(self):
        process = psutil.Popen(["python", "-c", "while True: pass"])

        self.client.force_login(self.user)
        response = self.client.post(reverse("monitor:kill"), {"pid": process.pid})
        self.assertEqual(response.status_code, 200)
        ps_process = psutil.Process(process.pid)
        self.assertEqual(ps_process.status(), "zombie")


class TestKillLogView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            username="testuser", password="password"
        )

    def test_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("monitor:kill_log"))
        self.assertEqual(response.status_code, 200)
