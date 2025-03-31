import logging

import psutil

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from monitor.utils import bytes_to_mib

# Get an instance of a logger
logger = logging.getLogger(__name__)


@login_required
def index(request):
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
        if process.info["pid"] == 0:
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
                    "memory": bytes_to_mib(process.info["memory_info"].rss)
                    if process.info["memory_info"]
                    else "N/A",
                }
            )

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return render(request, "monitor/index.html", {"processes": reversed(processes)})
