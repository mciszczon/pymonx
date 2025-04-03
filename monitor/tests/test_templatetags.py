from django.test import TestCase

from monitor.templatetags.monitor_extras import format_memory


class TestFormatMemory(TestCase):
    def test_bytes_to_mib_rounding(self):
        cases = [
            (0, "0.00"),  # Zero bytes
            (1024 * 1024, "1.00"),  # Exactly 1 MiB
            # 1.23456 MiB should round to "1.23"
            (int(1.23456 * 1024 * 1024), "1.23"),
            # 1.236 MiB should round up to "1.24"
            (int(1.236 * 1024 * 1024), "1.24"),
            # Borderline cases with banker's rounding:
            # Python's format rounds half to even.
            # 1.235 MiB: 1.235 rounds to "1.23" because 1.23 is even.
            (int(1.235 * 1024 * 1024), "1.23"),
            # 1.225 MiB: rounds to "1.22" (banker's rounding, 1.22 is even).
            (int(1.225 * 1024 * 1024), "1.22"),
            # 1.226 MiB: should round to "1.23"
            (int(1.226 * 1024 * 1024), "1.23"),
        ]

        for bytes_value, expected in cases:
            with self.subTest(bytes=bytes_value):
                result = format_memory(bytes_value)
                self.assertEqual(
                    result,
                    expected,
                    msg=f"Expected {expected} for {bytes_value} bytes, got {result}",
                )
