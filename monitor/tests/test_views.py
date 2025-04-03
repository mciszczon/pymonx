from dataclasses import asdict

import psutil
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from django.utils import timezone

from monitor.models import ProcessData, Snapshot


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


class TestSnapshotView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            username="testuser", password="password"
        )

    def test_view_snapshots(self):
        self.client.force_login(self.user)
        Snapshot.objects.create(
            user=self.user, data=[{}], cpu_usage=56.5, memory_usage=67.95
        )
        response = self.client.get(reverse("monitor:snapshot_list"))
        self.assertEqual(response.status_code, 200)

    @patch("monitor.views.get_processes")
    def test_make_snapshot(self, mock_get_processes):
        mock_get_processes.return_value = [
            ProcessData(
                pid=1,
                name="systemd",
                user="linus",
                status="running",
                start_time=timezone.now(),
                cpu=15.2,
                memory=1024,
            ),
            ProcessData(
                pid=2,
                name="shell",
                user="linus",
                status="running",
                start_time=timezone.now(),
                cpu=4.2,
                memory=5723651259,
            ),
        ]
        self.client.force_login(self.user)
        response = self.client.post(reverse("monitor:snapshot"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snapshot.objects.count(), 1)
        snapshot = Snapshot.objects.first()
        self.assertEqual(snapshot.data[0]["pid"], 1)
        self.assertEqual(snapshot.data[0]["name"], "systemd")
        self.assertEqual(snapshot.data[1]["pid"], 2)
        self.assertEqual(snapshot.data[1]["name"], "shell")

    def test_view_snapshot_detail(self):
        self.client.force_login(self.user)
        snapshot = Snapshot.objects.create(
            user=self.user,
            data=[
                asdict(
                    ProcessData(
                        pid=1,
                        name="systemd",
                        user="root",
                        status="running",
                        start_time=timezone.now(),
                        cpu=4.2,
                        memory=5723651259,
                    )
                )
            ],
            cpu_usage=26.4,
            memory_usage=67.9,
        )
        response = self.client.get(
            reverse("monitor:snapshot_detail", args=[snapshot.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_export_snapshot(self):
        self.client.force_login(self.user)
        snapshot = Snapshot.objects.create(
            user=self.user,
            data=[
                asdict(
                    ProcessData(
                        pid=1,
                        name="systemd",
                        user="root",
                        status="running",
                        start_time=timezone.now(),
                        cpu=4.2,
                        memory=5723651259,
                    )
                )
            ],
            cpu_usage=26.4,
            memory_usage=67.9,
        )
        response = self.client.get(
            reverse("monitor:snapshot_export", args=[snapshot.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
