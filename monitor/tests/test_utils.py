from datetime import datetime, timedelta

from django.test import TestCase
from freezegun import freeze_time

from monitor.models import ProcessData
from monitor.utils import time_since, filter_process


class TestTimeSince(TestCase):
    @freeze_time("2025-04-01 12:00:00")
    def test_time_since(self):
        minute_ago = datetime.now() - timedelta(minutes=1)
        result = time_since(minute_ago.timestamp())
        self.assertEqual(result, "1m")

        six_hours_ago = datetime.now() - timedelta(hours=6, minutes=12, seconds=4)
        result = time_since(six_hours_ago.timestamp())
        self.assertEqual(result, "6h 12m 4s")

        now = datetime.now()
        result = time_since(now.timestamp())
        self.assertEqual(result, "0s")

        seven_days_ago = datetime.now() - timedelta(days=7, seconds=4)
        result = time_since(seven_days_ago.timestamp())
        self.assertEqual(result, "7d 4s")

        years_ago = datetime.now() - timedelta(days=641)
        result = time_since(years_ago.timestamp())
        self.assertEqual(result, "641d")


class TestFilterProcess(TestCase):
    def test_pid_0(self):
        process = ProcessData(
            pid=0,
            name="Test",
            user="test",
            status="running",
            start_time=0,
            cpu=None,
            memory=None,
        )
        self.assertFalse(filter_process(process, "", ""))

    def test_root(self):
        process = ProcessData(
            pid=1,
            name="Test",
            user="root",
            status="running",
            start_time=0,
            cpu=None,
            memory=None,
        )
        self.assertFalse(filter_process(process, "", ""))

    def test_search(self):
        process = ProcessData(
            pid=1,
            name="Test",
            user="test",
            status="running",
            start_time=0,
            cpu=None,
            memory=None,
        )
        self.assertTrue(filter_process(process, "test", ""))
        self.assertTrue(filter_process(process, "Test", ""))
        self.assertTrue(filter_process(process, "1", ""))
        self.assertFalse(filter_process(process, "test1", ""))

    def test_status(self):
        process = ProcessData(
            pid=1,
            name="Test",
            user="test",
            status="running",
            start_time=0,
            cpu=None,
            memory=None,
        )
        self.assertTrue(filter_process(process, "", "running"))
        self.assertFalse(filter_process(process, "", "sleeping"))

    def test_search_and_status(self):
        process = ProcessData(
            pid=1,
            name="Test",
            user="test",
            status="running",
            start_time=0,
            cpu=None,
            memory=None,
        )
        self.assertTrue(filter_process(process, "test", "running"))
        self.assertFalse(filter_process(process, "test", "sleeping"))
