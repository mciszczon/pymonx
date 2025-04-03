import psutil
from datetime import datetime
from django.utils import timezone
from dacite import from_dict
from django.http import HttpRequest

from monitor.models import ProcessData


def bytes_to_mib(bytes_size: int) -> float:
    return bytes_size / (1024**2)


def time_since(timestamp: float | int, now: datetime = None) -> str:
    if now is None:
        now = timezone.now()

    delta = now - timezone.make_aware(
        datetime.fromtimestamp(timestamp), timezone=timezone.get_fixed_timezone(0)
    )

    days = delta.days
    seconds = delta.seconds
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:  # Always show at least seconds
        parts.append(f"{seconds}s")

    return " ".join(parts)


def filter_process(process: ProcessData, search: str, status: str) -> bool:
    if process.pid == 0:
        return False
    if process.user == "root":
        return False
    if search and (
        not process.name.lower().startswith(search.lower())
        and not str(process.pid).startswith(search.lower())
    ):
        return False
    if status and status.lower() != process.status:
        return False

    return True


def get_processes(search: str, status: str):
    processes: list[ProcessData] = []

    for process in psutil.process_iter(
        [
            "pid",
            "name",
            "username",
            "status",
            "create_time",
            "cpu_percent",
            "memory_info",
        ]
    ):
        process_data = from_dict(
            data_class=ProcessData,
            data={
                "pid": process.info["pid"],
                "name": process.info["name"],
                "user": process.info["username"] or "unknown",
                "status": process.info["status"],
                "start_time": process.info["create_time"],
                "cpu": process.info["cpu_percent"],
                "memory": "{:.2f}".format(bytes_to_mib(process.info["memory_info"].rss))
                if process.info["memory_info"]
                else None,
            },
        )
        if not filter_process(process_data, search, status):
            continue
        try:
            processes.append(process_data)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return processes


SORTING_ALLOWED_FIELDS = ("pid", "name", "status", "cpu", "memory", "start_time")


def parse_sort_param(request: HttpRequest) -> tuple[str, bool]:
    sort_param = request.GET.get("sort", "pid")

    reverse_order = sort_param.startswith("-")
    field = sort_param.lstrip("-")

    if field not in SORTING_ALLOWED_FIELDS:
        field = "pid"
        reverse_order = False

    return field, reverse_order
