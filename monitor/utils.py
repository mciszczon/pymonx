import psutil
from datetime import datetime


def bytes_to_mib(bytes_size: int) -> float:
    return bytes_size / (1024**2)


def time_since(timestamp: int) -> str:
    now = datetime.now()
    delta = now - datetime.fromtimestamp(timestamp)

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


def filter_process(process: psutil.Process, search: str, status: str) -> bool:
    if process.info["pid"] == 0:
        return False
    if process.info["username"] == "root":
        return False
    if search:
        search = search.lower()
        if not process.info["name"].lower().startswith(search) and not str(
            process.info["pid"]
        ).startswith(search):
            return False
    if status:
        status = status.lower()
        if status != process.info["status"]:
            return False

    return True


def get_processes(search: str, status: str):
    processes = []

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
        if not filter_process(process, search, status):
            continue
        try:
            processes.append(
                {
                    "pid": process.info["pid"],
                    "name": process.info["name"],
                    "user": process.info["username"] or "unknown",
                    "status": process.info["status"],
                    "start_time": process.info["create_time"],
                    "cpu": process.info["cpu_percent"],
                    "memory": "{:.2f}".format(
                        bytes_to_mib(process.info["memory_info"].rss)
                    )
                    if process.info["memory_info"]
                    else None,
                }
            )

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return processes
